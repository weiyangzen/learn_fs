# sources/distributed-fs/ceph-client/fs/xfs/scrub/quota_repair.c

## Purpose
`quota_repair.c` repairs quota file mappings, verifier-visible dquot block damage, and fixable dquot field inconsistencies. When counters are suspicious, it schedules a full quotacheck.

## Important APIs, Types, And Functions
`xrep_quota` is the public repair entry. `struct xrep_quota_info` tracks whether a later quotacheck is required. Mapping and block repair is handled by `xrep_quota_data_fork`, `xrep_quota_block`, `xrep_quota_item_bmap`, and `xrep_quota_item_fill_bmap_hole`. Dquot field repair is handled by `xrep_quota_item`, `xrep_quota_item_timer`, `xrep_quota_fix_timer`, and `xrep_quota_problems`.

## Control Flow
Repair retakes the quota inode ILOCK, repairs generic metadata inode forks, converts unwritten quota extents, truncates mappings beyond the maximum dquot id, cancels CoW reservations, clears reflink state, and rewrites bad dquot blocks. Verifier failures are repaired by rereading without ops, initializing every dquot in the block with correct magic, version, type, id, UUID, checksum, and timers.

After fork and buffer repair, it finishes deferred work, rolls the transaction, unlocks the quota inode, and iterates dquots through the quota manager. Per-dquot repair fills missing backing blocks, corrects cached file offsets and disk addresses, clamps soft limits to hard limits, caps impossible resource counts to filesystem totals where appropriate, adjusts reservations by the same delta, fixes timers through quota manager helpers, marks dquots dirty, logs them, and rolls.

## State And Persistence Behavior
Persistent changes include quota inode bmap changes, initialized dquot buffers, truncated invalid quota file regions, dquot limits, counters, timers, reservations, and quota CHKD scheduling via `xrep_force_quotacheck`. Transactions are repeatedly rolled to commit buffer and dquot changes safely.

## Dependencies And Integration Points
It depends on quota scrub type conversion, XFS bmap, dquot buffer verifiers, quota manager limit/timer adjustment, reflink cleanup, deferred operations, and transaction repair helpers. It complements `quotacheck_repair.c`, which recomputes exact counters.

## Risks And Edge Cases
Repair does not know exact counts when counters exceed physical limits, so it caps and forces quotacheck. Reflink changes count semantics. Filling sparse quota holes allocates blocks and initializes full dquot clusters. Bad verifier data is repaired at block granularity. Dquot locks must be released only through transaction completion paths when joined.

## Test Signals
Tests should cover sparse quota holes, unwritten extents, mappings past max dquot id, bad dquot magic/type/id/checksum, bigtime timer repair, counters above filesystem size, softlimit greater than hardlimit, reflink quota files, and forced quotacheck after repair.
