# sources/distributed-fs/ceph-client/fs/exfat/Makefile

## Purpose
The exFAT `Makefile` maps `CONFIG_EXFAT_FS` to the `exfat.o` composite object and lists the implementation translation units that form the filesystem driver.

## Important APIs, types, and functions
The only build targets are `obj-$(CONFIG_EXFAT_FS) += exfat.o` and `exfat-y := inode.o namei.o dir.o super.o fatent.o cache.o nls.o misc.o file.o balloc.o`. This expresses the driver layering: superblock/mount, inode/address-space, namespace operations, directory entries, FAT and bitmap allocation, cluster cache, NLS conversion, miscellaneous checksums/time/errors, and file operations.

## Control flow
There is no runtime control flow. Kbuild compiles the listed objects and links them into `exfat.o`; that composite is linked built-in or as `exfat.ko` depending on `EXFAT_FS`.

## State and persistence behavior
The file persists the compile-time module composition. Adding, removing, or reordering objects affects symbol availability and module init/exit linkage, but does not store filesystem runtime state.

## Dependencies and integration points
The Makefile integrates with the kernel build system and the `Kconfig` option in the same directory. It expects `super.o` to provide module registration and uses the other objects for the file and inode operation tables exported through headers.

## Risks and test signals
Risks include omitting a source object that defines referenced symbols, adding duplicate definitions, or failing modular build linkage. Test signals are `CONFIG_EXFAT_FS=m` and `=y` builds, `modpost` symbol checks, and boot/module-load smoke tests that mount an exFAT image.
