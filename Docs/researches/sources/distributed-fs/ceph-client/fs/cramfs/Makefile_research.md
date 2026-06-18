# sources/distributed-fs/ceph-client/fs/cramfs/Makefile

Purpose: defines the Cramfs composite object build.

Important entries: `obj-$(CONFIG_CRAMFS) += cramfs.o` and `cramfs-objs := inode.o uncompress.o`.

Control flow: no runtime flow. Kbuild links VFS/mount/read logic with zlib wrapper logic when Cramfs is enabled.

State and persistence: no state.

Dependencies/integration: pairs with Kconfig's `ZLIB_INFLATE` selection. The split confirms that the main filesystem implementation and decompressor wrapper are compiled together into the module/built-in object.

Risks: omitting `uncompress.o` would break compressed block reads; omitting `inode.o` would register nothing. Conditional backend code is handled by C preprocessor symbols in `inode.c`, not by Makefile object selection.

Test signals: compile Cramfs as built-in and module, run modpost for zlib symbols, and mount sample images.
