# File Research: sources/cow-pools/openzfs/module/zfs/spa_errlog.c

## Summary
Implements ZFS persistent logical data error logs. It supports both the legacy flat bookmark log and the newer `head_errlog` format that groups errors by head dataset and stores block birth TXGs.

## Main Responsibilities
- Logs pending uncorrectable data errors into in-memory AVL trees.
- Syncs current and scrub error lists into on-disk ZAP logs.
- Rotates logs when scrubs complete.
- Reports known errors to userland as bookmark arrays.
- Removes healed errors from pending and on-disk logs.
- Upgrades legacy error logs to the head-dataset format.
- Deletes or swaps dataset-specific errlogs for destroy/promote operations.

## Key APIs
- `spa_log_error()`.
- `spa_get_errlog()`, `spa_approx_errlog_size()`, `spa_get_last_errlog_size()`.
- `spa_errlog_rotate()`, `spa_errlog_drain()`, `spa_errlog_sync()`.
- `spa_remove_error()`.
- `spa_upgrade_errlog()`.
- `spa_delete_dataset_errlog()`, `spa_swap_errlog()`.
- `find_birth_txg()`, `find_top_affected_fs()`, `zep_to_zb()`, `name_to_errphys()`.
- `sync_error_list()`.

## Important Behavior
Errors are first inserted into `spa_errlist_last` or `spa_errlist_scrub` depending on scrub state. In sync context, lists are copied, locks are reordered safely, healed entries are removed, and errors are written to `DMU_POOL_ERRLOG_LAST` or `DMU_POOL_ERRLOG_SCRUB`.

Legacy logs key entries by full `zbookmark_phys_t`. `head_errlog` logs use a top-level ZAP keyed by head dataset object, with per-head ZAPs keyed by object/level/blkid/birth. Userland enumeration checks heads, snapshots, and clones to report affected datasets and can mark no-longer-present errors as healed.

## Risks
Lock ordering is explicit: dataset config locks precede errlog locks, and in-core lists are copied before disk updates because errlog writes can themselves encounter I/O errors. `head_errlog` processing depends on dataset holds, decryption availability, block-pointer birth lookup, and snapshot/clone ancestry. Upgrade intentionally skips entries it cannot validate to avoid permanent spurious errors.
