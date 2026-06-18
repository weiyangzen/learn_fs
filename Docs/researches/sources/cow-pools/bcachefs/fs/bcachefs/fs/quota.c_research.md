# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/quota.c

This file implements bcachefs quota metadata validation, superblock quota defaults, in-memory accounting, and Linux quotactl operations when `CONFIG_BCACHEFS_QUOTA` is enabled.

Always-built metadata operations:
- `bch2_sb_quota_validate()` validates the superblock quota field size.
- `bch2_sb_quota_to_text()` prints per-type flags and per-counter timer/warn settings.
- `bch_sb_field_ops_quota` registers the superblock field handlers.
- `bch2_quota_validate()` ensures quota bkey type index is below `QTYP_NR`.
- `bch2_quota_to_text()` prints hard/soft limits for space and inode counters.

Quota accounting:
- Uses per-quota-type `genradix` tables protected by per-type mutexes.
- `bch2_quota_acct()` checks enabled user/group/project quota types, applies hard/soft limit logic, updates in-memory counters, and sends quota netlink warnings.
- `bch2_quota_transfer()` moves space and inode usage between qids, used when ownership/project changes.
- `bch2_quota_check_limit()` enforces hard limits unless privileged, starts soft-limit timers, detects grace expiry, and clears warning state when usage drops.

Quota initialization:
- `bch2_fs_quota_init()` initializes locks.
- `bch2_fs_quota_exit()` frees genradix tables.
- `bch2_sb_get_or_create_quota()` creates the quota superblock field and defaults timer limits to seven days.
- `bch2_fs_quota_read()` reads on-disk quota limits and scans all inode snapshots to populate current usage without limit checks.

Quotactl support:
- `bch2_quota_enable()` enables enforcement flags but requires accounting to have been enabled at mount.
- `bch2_quota_disable()` clears enforcement flags.
- `bch2_quota_remove()` deletes quota btree ranges only when the corresponding quota accounting is disabled.
- `bch2_quota_get_state()` reports enabled accounting and timer/warn limits.
- `bch2_quota_set_info()` updates timer/warn limits in the superblock.
- `bch2_get_quota()` and `bch2_get_next_quota()` read in-memory quota state.
- `bch2_set_quota()` updates the quota btree and then mirrors new limits into memory.
- `bch2_quotactl_operations` wires these into the VFS quota interface.

Important details:
- Space limits are stored internally in sectors and converted to/from byte units for VFS quota structures.
- Quota reads account only live inodes discoverable via snapshot tree/master-subvolume lookup.
- Error paths return bcachefs error classes for VFS-facing calls.
