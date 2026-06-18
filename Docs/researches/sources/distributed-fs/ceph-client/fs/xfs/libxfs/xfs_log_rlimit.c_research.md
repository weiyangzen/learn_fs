# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_log_rlimit.c

Purpose: Computes the maximum transaction reservation and minimum legal log size for a filesystem feature set. It preserves historical compatibility where older kernels expected overestimated log sizes, while allowing corrected computations for newer feature combinations.

Important APIs: `xfs_log_get_max_trans_res` and `xfs_log_calc_minimum_size`. Private helpers include `xfs_want_minlogsize_fixes`, `xfs_log_calc_max_attrsetm_res`, and `xfs_log_calc_trans_resv_for_minlogblocks`.

Control flow: feature gating checks the ondisk superblock and enables corrected minimum-log computations only for v5 filesystems with parent pointers. Attribute set maximum reservation computes the largest local attr value reservation, with a parent-pointer-era fix for a unit conversion issue. The alternate transaction reservation table either uses modern calculations or temporarily restores legacy rmap/reflink assumptions, old rmap maxlevels, and older log counts/reservation formulas. `xfs_log_get_max_trans_res` scans the reservation table for the largest total reservation, comparing attrsetm separately. `xfs_log_calc_minimum_size` converts the max reservation to log blocks, accounts for log stripe unit padding, multiplies by `XFS_MIN_LOG_FACTOR`, and returns filesystem blocks.

State and persistence: no persistent writes. It reads superblock features and mount geometry; temporarily mutates `m_rmap_maxlevels` during legacy calculation and restores it before return.

Dependencies and integration: used by mkfs/mount-style validation to reject undersized logs. Depends on transaction reservation calculators, bmap/da space formulas, log unit reservation helpers, superblock feature predicates, and tracepoints.

Risks and test signals: risks include silently reducing minimum log size for filesystems that older kernels should mount, incorrect temporary mount state restoration, and log stripe unit rounding errors. Tests should compare minlog outputs across rmap/reflink/parent feature combinations, small AG geometries, large attr cases, and stripe-unit configurations.
