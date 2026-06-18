## sources/distributed-fs/ceph-client/fs/overlayfs/Makefile

Purpose: this Makefile wires the overlayfs module into the kernel build and lists the object files that compose `overlay.o`.

Important APIs and targets: `obj-$(CONFIG_OVERLAY_FS) += overlay.o` builds overlayfs when configured. `overlay-objs` includes `super.o`, `namei.o`, `util.o`, `inode.o`, `file.o`, `dir.o`, `readdir.o`, `copy_up.o`, `export.o`, `params.o`, and `xattrs.o`.

Control flow: there is no runtime control flow. Build control is conditional on `CONFIG_OVERLAY_FS`, and all listed objects are linked into one module/builtin object.

State and persistence behavior: no runtime state is owned here. The object list determines whether features implemented across this subset, such as copy-up, directory mutation, file I/O forwarding, export file handles, and inode metadata handling, are present in the final overlayfs binary.

Dependencies and integration points: depends on Kbuild conventions and the Kconfig symbol from `Kconfig`. The listed objects depend on shared declarations in `overlayfs.h`; omitting any object would break cross-file references such as `ovl_copy_up()`, `ovl_file_operations`, `ovl_dir_inode_operations`, or `ovl_export_operations`.

Risks and test signals: object ordering rarely matters for C symbol resolution but missing additions are easy to overlook when new source files are introduced. Build tests should verify overlayfs as module and builtin, link with all config combinations, and ensure feature symbols referenced by Kconfig-gated code resolve.
