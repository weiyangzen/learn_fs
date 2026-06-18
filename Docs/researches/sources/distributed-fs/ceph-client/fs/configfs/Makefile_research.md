# sources/distributed-fs/ceph-client/fs/configfs/Makefile

Purpose: defines how the configfs filesystem is built.

Important entries: `obj-$(CONFIG_CONFIGFS_FS) += configfs.o` builds the composite object when enabled. `configfs-objs` lists `inode.o`, `file.o`, `dir.o`, `symlink.o`, `mount.o`, and `item.o`.

Control flow: no runtime logic. Kbuild links the listed objects into `configfs.o` for built-in or modular use.

State and persistence: no state.

Dependencies/integration: connects the Kconfig option to the implementation files. The object composition shows the subsystem boundaries: mount/superblock setup, item lifetime helpers, inode metadata, directory operations, attribute file operations, and symlink operations.

Risks: missing an object can create unresolved exports or a filesystem that registers without core operations. Order is conventional but symbol resolution is handled by kbuild.

Test signals: build `CONFIG_CONFIGFS_FS=y`, `m`, and `n`; check exported symbols for configfs users; and run mount/register subsystem smoke tests in both module and built-in configurations.
