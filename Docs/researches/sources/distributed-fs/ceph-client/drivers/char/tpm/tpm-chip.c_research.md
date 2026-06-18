<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-chip.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-chip.c

## Purpose
Owns TPM chip allocation, lifecycle, device numbers, class devices, locality/ops locking, bootstrap, hwrng registration, event-log setup, and char-device registration.

## Important APIs, Types, And Functions
Exports `tpm_chip_start()`, `tpm_chip_stop()`, `tpm_try_get_ops()`, `tpm_put_ops()`, `tpm_default_chip()`, `tpm_chip_alloc()`, `tpmm_chip_alloc()`, `tpm_chip_bootstrap()`, `tpm_chip_register()`, and `tpm_chip_unregister()`. It defines `tpm_class`, `tpmrm_class`, `tpm_devt`, `dev_nums_idr`, and helper flows for hwrng and legacy sysfs links.

## Control Flow
Allocation assigns an IDR device number, initializes the class device and cdev, allocates TPM2 workspace buffers, and sets locality invalid. `tpm_try_get_ops()` takes a device reference, read-locks `ops_sem`, locks `tpm_mutex`, refuses suspended/disabled chips, starts locality/clock/cmd-ready, and returns with the chip ready for I/O. Registration bootstraps the chip, attaches sysfs groups, firmware logs, PPI, hwrng, primary and resource-manager char devices, then publishes the chip in the IDR.

## State And Persistence
Persistent chip state includes device number, class devices, ops pointer, flags, locality, TPM2 work space, hwrng registration, event-log dentries, sysfs groups, and IDR publication. Shutdown/unregister set `chip->ops = NULL` under write lock to block future operations.

## Dependencies And Integration Points
Central integration point for all transport drivers. It calls TPM1/TPM2 startup, PCR allocation, TPM2 shutdown, TPM2 auth-session teardown, eventlog, PPI, sysfs, hwrng, char devices, and resource-manager helpers.

## Risks And Edge Cases
Ops locking and device references are lifetime-critical during unregister. Shutdown may be called twice and guards against null ops. Hwrng must stay disabled for firmware-upgrade chips and AMD CRB quirked devices. Legacy sysfs symlink cleanup must match additions.

## Test Signals
Probe/remove stress, open file descriptors during unregister, suspend/resume races, TPM2 shutdown on reboot, default chip lookup, hwrng registration failures, firmware-upgrade mode, and resource-manager device creation/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-chip.c -->
