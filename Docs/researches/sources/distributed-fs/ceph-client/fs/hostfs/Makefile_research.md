# sources/distributed-fs/ceph-client/fs/hostfs/Makefile

Purpose: this Makefile builds UML hostfs support. It defines the kernel-side hostfs object composition and includes the UML-specific build rules needed for user-space syscall wrapper objects.

Important build variables: `hostfs-objs := hostfs_kern.o` builds the main `hostfs.o` module/builtin object from the kernel VFS implementation. `hostfs-builtin-$(CONFIG_HOSTFS) += hostfs_user.o hostfs_user_exp.o` adds the user-space helper and export objects when `CONFIG_HOSTFS` is enabled. `obj-y := $(hostfs-builtin-y) $(hostfs-builtin-m)` ensures those helper objects are built into the UML environment. `obj-$(CONFIG_HOSTFS) += hostfs.o` controls the actual filesystem object.

Control flow: Kbuild evaluates `CONFIG_HOSTFS`, builds the kernel half as `hostfs.o`, builds the helper/export objects when enabled, then includes `$(srctree)/arch/um/scripts/Makefile.rules` so UML can compile mixed kernel/user helper code correctly.

State and persistence: there is no runtime state, but the build layout determines whether hostfs can link its kernel code against exported wrapper symbols.

Dependencies and integration: this file is specific to the UML architecture. It integrates with Kbuild, `CONFIG_HOSTFS`, and `arch/um/scripts/Makefile.rules`. The split mirrors the source split: `hostfs_kern.c` calls APIs declared in `hostfs.h`; `hostfs_user.c` implements them; `hostfs_user_exp.c` exports them.

Risks: omitting `hostfs_user.o` or `hostfs_user_exp.o` would leave unresolved symbols or unavailable wrappers. The `obj-y` assignment for helper objects is unusual compared with ordinary filesystem Makefiles and should not be normalized without understanding UML build rules.

Test signals: build UML with `CONFIG_HOSTFS=y` and as module if supported, check that `hostfs.o` links with all `hostfs_user` symbols, and build with `CONFIG_HOSTFS=n` to ensure no stale helper objects are included unexpectedly.
