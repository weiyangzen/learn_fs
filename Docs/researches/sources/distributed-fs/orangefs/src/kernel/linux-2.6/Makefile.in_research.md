## sources/distributed-fs/orangefs/src/kernel/linux-2.6/Makefile.in

Purpose: Autoconf template for building the Linux 2.6 PVFS2 kernel module through kbuild, including source symlink setup for out-of-tree builds.

Important APIs and targets: Defines `csrc` and `hsrc` for the kernel module, including `acl.c`. In kbuild mode (`KERNELRELEASE` set), it sets `EXTRA_CFLAGS`, `obj-m += pvfs2.o`, and `pvfs2-objs := $(objs)`. Outside kbuild, `default` invokes `$(MAKE) -C $(KDIR) SUBDIRS=$(PWD) modules`, `links` creates missing symlinks, and `clean` removes symlinks plus generated module artifacts and `.cmd` files.

Control flow: The makefile switches behavior based on whether it is being evaluated by the kernel build system. The outer invocation prepares links to the source directory, then delegates to the configured kernel source. The inner invocation tells kbuild which objects compose `pvfs2.ko`.

State and persistence: Generates symlinks for source/header files in the build directory, object files, `pvfs2.o`, `pvfs2.ko`, module metadata, `.cmd` files, and `.tmp_versions`.

Dependencies and integration points: Uses configure substitutions for source/build roots, kernel source path, version, read-ahead cache/reset-file-position feature macros, and quiet build behavior. Includes OrangeFS/PVFS include directories needed by kernel sources.

Risks: The legacy `SUBDIRS=$(PWD)` interface is version-sensitive for newer kernels. Include and feature macros must match the configured kernel headers exactly. `links` does not refresh existing stale symlinks. `clean` removes only symlinked sources/headers, which is safer than the 2.4 makefile but still depends on correct directory layout.

Test signals: Run configured module builds against supported kernel versions, inspect generated kbuild command lines with `V=1`, verify ACL object inclusion, verify out-of-tree symlink creation/removal, load/unload `pvfs2.ko`, and test rebuild after source path changes.
