## sources/distributed-fs/ceph-client/fs/xfs/xfs_itable.h

Purpose: defines the in-memory bulk inode request contract and callback types used by bulkstat and inumbers implementations.

Important APIs and types: `struct xfs_ibulk` stores mount, idmap, user buffer pointer, start inode cursor, requested count, output count, bulk flags, and iwalk flags. Flags include `XFS_IBULK_NREXT64` to request 64-bit extent counts and `XFS_IBULK_METADIR` to expose metadata-directory records. `xfs_ibulk_advance` advances the user buffer and returns `-ECANCELED` when the caller-provided output count is full. Callback typedefs are `bulkstat_one_fmt_pf` and `inumbers_fmt_pf`. Public functions mirror `xfs_itable.c`.

Control flow: callers initialize `xfs_ibulk`, choose formatter callbacks, and call `xfs_bulkstat_one`, `xfs_bulkstat`, or `xfs_inumbers`. Formatters call `xfs_ibulk_advance` after copying one record out.

State and persistence behavior: the header has no persistent state. `xfs_ibulk` is mutable per-request cursor state, and its `startino`/`ocount` fields are the basis for resumable ioctl calls.

Dependencies and integration: used by native ioctl, compat ioctl, and inobt walk code. The callback contract deliberately separates kernel collection from ABI-specific copyout.

Risks and test signals: incorrect advancement sizes corrupt userspace buffers or cursor semantics; missing `-ECANCELED` handling can leak internal stop codes. Tests should verify exact output counts, restart cursors, legacy/native/compat record sizes, nrext64, metadir filtering, and inumbers formatting.
