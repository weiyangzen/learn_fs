<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/debugfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/debugfs/Makefile

Purpose: builds the debugfs filesystem object when `CONFIG_DEBUG_FS` is enabled.

Important APIs/types/functions: Kbuild variables `debugfs-objs := inode.o file.o` and `obj-$(CONFIG_DEBUG_FS) += debugfs.o`.

Control flow: Kbuild links `inode.o` and `file.o` into `debugfs.o`, then includes that object in the kernel or module according to the `CONFIG_DEBUG_FS` tristate-like build setting.

State and persistence: no runtime state; this is build metadata only. It determines whether the debugfs registration, inode cache, creation APIs, and file proxy helpers are compiled.

Dependencies and integration: integrates with the Linux kernel Kbuild system and the `CONFIG_DEBUG_FS` Kconfig option. `inode.c` owns filesystem registration and object creation, while `file.c` owns typed file helpers and removal-safe proxy operations.

Risks: missing an object here would surface as unresolved symbols or absent debugfs functionality. The file deliberately keeps debugfs as a two-object composite, so adding new source files requires updating `debugfs-objs`.

Test signals: kernel build with `CONFIG_DEBUG_FS=y` or module-style configurations should compile and expose debugfs APIs. A build with `CONFIG_DEBUG_FS=n` should omit `debugfs.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/debugfs/Makefile -->
