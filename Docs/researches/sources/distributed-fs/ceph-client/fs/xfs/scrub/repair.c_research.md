# sources/distributed-fs/ceph-client/fs/xfs/scrub/repair.c

## Purpose
`repair.c` provides shared infrastructure for XFS online repair. It owns repair attempt/retry semantics, transaction rolling while retaining metadata locks, block reservation estimates, AG and rtgroup cursor setup, btree root discovery, quota fallback handling, metadata inode fork repair orchestration, and reservation reset helpers.

## Important APIs, types, and functions
Core entry points include `xrep_attempt`, `xrep_will_attempt`, `xrep_failure`, `xrep_roll_ag_trans`, `xrep_roll_trans`, `xrep_defer_finish`, `xrep_ag_has_space`, `xrep_calc_ag_resblks`, `xrep_calc_rtgroup_resblks`, `xrep_fix_freelist`, `xrep_find_ag_btree_roots`, `xrep_ag_btcur_init`, `xrep_ag_init`, `xrep_rtgroup_init`, `xrep_rtgroup_btcur_init`, `xrep_require_rtext_inuse`, `xrep_reset_perag_resv`, `xrep_metadata_inode_forks`, `xrep_setup_xfbtree`, `xrep_buf_verify_struct`, `xrep_check_ino_btree_mapping`, `xrep_inode_set_nblocks`, and `xrep_reset_metafile_resv`.

## Control flow
`xrep_attempt` drops scrub cursors, calls the operation-specific repair function, records stats, and converts success, drain requests, and lock escalation into `-EAGAIN` rescrub cycles. Transaction helpers dirty and hold AG headers across rolls and deferred work completion so repairs retain exclusive metadata control. Reservation estimators read AGI/AGF when possible and fall back to worst-case btree sizes. Root finding scans rmap-owned blocks, filters AGFL blocks, validates candidate buffers by magic/uuid/verifier, and records unique highest-level roots. Metadata inode repair runs subordinate scrub/repair passes over inode, data fork, and optional attr fork.

## State and persistence
Most state is transactional or in-core: scrub flags, repair stats, AG header buffers, perag/rtgroup cursor sets, quota flags, inode extent-count flags, and metadata reservation counters. Persistent changes happen only through callers' transactions, including quota flag updates, inode core updates, superblock logging, and repaired metadata roots.

## Dependencies and integration points
This file is the common layer for all repairers declared in `repair.h`. It integrates allocation, ialloc, rmap/refcount btrees, rtgroup metadata, quota, deferred operations, scrub subordinate contexts, xfiles, buffer verifiers, and health/reservation systems.

## Risks and test signals
Risks include retry loops with unchanged corruption flags, lock retention across transaction rolls, incorrect worst-case reservations, false root detection from stale AGFL buffers, quota flag races, and rtgroup/free-space validation mistakes. Tests should cover no-repair builds, force rebuild, drain/deadlock retry paths, repair success rescrub, AGF/AGI reread identity, root discovery ambiguity, metadata inode fork cleanup, zoned realtime checks, and ENOSPC reservation reset handling.
