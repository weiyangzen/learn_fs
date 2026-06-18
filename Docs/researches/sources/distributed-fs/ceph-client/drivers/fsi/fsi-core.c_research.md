<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-core.c -->
# sources/distributed-fs/ceph-client/drivers/fsi/fsi-core.c

## Purpose
`fsi-core.c` implements the Linux FSI bus core. It registers the FSI bus and master class, exposes endpoint read/write helpers, discovers CFAM slaves and engines, manages slave character devices, allocates minors for FSI client cdevs, handles bus error recovery, and provides master/driver registration APIs.

## Important APIs, types, and functions
Exported APIs include `fsi_device_read()`, `fsi_device_write()`, `fsi_device_peek()`, `fsi_slave_read()`, `fsi_slave_write()`, `fsi_slave_claim_range()`, `fsi_slave_release_range()`, `fsi_get_new_minor()`, `fsi_free_minor()`, `fsi_master_rescan()`, `fsi_master_register()`, `fsi_master_unregister()`, `fsi_driver_register()`, and `fsi_driver_unregister()`. Core internal flows include `fsi_slave_init()`, `fsi_slave_scan()`, `fsi_slave_handle_error()`, `fsi_master_scan()`, and CFAM cdev operations `cfam_read()`/`cfam_write()`.

## Control flow
Postcore init allocates a character-device major, registers the FSI bus, and registers the FSI master class. A hardware master calls `fsi_master_register()`, receives an ID, registers its master device, and unless `no-scan-on-init` is set, scans each link. Scanning enables a link, sends a break, reads CFAM ID zero, validates CRC4, creates a slave device, configures async mode if the master software-clocks the bus, forces LBUS ownership, programs SMODE, allocates a CFAM minor/cdev, applies link delay config, creates a legacy raw sysfs file, and scans the engine table. Engine-table entries with valid CRC, type, and slots become `struct fsi_device` children matched to FSI client drivers.

Bus access enters through `fsi_device_read/write()` or CFAM/raw file ops, validates bounds and alignment, calls `fsi_slave_read/write()`, encodes 23-bit addresses through slave ID when needed, and retries after `fsi_slave_handle_error()`. Error handling first reports/clears slave status, then optionally sends TERM and probes communication, and finally sends BREAK, restores delays, reprograms SMODE, and calls the master's `link_config`. Master rescan unscans all child slaves/devices under `scan_lock` before scanning again.

## State and persistence behavior
Global runtime state includes `master_ida`, `fsi_minor_ida`, `fsi_base_dev`, and the `discard_errors` module parameter. Each master owns scan state and link callbacks; each slave stores CFAM ID, chip ID, link/id, size, cdev/minor, send/echo delays, OF node, and parent master. No durable persistence exists, but minor numbering preserves legacy ABI where possible and OF aliases can force stable client numbering.

## Dependencies and integration points
The file depends on CRC4, device/bus/class core, IDA allocation, OF matching/address data, cdev/fs/uaccess, tracepoints, `fsi-master.h`, and `fsi-slave.h`. It integrates upward with FSI client drivers through `struct fsi_driver` and downward with hardware-specific masters through `struct fsi_master` callbacks.

## Risks and edge cases
Important risks include 23-bit address encoding only working for slave ID zero, engine-table CRC/slot parsing errors, userspace ABI differences under `CONFIG_FSI_NEW_DEV_NODE`, retry/error recovery loops that can hide persistent bus faults, and lifetime rules where `fsi_master_register()` takes ownership of `master->dev`. `fsi_slave_claim_range()` currently does not check overlaps, so hub address reservations are advisory.

## Test signals
Signals include bus/master class registration, master scan with valid/invalid CFAM CRC, engine discovery and OF node matching, CFAM char-device reads/writes with unaligned offsets, raw sysfs access sizing, TERM/BREAK recovery paths, minor allocation with legacy and alias numbering, driver match/probe/remove, and rescan/unregister cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-core.c -->
