# File Research: sources/cow-pools/openzfs/module/zfs/zfs_log.c

## Role

`zfs_log.c` builds ZIL intent log records for ZFS filesystem operations. These routines are called inside DMU transactions and either create replayable in-memory `itx_t` records during normal operation or avoid/logically skip work while ZIL replay is already in progress.

## Main Components

- `zfs_log_create_txtype()`: maps create kind plus ACL/xvattr presence to the correct ZIL transaction type.
- `zfs_log_xvattr()`: serializes extended attribute masks and optional values into `lr_attr_t` trailing data.
- FUID helpers: `zfs_log_fuid_ids()` and `zfs_log_fuid_domains()` append FUID IDs and domain strings to log records.
- `zfs_xattr_owner_unlinked()`: suppresses logging for extended-attribute nodes whose owner is already unlinked.
- Namespace logging:
  - `zfs_log_create()`
  - `zfs_log_remove()`
  - `zfs_log_link()`
  - `zfs_log_symlink()`
  - `zfs_log_rename()`
  - `zfs_log_rename_exchange()`
  - `zfs_log_rename_whiteout()`
- Data and metadata logging:
  - `zfs_log_write()`
  - `zfs_log_truncate()`
  - `zfs_log_setattr()`
  - `zfs_log_setsaxattr()`
  - `zfs_log_acl()`
  - `zfs_log_clone_range()`

## Important Behavior

- Most functions return immediately when `zil_replaying(zilog, tx)` is true.
- Operations on unlinked znodes are generally not logged.
- Create logging encodes object IDs, dnode slot count, mode, UID/GID or FUID owner/group, generation, create time, rdev, optional xvattrs, optional ACLs, FUID metadata, and name.
- Remove logging calls `zil_remove_async()` for unlinked removed objects to prevent stale async write records from leaking into a reused object ID.
- Write logging chooses `WR_COPIED`, `WR_NEED_COPY`, or `WR_INDIRECT` through `zil_write_state()`, may inline data for copied writes, splits indirect writes on block boundaries, and accounts write-log bytes through `dsl_pool_wrlog_count()`.
- Clone-range logging splits block pointer arrays so each intent record stays within `zil_max_log_data()`.

## Dependencies

- ZIL internals: `zil_itx_create()`, `zil_itx_assign()`, `zil_write_state()`, `zil_max_copied_data()`, `zil_max_log_data()`
- Znode/SA accessors: `sa_lookup()`, `ZTOZSB()`, `ZTOUID()`, `ZTOGID()`
- DMU/dbuf for copied write data: `sa_get_db()`, `dmu_read_by_dnode()`
- FUID and ACL support: `zfs_fuid_info_t`, `vsecattr_t`, ACE/FUID record layout macros

## Invariants And Safety Notes

- These functions must be called within a DMU transaction.
- Record sizes are computed before allocation; trailing record payloads are packed manually, so size arithmetic must match replay-side decoding exactly.
- Replay compatibility depends on stable ZIL record layouts and transaction type choices.
- `zfs_log_write()` attaches the stable-storage callback only to the last generated write intent record for a logical write.
- Extended attribute owner checks differ slightly on FreeBSD because vnode lock semantics prevent the ordinary `zrele()` pattern.

## When Modifying

- Any record layout change must be mirrored in ZIL replay code and remain compatible with existing on-disk log records.
- Be conservative with new fields in packed trailing data; update size calculations first.
- Preserve replay and unlinked-object guards unless there is a precise replay-side reason to change them.
