# sources/distributed-fs/ceph/src/rgw/rgw_bucket_sync.h

Purpose: declares bucket sync policy mapping and query types for RGW multisite bucket-level synchronization.

Important APIs/types/functions: `rgw_sync_group_pipe_map`, `RGWSyncPolicyCompat`, `RGWBucketSyncFlowManager` with nested `endpoints_pair`, `pipe_rules`, `pipe_handler`, and `pipe_set`, `RGWBucketSyncPolicyHandler`, `rgw_bucket_sync_pair_info`, and `rgw_bucket_sync_pipe`.

Control flow: declarations model two levels: flow manager resolves raw policy flow groups into pipe sets, and policy handler owns zone/bucket context and exposes source/target pipe queries. `pipe_handler` delegates object parameter lookup to shared `pipe_rules`.

State/persistence: in-memory policy resolution state includes group maps, source/target pipes by zone, zone sets, source/target bucket hints, and resolved hints. `rgw_bucket_sync_pipe` bundles resolved source/destination bucket info and attrs for downstream sync.

Dependencies/integration: includes `rgw_common`, sync policy definitions, zone metadata, service forward declarations, `RGWBucketInfo`, object tags, bucket shard types, and buffer attrs.

Risks: many getters return mutable or raw pointers/references to internal containers, so lifetime is tied to the handler. Child handlers point at parent handlers and parent flow managers. `bucket_exports_data()` assumes `bucket_info` is present when needed.

Test signals: construction of root and child handlers, lifetime of shared rule refs, pipe-set insert/disable, source/dest query aggregation including resolved hints, and object filter matching.
