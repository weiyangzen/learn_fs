# sources/distributed-fs/ceph-client/fs/xfs/scrub/quota.c

## Purpose
`quota.c` scrubs the quota metadata file and individual dquot records for one quota type. It checks structural backing mappings, limit/timer consistency, and resource counts that are obviously impossible.

## Important APIs, Types, And Functions
`xchk_quota_to_dqtype` maps scrub types to user, group, or project dquot types. `xchk_setup_quota` validates quota availability, installs the quota inode as the live inode, and locks it. `xchk_quota` drives the full check. `struct xchk_quota_info` tracks the scrub context and monotonic dquot ids. Helpers include `xchk_quota_data_fork`, `xchk_quota_item`, `xchk_quota_item_bmap`, and `xchk_quota_item_timer`.

## Control Flow
Setup rejects disabled quotas, invalid scrub types, and quota types not enabled. Scrub first runs metadata inode fork checks and then walks quota inode extents to reject unwritten, delalloc, or out-of-range mappings. It drops the quota inode ILOCK before using normal dquot iteration. Each dquot is locked after the quota inode ILOCK is acquired in the quota locking order; its file offset and cached disk address are cross-checked against `xfs_bmapi_read`.

The item check validates monotonic id iteration, hard limits relative to filesystem size, soft limit ordering, resource counts against total data/realtime/inode capacity, hard-limit exceedance warnings, and timer presence when usage exceeds soft or hard limits.

## State And Persistence Behavior
Scrub is read-only. It sets corruption or warning flags but does not update dquots. It uses dquot locks and quota inode locks for consistency during checks.

## Dependencies And Integration Points
The file depends on XFS quota manager iteration, dquot locking, bmap reads, metadata inode fork scrub, and scrub setup. It shares the dqtype helper with quota repair.

## Risks And Edge Cases
Reflink filesystems can legitimately show block counts above physical space due to shared accounting, so those become warnings instead of corruption. Root dquot id zero bypasses hard-limit exceedance review. Incorrect lock ordering can deadlock with quota operations, which is why the code explicitly uses ILOCK then dquot lock.

## Test Signals
Tests should cover quota off, one quota type off, unwritten quota file extents, out-of-range extents, dquot block holes, bad cached block address, soft greater than hard, missing or stale timers, reflink over-accounting, and non-monotonic dquot iteration.
