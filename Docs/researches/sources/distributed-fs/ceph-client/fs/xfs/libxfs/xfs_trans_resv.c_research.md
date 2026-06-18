# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_trans_resv.c

Purpose: Computes XFS transaction log reservations and log operation counts for all major metadata operations, including data writes, truncates, namespace changes, attributes, quotas, growfs, realtime metadata, deferred intent completions, and atomic write ioend completion.

Important APIs, types, and functions: Exports `xfs_allocfree_block_count`, finish reservation helpers for EFI/RUI/CUI/BUI and realtime variants, minimum-log-size variants for write/truncate/quota allocation, `xfs_trans_resv_calc`, `xfs_calc_max_atomic_write_fsblocks`, `xfs_calc_atomic_write_log_geometry`, and `xfs_calc_atomic_write_reservation`. Internal helpers calculate buffer overhead, inode log size, inobt/finobt/inode chunk reservations, realtime allocation/refcount block counts, namespace parent-pointer overheads, and per-transaction reservation bodies.

Control flow: Reservation formulas combine fixed item overhead, log op headers, buffer log format overhead rounded to historical 128-byte units, inode log sizes, btree height-derived split budgets, quota overhead, and feature-dependent deferred intent costs. `xfs_trans_resv_calc` fills `struct xfs_trans_resv` in dependency order, computing attribute reservations before namespace reservations because parent pointers may invoke xattr updates. Atomic write helpers derive per-intent and finish-step overhead, then calculate supported block counts or required log reservation and minimum log blocks.

State and persistence: The file persists nothing directly. It populates `mp->m_resv`, which controls runtime transaction ticket sizing and minimum log sizing. Bad values can cause transaction reservation overrun, unnecessary log size rejection, or excessive reserved log space.

Dependencies and integration points: Depends on mount geometry, btree maxlevels, quota constants, realtime bitmap sizing, deferred log item space calculators, parent pointer attr formats, and log minimum size calculations. It is consumed by transaction allocation and mount-time log validation.

Risks and test signals: Risks include under-reserving when feature combinations stack, preserving old reflink minimum-log behavior incorrectly, missing realtime rmap/refcount costs, parent-pointer relog overhead mistakes, and arithmetic overflow in atomic write sizing. Test fstests covering reflink, rmapbt, rtreflink, rtgroups, parent pointers, quota allocation, growfs rt/data, min-log-size mount rejection, atomic writes with varied block counts, and injected transaction reservation overruns.
