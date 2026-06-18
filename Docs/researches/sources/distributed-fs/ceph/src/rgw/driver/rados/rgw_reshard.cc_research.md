# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_reshard.cc

## Purpose
This file implements dynamic and administrator-triggered bucket index resharding for the RADOS RGW backend. It calculates preferred shard counts, prepares new index generations, copies or replays bucket index entries into target shards, updates bucket layout metadata, maintains a reshard queue in RADOS objects, and runs the background reshard worker.

## Important APIs, Types, And Functions
- `RGWBucketReshard::calculate_preferred_shards()` decides whether expansion or reduction is needed based on object count, current shard count, max/min objects per shard, multisite multiplier, layout minimums, and optional prime shard preference.
- `BucketReshardShard` batches entries for one target shard, tracks category stats, writes cls operations asynchronously, and waits for completions.
- `BucketReshardManager` owns all target shards for a target layout and flushes/waits them as a unit.
- `init_target_index()`, `init_target_layout()`, `revert_target_layout()`, `init_reshard()`, `change_reshard_state()`, `cancel_reshard()`, `commit_target_layout()`, and `commit_reshard()` form the persistent reshard state machine.
- `RGWBucketReshardLock` wraps cls lock acquisition, release, and renewal over the reshard pool.
- `RGWBucketReshard::reshard_process()`, `do_reshard()`, and `execute()` implement the actual migration.
- `RGWReshard::{add,update,list,get,remove,process_entry,process_single_logshard,process_all_logshards}` implement the persistent queue and worker processing.
- `RGWReshardWait` provides blocking or coroutine-aware waits that can be canceled on shutdown.

## Control Flow
Dynamic shard calculation first determines whether expansion or reduction is warranted. Queue insertion hashes tenant and bucket name to a reshard log shard object. The background worker scans every log shard under a log-shard lock, lists queue entries, and calls `process_entry()`. Entry processing reloads current bucket info, drops stale queue records, performs extra safety checks for dynamic reductions, enforces multisite bilog-history limits, then constructs `RGWBucketReshard` and calls `execute()`.

`execute()` takes the bucket lock, optionally updates the queue entry initiator, calls `init_reshard()` to create target index objects and write target layout metadata, performs migration, and commits. If logrecord is supported, migration has two phases: `InLogrecord` copies the inventory while client writes record reshard log entries, then `change_reshard_state()` switches to `InProgress` to block writes and `reshard_process()` replays incremental records. If logrecord is unsupported, writes are blocked first and the inventory is copied once. Commit promotes `target_index` to `current_index`, appends a new log layout, optionally writes datalog entries for old shards, and deletes old index objects when no retained bilog layout references them.

## State And Persistence Behavior
Persistent state is split across bucket instance metadata, bucket index shard objects, reshard pool queue objects, cls lock objects, bucket index reshard status, reshard log entries, and data/bucket log layouts. `init_target_layout()` writes `layout.target_index`, increments the generation, and sets `layout.resharding` to either `InLogrecord` or `InProgress`. `revert_target_layout()` removes target index objects, trims reshard log entries, and clears target metadata. `commit_reshard()` writes the new current layout and cleans old index state only after commit. Many metadata updates retry `-ECANCELED` races up to ten times by rereading bucket info and checking that the expected current layout remains unchanged.

## Dependencies And Integration Points
The implementation depends on bucket index services (`svc()->bi`, `svc()->bi_rados`, `svc()->bilog_rados`), datalog service, zone service, `RGWRados` bucket info/index helpers, cls rgw client operations, cls lock client, Ceph config values, and `RadosStore`. It integrates with multisite sync through bilog history and datalog wakeup entries, and with fault injection through `ReshardFaultInjector` keys such as `init_index`, `set_target_layout`, `trim_reshard_log_entries`, `change_reshard_state`, `block_writes`, `commit_target_layout`, and `do_reshard`.

## Risks And Edge Cases
Resharding is sensitive to races with bucket metadata writes, expired locks, partial target index creation, and logrecord feature support. Errors during commit can leave writes unblocked but target metadata still present if cleanup also fails. Dynamic reduction deliberately waits and rechecks stats to avoid oscillation; changing config can drop queued reductions. Multisite buckets cannot reshard when retained log history is already too deep. `process_single_logshard()` ignores the return value of `process_entry()`, so one failing bucket does not stop the shard scan. Old bogus OLH entries with empty names are filtered during migration.

## Test Signals
Strong tests should cover prime shard selection, expansion and reduction thresholds, logrecord-supported and fallback block-reshard paths, injected failures at every state transition, retry behavior on `-ECANCELED`, cleanup of stale target layouts, lock renewal under long migrations, dynamic reduction wait logic, multisite bilog-history refusal, stale queue cleanup, and preservation of bucket stats and markers across source and target shards.
