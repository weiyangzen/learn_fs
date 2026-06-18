# File Research: sources/cow-pools/nilfs-utils/sbin/mount/Makefile.am

## Scope

Builds NILFS mount and umount helper binaries in either libmount or legacy util-linux compatibility mode.

## Build Behavior

- Always builds core sbin programs `mount.nilfs2` and `umount.nilfs2`.
- Common headers include `mount.nilfs2.h`; libmount builds add `mount_attrs.c`, `libmount_compat.h`, and `mount_attrs.h`.
- Legacy builds use `fstab.c`, `mount_mntent.c`, `mount_opts.c`, `sundries.c`, `xmalloc.c`, and related headers.
- Both helper variants link realpath and cleaner-exec libraries plus configured mount, SELinux, and POSIX timer libraries.
- Optional compatibility symlink install/uninstall hooks mirror helpers into `$(exec_prefix)/sbin`.

## Dependencies And Risks

The conditional `CONFIG_LIBMOUNT` switch selects distinct source trees with similar semantics. Packaging must keep both variants compiling because the same program names are emitted from different source files.
