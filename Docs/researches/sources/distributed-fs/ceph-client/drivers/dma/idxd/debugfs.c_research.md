# sources/distributed-fs/ceph-client/drivers/dma/idxd/debugfs.c

## Purpose
`debugfs.c` adds IDXD debugfs support, mainly an event-log dump for devices with EVL support.

## Important APIs, Types, And Functions
Key functions are `idxd_init_debugfs()`, `idxd_remove_debugfs()`, `idxd_device_init_debugfs()`, `idxd_device_remove_debugfs()`, `debugfs_evl_show()`, and `dump_event_entry()`.

## Control Flow
Global init creates the `idxd` debugfs directory when debugfs is available. Per-device init creates a device directory and optional `event_log` file. Reads lock the EVL, read head/tail from hardware, walk ring entries, and print decoded plus raw fields.

## State And Persistence Behavior
Debugfs dentries are stored on `idxd_device`; EVL memory is owned elsewhere and read under `evl->lock`.

## Dependencies And Integration Points
It depends on debugfs, seq_file, IDXD registers/uapi layouts, and EVL setup in `device.c`.

## Risks And Test Signals
Pointer arithmetic assumes EVL entry size matches hardware caps. Test file presence only for EVL-capable devices, readable dumps under load, and clean recursive removal.
