# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_cluster.h

## Purpose
`rgw_dedup_cluster.h` declares the `rgw::dedup::cluster` coordinator used by RGW dedup workers to share a scan across multiple RGW processes. It provides token naming, epoch reset, token acquisition, token completion, heartbeat updates, statistics collection, and admin control notify helpers.

## Important APIs, Types, And Functions
`WORKER_SHARD_PREFIX` and `MD5_SHARD_PREFIX` identify the two token namespaces. `cluster::shard_token_oid` constructs legal token object names by appending a three-digit hex shard id to a prefix and validates token names during cleanup.

The constructor takes a `DoutPrefixProvider`, `CephContext`, and SAL driver and generates local lock and cluster identifiers. `reset()` prepares the coordinator for a run. `get_next_work_shard_token()` and `get_next_md5_shard_token()` return the next lockable shard or null sentinel values. `mark_work_shard_token_completed()` and `mark_md5_shard_token_completed()` encode shard stats, update local completion caches, and persist completion.

Static APIs support admin and watcher integration: `collect_all_shard_stats()`, `watch_reload()`, `unwatch_reload()`, `ack_notify()`, `dedup_control_bl()`, `dedup_control()`, and `dedup_restart_scan()`.

## Control Flow
The background service calls `reset()` at scan setup, then repeatedly asks for work shard tokens during bucket ingress. After work shards complete, MD5 shard processors use the same token pattern. Completion checks use `all_work_shard_tokens_completed()` and `all_md5_shard_tokens_completed()`, which delegate to a common private checker.

Admin commands use static functions and do not require a live `cluster` instance. They open the control pool, notify `DEDUP_WATCH_OBJ`, decode acknowledgements, or update the epoch before restart.

## State And Persistence Behavior
The class caches current worker and MD5 shard cursors, epoch time, token creation time, and per-shard completion arrays. Persistent state is stored outside the class in RADOS control-pool objects and xattrs. Completion states in `d_completed_workers` and `d_completed_md5` are local caches of persisted xattr states.

## Dependencies And Integration Points
The class depends on `rgw_dedup_utils.h` for shard and stats types, `rgw_dedup_store.h` for record/block identifiers, `rgw_dedup_filter.h` for restart filtering, RADOS watch contexts, SAL RadosStore, optional yields, and Ceph formatters.

## Risks And Edge Cases
`shard_token_oid` has a fixed 16-byte buffer and prefixes are close to the limit; changes to prefixes must preserve the length invariant. The public completion helpers increment local completed counts before persisting the completed xattr, so caller behavior after a failed persist must be reviewed carefully.

## Test Signals
Unit-level tests should validate token object formatting and bounds, local completion-array transitions, null shard returns, and restart filter serialization. Integration tests should run multiple simulated workers contending for tokens.
