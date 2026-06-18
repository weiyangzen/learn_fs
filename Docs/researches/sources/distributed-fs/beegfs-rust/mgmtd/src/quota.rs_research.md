<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/quota.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/quota.rs

Purpose: periodically collects quota usage from storage nodes, stores it in SQLite, calculates exceeded quota IDs, and pushes enforcement state to meta/storage nodes.

Important APIs/types/functions: `fetch_and_update()` gathers configured user/group IDs, requests `GetQuotaInfo` from each storage target owner, and replaces `quota_usage` per successfully fetched target. `distribute_exceeded()` builds `SetExceededQuota` messages for every pool/id-type/quota-type combination and fills exceeded IDs when licensed. `try_read_quota_ids()` parses whitespace-separated numeric IDs from files.

Control flow: collection skips if quota feature is not licensed. It discovers mapped storage targets, builds ID sets from system users/groups, files, and configured ranges, concurrently requests user and group quota per target, and only updates a target when both requests succeed. Enforcement sends empty messages too, so stale exceeded IDs are cleared on nodes.

State and persistence: mutates `quota_usage` rows; reads pools, targets, quota limits, default limits, and user config. Sends enforcement state to all meta/storage nodes.

Dependencies and integration points: called by `timer.rs` when quota is enabled. Integrates license checks, system ID iteration, BeeMsg quota messages, and SQLite aggregation.

Risks: large configured ID ranges can create heavy network and DB load. Partial target fetch failure intentionally preserves old usage for that target. Enforcement can be very message-heavy because it sends pool x id-type x quota-type messages to every node.

Test signals: async tests cover quota collection, failed-fetch preservation/removal behavior, and exceeded quota message content across pools/types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/quota.rs -->
