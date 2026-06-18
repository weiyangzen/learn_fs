# sources/distributed-fs/ceph-client/fs/hostfs/hostfs_user_exp.c

Purpose: this file exports the hostfs user-wrapper symbols for GPL kernel use in the UML build.

Important APIs: it includes `<linux/module.h>` and `hostfs.h`, then calls `EXPORT_SYMBOL_GPL()` for every wrapper implemented by `hostfs_user.c`: stat/access/open/dir iteration/read/write/lseek/fsync/replace/close/create/setattr/symlink/unlink/mkdir/rmdir/mknod/link/readlink/rename/rename2/statfs.

Control flow: there is no runtime logic beyond module symbol registration. The export table must match both the declarations in `hostfs.h` and the implementations in `hostfs_user.c`.

State and persistence: no state is held or changed here. Its effect is link-time/runtime symbol availability for the kernel-side hostfs object.

Dependencies and integration: this file is tied to the UML hostfs Makefile, which builds `hostfs_user_exp.o` together with `hostfs_user.o` when `CONFIG_HOSTFS` is enabled. `hostfs_kern.c` depends on these exported symbols resolving.

Risks: missing an export causes link or module-load failures; exporting a stale name causes compile failure if prototypes change. Over-exporting would expand the callable surface for GPL modules, so the list should stay limited to the hostfs wrapper ABI.

Test signals: build hostfs after adding/removing wrapper prototypes, check module symbol resolution, and run `modpost`/Kbuild diagnostics for missing or unused exports.
