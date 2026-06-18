<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/timer.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/timer.rs

Purpose: starts and runs periodic background tasks for stale-client deletion, quota updates, quota enforcement, and buddy-group switchover.

Important APIs/types/functions: `start_tasks()` spawns task futures. `delete_stale_clients()` periodically deletes old client nodes. `update_quota()` runs quota collection and exceeded distribution. `switchover()` periodically calls `db::buddy_group::check_and_swap_buddies()` and broadcasts target refreshes after swaps.

Control flow: stale-client loop sleeps for configured timeout or exits on pre-shutdown. Quota loop runs immediately, then sleeps for the configured interval. Switchover uses `node_offline_timeout / 6`, skips missed ticks, delays the initial real check by one interval, and exits on pre-shutdown.

State and persistence: stale-client and switchover tasks mutate SQLite; quota task mutates quota usage and sends enforcement messages. Switchover sends `RefreshTargetStates` after DB swaps.

Dependencies and integration points: started by `lib.rs`; relies on run-state pre-shutdown signaling, DB helpers, quota module, and BeeMsg refresh messages.

Risks: no task is joined here; lifecycle is controlled by cloned run-state handles. Switchover timing must align with node target-offline behavior to avoid unsafe failover around management shutdown. Errors are logged and loops continue.

Test signals: no direct tests. DB buddy-group tests cover swap logic; integration tests should validate task exit on pre-shutdown and quota scheduling behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/timer.rs -->
