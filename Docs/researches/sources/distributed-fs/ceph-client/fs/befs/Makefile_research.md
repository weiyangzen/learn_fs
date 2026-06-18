# sources/distributed-fs/ceph-client/fs/befs/Makefile

Purpose: declares how the BeFS driver object is built from its component files.

Important APIs/types/functions: `obj-$(CONFIG_BEFS_FS) += befs.o`, `ccflags-$(CONFIG_BEFS_DEBUG) += -DDEBUG`, and `befs-objs := datastream.o btree.o super.o inode.o debug.o io.o linuxvfs.o`.

Control flow: when BeFS is enabled, Kbuild links all listed objects into `befs.o`; debug builds add a compile define used by local debug code.

State and persistence: build metadata only.

Dependencies and integration: reflects the subsystem layering: VFS mount/inode code, superblock parsing, inode validation, datastream and B+tree readers, block I/O, and debug helpers.

Risks: omitting a component breaks exported internal symbols; stale debug flags can leave debug paths compiled differently than Kconfig implies.

Test signals: compile BeFS built-in and module, with and without `CONFIG_BEFS_DEBUG`.
