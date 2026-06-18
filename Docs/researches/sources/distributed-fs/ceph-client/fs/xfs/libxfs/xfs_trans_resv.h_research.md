# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_trans_resv.h

Purpose: Defines transaction reservation data structures, reservation slots, log count constants, and prototypes for reservation calculators.

Important APIs, types, and functions: Defines `struct xfs_trans_res`, `struct xfs_trans_resv`, `M_RES`, directory operation reservation macros, default and operation-specific log counts, old reflink log counts retained for minimum log calculations, finish reservation prototypes, minimum-log-size calculators, and atomic write reservation helpers.

Control flow: Mount code calls `xfs_trans_resv_calc` to populate `M_RES(mp)`. Transaction allocation paths select a specific reservation slot such as `tr_write`, `tr_itruncate`, `tr_rename`, `tr_attrsetm`, `tr_growrtalloc`, or `tr_atomic_ioend`. Deferred operation completion code uses the finish helper prototypes for dynamic counts.

State and persistence: Reservation structures are in-memory mount state only. Their values indirectly constrain persistent metadata operations by ensuring enough journal space for complete atomic transactions.

Dependencies and integration points: Included by most XFS code that allocates transactions. It depends on transaction space macros from `xfs_trans_space.h` via consumers and on mount geometry.

Risks and test signals: Risks are missing reservation slots for new operations, changing historical log counts, and mismatched runtime vs minimum-log reservations. Test compile coverage, mount-time log sizing, every transaction type, and feature-specific logcount adjustments.
