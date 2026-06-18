# sources/control-plane/mayastor/io-engine/src/grpc/v1/snapshot.rs

Purpose: this v1 service implements nexus snapshots, replica snapshots, snapshot listing/deletion, clone creation, and clone listing. It reuses `ReplicaService` locks for replica-backed operations and nexus resource locks for nexus-wide snapshots.

Important APIs/types/functions: `SnapshotService` delegates `RWSerializer` to `replica_svc` and has its own `serialized` helper for protected nexus locks. Conversions map nexus snapshot descriptors/statuses, `SnapshotDescriptor` to `SnapshotInfo`, list requests to backend args, and clone requests to list args. `ReplicaGrpc::create_snapshot` prepares replica snapshot config, checks UUID collision, creates the snapshot, and returns descriptor info. `SnapshotGrpc` finds snapshots across factories and verifies pool ownership.

Control flow: `create_nexus_snapshot` locks the nexus, builds `SnapshotParams`, converts requested replica descriptors, calls `nexus.create_snapshot`, and returns done/skipped statuses plus timestamp. Replica snapshot and list/destroy/clone paths run through `spdk_submit!` under replica shared/exclusive locks. Clone creation rejects duplicate clone UUIDs and discarded snapshots before preparing clone config.

State and persistence: creates snapshot lvol metadata, snapshot xattrs/config, clone lvols, and nexus snapshot coordination state. `SNAPSHOT_READY_AS_SOURCE` is currently false in responses.

Dependencies and integration points: integrates internal snapshot traits, `ReplicaFactory`, `GrpcReplicaFactory`, `PoolGrpc`, `nexus_lookup`, `ResourceLockManager`, `UntypedBdev`, and v1 snapshot/replica protobufs.

Risks: `filter_snapshots_by_snapshot_query_type` appears to match `query.invalid` against `valid_snapshot`, which is easy to misread and may be semantically wrong; timestamp parsing defaults silently; snapshot UUID collision only checks bdev UUID globally; list suppresses backend errors. Test signals should cover query filtering, duplicate snapshot/clone UUIDs, discarded snapshot clone rejection, pool verification, nexus lock timeout, skipped replica status mapping, and timestamp/reference-byte fields.
