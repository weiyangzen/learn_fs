# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_shared.h

Purpose: Collects XFS definitions shared between kernel and userspace libxfs that do not fit in more specific shared headers, especially verifier/btree op exports, transaction flags, superblock modification flags, buffer reference priorities, and inode geometry.

Important APIs, types, and functions: Declares many `xfs_buf_ops` verifier objects, btree op objects, btree type predicates such as `xfs_btree_is_rtrmap` and `xfs_btree_is_rtrefcount`, log reservation helpers, transaction flags `XFS_TRANS_*`, superblock modification masks `XFS_TRANS_SB_*`, buffer reference constants, and `struct xfs_ino_geometry`.

Control flow: Metadata modules publish verifier and btree operation tables here so generic btree, buffer, scrub, repair, and trace code can compare operation identities and route behavior. Transaction flags communicate logging, sync, reserve-pool, lowspace, writecount, freed-block, intent-done, and rtbitmap lock state through the transaction subsystem.

State and persistence: No runtime state is allocated here. The constants affect buffer cache retention, transaction semantics, and superblock field logging. `struct xfs_ino_geometry` is a mount-time cache of inode allocation and validation geometry derived from the superblock and feature bits.

Dependencies and integration points: Included throughout libxfs, kernel XFS, and userspace tools. It connects buffer verifiers, btree implementations, transaction accounting, and inode allocation geometry.

Risks and test signals: Risks are shared ABI/semantic drift, stale btree identity predicates when new ops are added, transaction flag bit collisions, and buffer reference changes that alter cache pressure. Test kernel and userspace builds, metadata verifier dispatch, trace string mappings, transaction flag propagation, and inode allocation on sparse/finobt configurations.
