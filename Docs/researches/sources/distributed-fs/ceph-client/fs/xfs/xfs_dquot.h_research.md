# sources/distributed-fs/ceph-client/fs/xfs/xfs_dquot.h

Purpose: Defines the in-core XFS dquot model, quota resource counters, preallocation thresholds, lock helpers, type/enforcement predicates, and public dquot APIs.

Important APIs, types, and functions: Defines `struct xfs_dquot_res`, `struct xfs_dquot_pre`, `struct xfs_dquot`, low-space constants, and inline helpers for flush locking, type checks, quota-on checks, inode dquot access, enforcement, low-space detection, and reference holds. Declares lookup, flush, locking, conversion, timer, preallocation, and buffer-attach functions.

Control flow: Callers use predicates before quota lookup/enforcement, completion helpers around dqflush serialization, and lock helpers for multi-dquot transactions.

State and persistence: `struct xfs_dquot` mirrors persistent limits, counters, and timers while adding reservations, file offsets, backing daddr, log item, LRU/cache refs, flush state, and pin wait state.

Dependencies and integration points: Used by quota accounting, transaction reservation, inode ownership changes, dquot log items, AIL writeback, and quota ioctl code.

Risks and test signals: Risks are incorrect enforcement predicates, reservation/count confusion, low-space underflow with zero hard limits, and lock nesting mistakes. Test multi-dquot locking, disabled/enforced permutations, metadata inode exclusion, and preallocation decisions.
