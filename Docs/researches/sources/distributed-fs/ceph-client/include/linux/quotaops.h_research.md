# sources/distributed-fs/ceph-client/include/linux/quotaops.h

Purpose: exposes VFS quota operation helpers to filesystems and supplies no-op or inode-byte-accounting fallbacks when `CONFIG_QUOTA` is disabled.

Important APIs and types: `sb_dqopt()` returns the superblock's `quota_info`. `is_quota_modification()` detects attribute changes needing quota transfer. In quota builds, declarations include `dquot_initialize()`, `dqget()`, `dqgrab()`, `dqput()`, allocation/free/reservation helpers, quota on/off/load/sync/state functions, `dquot_transfer()`, and exported `dquot_operations`/`dquot_quotactl_sysfile_ops`. Inline status helpers test usage, limits, suspension, loaded, and active state. Common wrappers translate blocks to bytes via `inode->i_blkbits` and mark inodes dirty after successful accounting.

Control flow: filesystems call initialization before operations that charge quota, call allocation/reservation/free helpers during block and inode changes, transfer quota on owner/project changes, sync/writeback dirty dquots, and use quotaon/off helpers at mount or quotactl time. Disabled builds preserve basic `i_blocks`/byte accounting while accepting all quota operations.

State and persistence: state is owned by `quota.h` structures and filesystem quota files. This header controls when quota changes mark inodes dirty and when reservations are converted into real usage.

Dependencies and integration points: depends on VFS `fs.h`, quota core declarations, mount idmaps, inode dirtying, and filesystem block-size semantics. It is the normal integration point for filesystem write, truncate, chown, and quota-control paths.

Risks and test signals: risks include missing `dquot_initialize()`, incorrect block-to-byte shifts, inode dirtying omissions, nofail allocation masking quota failures, transfer races under `i_rwsem`, and disabled-config behavior diverging from quota-enabled behavior. Test quota enforcement during create/write/truncate/chown/project-ID changes, delayed allocation reserve/claim/reclaim, quota disabled builds, remount suspend/resume, quota sync/writeback, and ENOSPC/EDQUOT handling.
