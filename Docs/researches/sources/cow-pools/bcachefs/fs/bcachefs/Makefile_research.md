# File Research: sources/cow-pools/bcachefs/fs/bcachefs/Makefile

This is the kbuild file for the bcachefs module/object.

When `CONFIG_BCACHEFS_FS` is enabled, `bcachefs.o` is built. `bcachefs-y` enumerates the module’s object files. The files in this research group are part of the allocation subsystem entries near the top:
- `alloc/accounting.o`
- `alloc/background.o`
- `alloc/backpointers.o`
- `alloc/buckets.o`
- `alloc/check.o`

The Makefile then lists the broader implementation: allocation helpers, btree code, data/checksum/compression/copygc/erasure coding, filesystem operations, initialization/recovery, journal code, superblock handling, snapshots, utilities, vendor support, and VFS integration.

Conditional additions:
- `debug/async_objs.o` is included when `CONFIG_DEBUG_FS` is enabled.
- `util/mean_and_variance_test.o` is included for `CONFIG_MEAN_AND_VARIANCE_UNIT_TEST`, except in DKMS builds.
- `module-version.o` is added for DKMS builds.

It also disables noisy `psabi` compiler warnings and explicitly adds `-I$(src)` because kbuild sometimes does not pass the source include path consistently. The Makefile establishes that the allocation/accounting files are core bcachefs objects, not optional side modules.
