# File Research: sources/cow-pools/bcachefs-tools/fs/fs/quota.c

## Purpose
Implements bcachefs quota format validation, superblock quota settings, in-memory quota accounting, quota limit enforcement, mount-time quota reconstruction, and Linux `quotactl_ops` integration.

## Main Contents
- Text labels for user/group/project quota types and space/inode counters.
- Superblock quota field operations:
  - `bch2_sb_quota_validate()` checks field size.
  - `bch2_sb_quota_to_text()` prints flags, timelimits, and warnlimits.
- Quota bkey operations:
  - `bch2_quota_validate()` rejects quota keys whose inode position is outside `QTYP_NR`.
  - `bch2_quota_to_text()` prints hard/soft limits for space and inode counters.
- Under `CONFIG_BCACHEFS_QUOTA`, debugging text helpers for `qc_info` and `qc_dqblk`.
- `for_each_set_qtype()` iteration over enabled quota types from mount options.
- Limit checking and notification:
  - `bch2_quota_check_limit()` handles hardlimit, softlimit, timer, warning issue/clear, and `KEY_TYPE_QUOTA_NOCHECK`.
  - `flush_warnings()` sends kernel quota netlink warnings.
- Accounting APIs:
  - `bch2_quota_acct()` charges or uncharges a single counter across all enabled qtypes.
  - `bch2_quota_transfer()` moves space and one inode between qids for selected qtypes.
- `__bch2_quota_set()` loads persistent limits from quota bkeys into in-memory radix tables and optionally updates timer/warn fields.
- Filesystem lifecycle: `bch2_fs_quota_init()`, `bch2_fs_quota_exit()`, `bch2_fs_quota_read()`.
- Mount-time reconstruction: reads superblock limits, quota btree keys, then scans all inode snapshots and charges live master-subvolume inodes.
- Quota control operations for enable, disable, remove, get state, set info, get quota, get next quota, and set quota.

## Integration Notes
Quota ids come from `bch_qid()` in `quota.h`, derived from inode uid/gid/project. Persistent hard/soft limits live in `BTREE_ID_quotas`, while global grace/warn limits live in the superblock quota field. Runtime usage is maintained in `c->quotas[type].table` radix tables protected by per-type mutexes. `bch2_quotactl_operations` exposes this implementation to the VFS.

## Risks and Edge Cases
- Space values in VFS quota structs are bytes while internal accounting uses sectors; conversions shift by 9.
- `bch2_quota_transfer()` passes `dst_q[i]->c[...] .v + delta` as the delta argument to `bch2_quota_check_limit()`, even though `bch2_quota_check_limit()` itself adds `qc->v + v`. This deserves audit because it appears to double-count existing destination usage during limit checks.
- Accounting is enabled only when corresponding mount options are active; enabling enforcement without accounting is rejected.
- Quota scan skips inodes deleted in a given snapshot by treating ENOENT as an advance condition.
