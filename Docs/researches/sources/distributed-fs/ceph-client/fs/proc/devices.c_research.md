# sources/distributed-fs/ceph-client/fs/proc/devices.c

Purpose: Implements `/proc/devices`, listing registered character and, when block support is enabled, block device majors.

Important APIs and types: Uses `chrdev_show()`, `blkdev_show()`, `CHRDEV_MAJOR_MAX`, `BLKDEV_MAJOR_MAX`, seq operations, `proc_create_seq()`, and `pde_make_permanent()`.

Control flow: The seq iterator uses the file position as a major-number index. `devinfo_show()` prints a character-device header at index zero, calls `chrdev_show()` for character majors, then prints a block-device header and calls `blkdev_show()` for block majors after offsetting past character majors. Iteration stops after the combined major range.

State and persistence: No state is stored here; reads reflect current registered device majors maintained by char/block device subsystems.

Dependencies and integration points: Integrates with procfs seq files, char device registration, optional block device registration, and permanent proc entry handling.

Risks: Off-by-one errors in position handling could omit major zero headers or overrun the valid range. Output format is traditional and consumed by scripts. With `CONFIG_BLOCK` disabled, the combined range still includes `BLKDEV_MAJOR_MAX` in the iterator condition even though only character output is produced for the first range.

Test signals: Register/unregister char and block majors, read while registrations change, build with and without `CONFIG_BLOCK`, and verify header placement and termination.
