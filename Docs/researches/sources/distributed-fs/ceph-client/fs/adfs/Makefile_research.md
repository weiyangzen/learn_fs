<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/adfs/Makefile

## Purpose
This Makefile builds the ADFS filesystem object from its directory, file, inode, map, and superblock implementation files.

## Important APIs, types, and functions
It builds `adfs.o` for `CONFIG_ADFS_FS` from `dir.o`, `dir_f.o`, `dir_fplus.o`, `file.o`, `inode.o`, `map.o`, and `super.o`.

## Control flow
Kbuild links all listed objects into the ADFS module or built-in object when configured.

## State and persistence
No runtime state; it defines build composition.

## Dependencies and integration points
It maps the ADFS Kconfig symbol to the implementation files declared through `adfs.h`.

## Risks and test signals
Risks include stale object list entries and missing format-specific directory code. Test signals are module/built-in ADFS builds with read-only and RW configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/Makefile -->
