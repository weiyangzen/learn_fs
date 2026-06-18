## sources/distributed-fs/openafs/src/afs/LINUX/osi_vfs.h

Purpose: Linux vnode/VFS compatibility header that maps portable OpenAFS vnode and vattr concepts onto Linux inode and superblock types.

Important APIs and types: defines `vnode_t` as `struct inode`, aliases `vnode` to `inode`, maps vnode-style fields such as `v_op`, `v_fop`, `v_type`, `v_vfsp`, and `v_data` to inode fields, and maps vnode type constants (`VREG`, `VDIR`, `VLNK`, etc.) to Linux mode bits. It defines `enum vcexcl { EXCL, NONEXCL }`, file flag aliases (`FWRITE`, `FTRUNC`, `IO_APPEND`, `FSYNC`), permission aliases (`VREAD`, `VWRITE`, `VEXEC`, `VSUID`, `VSGID`), `vfs` as `super_block`, and `struct vattr`.

Control flow: no runtime control flow. This is compile-time glue consumed by Linux OSI and common AFS vnode code.

Dependencies and integration: depends on Linux inode, mode, time, uid/gid, and OpenAFS `afs_size_t` definitions included by callers. The `vattr_t` structure is central to `afs_getattr`, `afs_setattr`, `afs_fill_inode`, and Linux inode operation wrappers in `osi_vnodeops.c`.

State and persistence: no storage. Its macro mappings determine how other files read and write Linux inode state.

Risks: macro field aliases are sensitive to kernel structure evolution. The `v_data` alias to `u.generic_ip` is only valid on older kernels and must be guarded by surrounding compatibility macros elsewhere. `i_size_read`/`i_size_write` fallback macros are non-locking fallbacks for kernels lacking helpers.

Test signals: compile coverage across supported Linux kernel versions, attribute round-trips through `vattr2inode`/`iattr2vattr`, and vnode operation builds that exercise all mapped constants.
