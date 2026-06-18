# sources/distributed-fs/ceph-client/fs/ext2/Makefile

Purpose: Defines Kbuild object composition for the ext2 filesystem driver.

Important APIs/types/functions: `obj-$(CONFIG_EXT2_FS) += ext2.o` creates the composite ext2 object. Core members are `balloc.o`, `dir.o`, `file.o`, `ialloc.o`, `inode.o`, `ioctl.o`, `namei.o`, `super.o`, `symlink.o`, and `trace.o`. Optional members are gated by `CONFIG_EXT2_FS_XATTR`, `CONFIG_EXT2_FS_POSIX_ACL`, and `CONFIG_EXT2_FS_SECURITY`.

Control flow: Kbuild composes `ext2.o` from mandatory and optional object lists. `CFLAGS_trace.o := -I$(src)` lets tracepoint infrastructure include the local `trace.h`.

State and persistence behavior: No runtime state. The file determines which feature implementations exist in the built driver.

Dependencies and integration points: Integrated with Kconfig symbols, tracepoint generation, VFS feature files, xattr handlers, ACL support, and security-label support.

Risks: Removing a mandatory object breaks core operation tables or exported internal helpers. Optional object gating must stay consistent with stubs in headers such as `acl.h` and `xattr.h`.

Test signals: Build ext2 under all option combinations; validate tracepoint compilation; confirm undefined symbols do not appear when xattr, ACL, or security support is disabled.
