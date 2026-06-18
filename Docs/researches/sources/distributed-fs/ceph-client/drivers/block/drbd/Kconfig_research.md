# sources/distributed-fs/ceph-client/drivers/block/drbd/Kconfig

## Purpose

This Kconfig file defines configuration for the DRBD replicated block device driver and its fault-injection option. It gates DRBD on procfs and networking support, selects required helper libraries, and documents the driver as a network RAID-1 style replicated block device for high-availability clusters.

## Important Options

- `BLK_DEV_DRBD`: tristate option for DRBD support. It depends on `PROC_FS && INET`, selects `LRU_CACHE` and `CRC32`, and can be built in, modular, or disabled.
- `DRBD_FAULT_INJECTION`: boolean option depending on `BLK_DEV_DRBD`. It enables sysfs/module-parameter driven simulated faults for metadata I/O, data I/O, bitmap allocation, peer request allocation, and receive-side corruption.
- A comment explains that DRBD is disabled when `PROC_FS` or `INET` is not selected.

## Control Flow and Integration

Kconfig has no runtime control flow, but it shapes compilation:

- `BLK_DEV_DRBD=m/y` causes the Makefile to build `drbd.o`.
- Selecting `LRU_CACHE` is required by the activity log and resync extent caches.
- Selecting `CRC32` supports checksum paths used by DRBD metadata/activity-log code.
- Optional fault injection compiles hooks used by DRBD paths such as metadata I/O, bitmap allocation, and request allocation.

## State and Persistence Behavior

The file does not store runtime state. Its choices affect whether DRBD code exists in the kernel and whether fault injection parameters exist at runtime.

## Dependencies

- `PROC_FS`: required for DRBD proc integration.
- `INET`: required because DRBD replication uses networking.
- `LRU_CACHE` and `CRC32`: selected helper functionality.
- The help text notes that authentication additionally requires `CRYPTO_HMAC` and a hash function, but those are not hard dependencies in this option.

## Risks and Edge Cases

- Authentication support is documented but not selected automatically; a configuration can enable DRBD without the crypto options needed for authenticated connections.
- The disabled comment only appears for missing `PROC_FS` or `INET`; users may still need other runtime tooling and cluster management outside kernel config.
- Fault injection is powerful and can simulate corruption; it must remain test-only.

## Test Signals

- Kconfig dependency tests with `PROC_FS=n`, `INET=n`, and both enabled.
- Build DRBD built-in and module configurations.
- Build with and without `DRBD_FAULT_INJECTION` and verify sysfs/module fault controls appear only when enabled.
