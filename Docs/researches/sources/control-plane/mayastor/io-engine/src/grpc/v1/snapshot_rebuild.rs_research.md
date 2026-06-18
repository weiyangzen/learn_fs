# sources/control-plane/mayastor/io-engine/src/grpc/v1/snapshot_rebuild.rs

Purpose: this v1 service exposes snapshot rebuild job lifecycle and status APIs. It creates jobs that rebuild a replica from a snapshot, lists active jobs, and destroys/stops jobs.

Important APIs/types/functions: `SnapshotRebuildService` stores a `ReplicaService` clone but currently does not lock through it. `create_snapshot_rebuild`, `list_snapshot_rebuild`, and `destroy_snapshot_rebuild` implement the generated RPC trait. `SnapRebuild` pairs an `Arc<SnapshotRebuildJob>` with current `RebuildStats`. Conversion impls map `SnapRebuild` to protobuf, `RebuildState` to rebuild status, and `RebuildError` to tonic statuses.

Control flow: create rejects bitmap requests, returns an existing job idempotently if present, otherwise builds/stores a job, looks it up, starts it, and returns status. List either returns all jobs or looks up a single job keyed by `replica_uuid` field. Destroy looks up a job, force-stops it through either async channel or immediate result, logs the outcome, destroys the job, and returns empty success.

State and persistence: mutates in-memory snapshot rebuild job registry and calls `store()` on creation. It reports stats-derived byte totals and timestamps but has fixed `persisted_checkpoint = 0` and `target_remote = false`.

Dependencies and integration points: integrates `SnapshotRebuildJob`, `RebuildStats`, `RebuildError`, `SnapshotRebuildError`, `spdk_submit!`, and v1 snapshot-rebuild protobufs.

Risks: list filtering uses `replica_uuid` as a lookup key even though create/destroy use job UUID, which may confuse clients; no explicit service/resource locking; bitmap unsupported; persisted checkpoint is not implemented. Test signals should cover idempotent create, bitmap rejection, destroy of running/stopped/missing jobs, byte conversions, state mapping, and lookup semantics.
