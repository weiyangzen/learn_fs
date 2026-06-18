# sources/distributed-fs/ceph-client/net/atm/resources.c

## Purpose
`resources.c` manages registered ATM devices and device-level ioctl operations. It owns the global device list, registration/deregistration, device lookup, stats copying/zeroing, name enumeration, and procfs seq helpers.

## Important APIs and Functions
- Global state: `LIST_HEAD(atm_devs)` and `DEFINE_MUTEX(atm_dev_mutex)`.
- `atm_dev_lookup`: locked lookup by device number with refcount hold.
- `atm_dev_register`: allocates and initializes `struct atm_dev`, assigns a number, registers procfs/sysfs, and appends to `atm_devs`.
- `atm_dev_deregister`: marks removed, unlinks, releases VCCs, unregisters sysfs/procfs, and drops the registration reference.
- `atm_getnames`: implements `ATM_GETNAMES` by copying device numbers to userspace.
- `atm_dev_ioctl`: central device ioctl dispatcher for type/ESI/stats/address/loop/range/SONET and driver-specific commands.
- `atm_dev_seq_start`, `atm_dev_seq_next`, `atm_dev_seq_stop`: procfs device-list traversal under `CONFIG_PROC_FS`.

## Control Flow
Registration allocates a device with defaults (`ATM_PHY_SIG_UNKNOWN`, OC3 link rate, initialized address lists), then under `atm_dev_mutex` resolves its number, installs ops/flags/stats/refcount, registers proc and sysfs, and links the device. Deregistration sets `ATM_DF_REMOVED`, removes the list entry, releases active VCCs through `atm_dev_release_vccs`, and tears down sysfs/procfs. Ioctls first fetch the user-supplied buffer length, lookup/autoload the target device, handle core commands inline, and fall through to driver `ioctl`/`compat_ioctl` for device-specific or SONET commands.

## State and Persistence
The persistent state is the global registered device list, per-device stats, ESI, address lists, flags, link rate, proc/sysfs bindings, and device refcounts. Stats-zeroing is implemented by copying current atomics and subtracting them after a successful userspace copy.

## Dependencies and Integration
Integrates with `addr.h` address helpers, procfs hooks from `proc.c`, sysfs helpers declared in `resources.h`, device module autoloading via `try_then_request_module`, and common VCC cleanup via `atm_dev_release_vccs`.

## Risks and Test Signals
Risks include device number races, registration rollback after proc/sysfs failures, user-buffer length mistakes, admin capability enforcement, compat driver ioctl handling, and stats subtraction under concurrent updates. Test signals include registering duplicate and auto-numbered devices, `ATM_GETNAMES`, ESI set/get permission paths, address add/delete/get, stats get/zero, deregistration with open VCCs, and proc/sysfs cleanup.
