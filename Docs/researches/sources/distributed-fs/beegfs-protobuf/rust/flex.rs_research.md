# Research: sources/distributed-fs/beegfs-protobuf/rust/flex.rs

## Purpose

`flex.rs` is generated Rust code for the BeeRemote/Flex worker-node protobuf service and shared work model. It defines worker heartbeats, work submission and cancellation, configuration updates, remote storage target definitions, job/work payloads, capability reporting, and tonic client/server bindings.

## Important APIs, Types, and Functions

Operational RPC messages include `HeartbeatRequest/Response`, `SubmitWorkRequest/Response`, `UpdateWorkRequest/Response`, `BulkUpdateWorkRequest/Response`, `UpdateConfigRequest/Response`, and `GetCapabilitiesRequest/Response`. `WorkerNodeClient` exposes async unary calls for `update_config`, `heartbeat`, `submit_work`, `update_work`, `bulk_update_work`, and `get_capabilities`; `worker_node_server::WorkerNode` is the trait to implement on worker services.

Core data models include `JobLockedInfo`, `JobRequestCfg`, `WorkRequest`, `BuilderJob`, `MockJob`, `SyncJob`, `Work`, `RemoteStorageTarget`, `BeeRemoteNode`, `Feature`, and `BuildInfo`. `WorkRequest` identifies a job/request, external id, path, optional segment, remote storage target id, stub/priority flags, and oneof work type (`MockJob`, `SyncJob`, `BuilderJob`). `Work` reports worker-side status and per-part results, including offsets, entity tags, SHA-256 checksums, and completion flags.

`RemoteStorageTarget` uses a oneof for S3, POSIX, Azure, or mock backends. S3 configuration includes endpoint, partition, region, bucket, credentials, and storage classes with archival restore settings. `UpdateConfigRequest` replaces worker configuration by sending BeeRemote connection information and the full set of RSTs that should remain configured.

## Control Flow and State Behavior

Generated client methods wait for tonic readiness and issue unary RPCs. Generated server dispatch matches fixed paths under `flex.WorkerNode` and forwards requests to an implementor. Business control flow is described by message comments: BeeRemote submits work, worker nodes accept and execute it, workers update status, and BeeRemote may cancel or bulk-update work during node initialization or draining.

The state model is explicit in enums. `work::State` covers `UNKNOWN`, `CREATED`, `SCHEDULED`, `RUNNING`, `RESCHEDULED`, `ERROR`, `FAILED`, `CANCELLED`, and `COMPLETED`. Terminal states imply the worker should no longer retain or act on the request after reporting it. `HeartbeatResponse` can include readiness and active request stats. `UpdateConfigRequest` is replace-all for RSTs: omitted targets should be deleted.

## Dependencies and Integration Points

This module depends on tonic/prost/prost-types and is heavily referenced by `beeremote.rs`. It is the integration boundary between BeeRemote and worker nodes such as BeeSync. It also bridges to external systems through RST backends: S3-compatible object stores, Azure modeled through S3-compatible details plus account, POSIX paths, and test/mock targets.

## Risks and Edge Cases

The generated API does not validate backend compatibility, credentials, RST id references, segment ranges, part ranges, checksum formats, archival restore timing strings, or whether a worker actually supports a submitted work type. Comments state that callers must ensure job type and RST compatibility. `UpdateConfigRequest` deleting omitted RSTs is powerful and risky if a partial config is sent accidentally. Secrets and TLS controls are plain fields, so logging and serialization hygiene matter. Unknown state handling is necessary when BeeRemote cannot contact workers.

## Test Signals

Tests should cover worker service contract calls, heartbeat readiness/stat reporting, config replace/delete semantics, RST oneof round trips, S3 archival settings validation in higher-level code, work state transitions, cancellation/bulk-update behavior, segment and part boundary validation, checksum/ETag propagation, and capability-map compatibility across versions.
