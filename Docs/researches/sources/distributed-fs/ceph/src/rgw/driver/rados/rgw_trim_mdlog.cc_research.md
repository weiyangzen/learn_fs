# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_mdlog.cc

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_mdlog.cc` implements metadata-log trimming for RGW multisite. It handles both metadata master and peer zones, purges obsolete period logs, trims current-period mdlog shards only when safe for peer sync progress, and coordinates trim work with RADOS locks.

## Important APIs, Types, and Functions

`PurgeLogShardsCR` removes all shards for one mdlog period. `PurgePeriodLogsCR` walks mdlog period history and removes old period logs before updating the oldest-log-period cursor. `make_peer_connections()` builds REST connections for realm zones. `get_stable_marker()`, `operator<`, and `take_min_status()` calculate safe master-side trim status. `TrimEnv`, `MasterTrimEnv`, and `PeerTrimEnv` carry shared state. `MetaMasterStatusCollectCR` fetches peer metadata sync status. `MetaMasterTrimShardCollectCR` trims master mdlog shards by marker. `MetaPeerTrimShardCR` derives safe peer trim timestamps from the master's first mdlog entries. `MetaPeerTrimShardCollectCR`, `MetaMasterTrimCR`, and `MetaPeerTrimCR` coordinate master/peer flows. `MetaTrimPollCR` handles periodic lock/sleep/unlock-on-error behavior. Factory functions create periodic or admin trim coroutines.

## Control Flow

Periodic trim sleeps, locks `RGWMetadataLogHistory::oid` with lock name `meta_trim`, and runs either master or peer trim depending on `is_meta_master()`. Master trim fetches metadata sync status from all peer zones, computes the minimum realm epoch and per-shard markers, purges older period logs if peers advanced, and trims current-period shards when the minimum epoch equals the current epoch. Peer trim fetches mdlog info from the master, adopts the master's shard count, purges old period logs if the master advanced, and for current-period shards reads the master's first entry or shard info to compute a safe timestamp before trimming local mdlog entries older than that.

## State and Persistence Behavior

The code deletes mdlog shard objects from the zone log pool, updates mdlog history/oldest-log-period metadata through `svc_mdlog`, and trims timelog entries. In-memory state tracks last purged epoch, last current-period master trim markers, and last peer trim timestamps. Locks are RADOS objects in the log pool. No independent trim status object is introduced here.

## Dependencies and Integration Points

Dependencies include RGW sync types, metadata log service, zone service and period history, cls/log trim coroutines, REST admin log status endpoints, master connection helpers, RADOS lock/remove/timelog trim coroutines, and RGWHTTPManager. The implementation is tightly coupled to realm period history and multisite metadata sync status.

## Risks and Edge Cases

Endpoint sanity checks refuse trimming if any zone has no endpoint, because peer status/master reads would be unsafe. Master trim requires all peer status responses and matching shard counts. Peer timestamp trimming subtracts one second from the master's first entry timestamp, which is conservative but depends on timestamp ordering. Purging period logs races with other gateways; `-ENOENT` is treated as a successful race. Periodic trim intentionally keeps the lock after success but unlocks on errors so another gateway can try.

## Test Signals

Important tests include endpoint sanity checks, peer connection construction, minimum status calculation across epochs and markers, shard-count mismatch, period purge races, master current-period marker trims, peer empty/non-empty master shard timestamp derivation, old period purge on master/peer, lock contention and unlock-on-error, and factory selection for master versus peer zones.
