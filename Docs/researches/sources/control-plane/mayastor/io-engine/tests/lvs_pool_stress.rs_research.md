# sources/control-plane/mayastor/io-engine/tests/lvs_pool_stress.rs

Purpose: performance/regression tests for listing large numbers of LVS replicas and snapshots, including conversion to API protobufs and gRPC list latency.

Important APIs/types/functions: `ms` starts Mayastor with gRPC/device monitor and NVMe max namespaces. `lvol_list` creates nearly 8000 thin replicas, converts them to `io_engine_api::v1::replica::Replica`, shares all over NVMf, repeats conversion, and calls `ReplicaRpcClient::list_replicas`. `lvol_snap_list` creates 1024 replicas, 256 snapshots and clones for the first 10, then uses `Lvol::list_all_snapshots`.

Control flow: create large pool with metadata max expansion, populate replicas/snapshots, measure list loops with `Instant`, assert duration thresholds, and destroy all pools.

State and persistence: in-memory malloc-backed LVS pool but with LVS metadata for many lvols/snapshots/clones. gRPC state is served from the Mayastor instance.

Dependencies and integration points: LVS iteration, NVMf share URI lookup, replica protobuf conversion, gRPC server/client, snapshot/clone metadata, chrono timestamps.

Risks and edge cases: time thresholds are performance-sensitive and may fail on heavily loaded systems. Large object counts stress memory and namespace limits. The test sets `RUST_LOG=error` globally.

Test signals: protects against O(n^2) or expensive subsystem lookups during list operations and snapshot enumeration.
