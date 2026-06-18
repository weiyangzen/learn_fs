<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/snapshot.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/snapshot.rs

Purpose: v1 gRPC builders for replica snapshots and snapshot clones in tests.

Important APIs/types: `ReplicaSnapshotBuilder` stores RPC handle, replica UUID, snapshot UUID/name, entity ID, and txn ID. It can generate a snapshot UUID, create a replica snapshot, and filter listed snapshots by source replica. `SnapshotCloneBuilder` stores RPC handle, snapshot UUID, clone name, and clone UUID. It creates snapshot clones and filters listed clone replicas by snapshot UUID. Free functions `list_snapshot` and `list_snapshot_clone` expose unfiltered RPC list calls.

Control flow: builders lock the shared RPC handle and call generated snapshot service methods. Filtering is done client-side after listing all objects.

State and dependencies: mutates snapshot and clone state in io-engine. Depends on `io_engine_api::v1::snapshot` and tonic status.

Risks and test signals: required fields use `expect`/`unwrap`, so incomplete setup panics. `with_snapshot_uuid()` always generates a UUID and accepts no input, unlike clone UUID setter. Healthy tests assert create responses and list filters contain the new snapshot/clone.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/snapshot.rs -->
