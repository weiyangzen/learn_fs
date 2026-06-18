# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_ctl_drv.c

## Purpose
This file implements the `intel_qat` base module entry/exit and the `/dev/qat_adf_ctl` character device used to configure, start, stop, and query QAT devices. It also initializes global workqueues/AER and registers QAT crypto/compression services.

## Important APIs, Types, And Functions
Important functions include `adf_chr_drv_create()`, `adf_chr_drv_destroy()`, `adf_ctl_ioctl()`, ioctl handlers for config/stop/start/status/device-count, `adf_copy_key_value_data()`, `adf_ctl_stop_devices()`, `adf_register_ctl_device_driver()`, and `adf_unregister_ctl_device_driver()`. `struct adf_ctl_drv_info` holds char-device major/cdev state.

## Control Flow
Module init creates the char device/class, initializes misc/AER/PF/VF workqueues, registers crypto and compression services, and unwinds in reverse on failure. Ioctl dispatch is serialized by `adf_ctl_lock`. Config ioctl copies user-linked sections/keys into kernel config if the device is stopped. Stop verifies IDs and busy/reset state, stops VFs first, then PFs/all matching devices. Start calls `adf_dev_up(accel_dev, false)`. Status copies hardware counts, state, device type, instance, and BDF to user space.

## State And Persistence Behavior
Global runtime state includes the char-device major/cdev and class. Device config written by ioctl is volatile in `accel_dev->cfg`. Crypto/compression registration persists until module unload.

## Dependencies And Integration Points
It depends on Linux char device/uaccess/mutex, QAT config/user structs, device manager, common lifecycle, workqueues, AER, PF/VF code, and algorithm registration.

## Risks
User-pointer traversal must be bounded and rollback on error. Stop/start races are guarded by `adf_ctl_lock` and device busy checks, but external users can still hold references. Module init unwind must mirror registration order. Device status ABI must remain stable.

## Test Signals
`/dev/qat_adf_ctl` creation, compat ioctl tests, config copy/rollback, start/stop all devices with VFs, busy-device rejection, status/device-count output, algorithm registration/unregistration, and module load/unload cleanup.
