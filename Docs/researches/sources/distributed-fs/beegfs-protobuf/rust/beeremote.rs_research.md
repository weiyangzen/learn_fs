# Research: sources/distributed-fs/beegfs-protobuf/rust/beeremote.rs

## Purpose

`beeremote.rs` is generated Rust code for the BeeRemote protobuf service. It defines messages and tonic client/server bindings for externally facing BeeRemote RPCs used by clients and worker nodes to submit, query, update, and report distributed remote-storage jobs. The file is generated, but its comments document the intended job lifecycle and persistence model.

## Important APIs, Types, and Functions

Core request/result types are `SubmitJobRequest`, `SubmitJobResponse`, `JobRequest`, `Job`, `JobResult`, `UpdateJobsRequest`, `UpdateJobsResponse`, `GetJobsRequest`, `GetJobsResponse`, `UpdateWorkRequest`, `GetRstConfigResponse`, and `GetStubContentsResponse`. `JobRequest` identifies a path, optional name, priority, remote storage target id, force/stub flags, generation status, update flag, and a oneof job type: `flex::SyncJob`, `flex::MockJob`, or `flex::BuilderJob`.

`Job` adds persistent job id, created timestamp, status, external id, and start/stop mtimes. `JobResult` combines a `Job` with generated `flex::WorkRequest` entries and latest worker `WorkResult` summaries. `UpdateJobsRequest` supports path/job/RST filtering and a `NewState` enum currently centered on cancel/delete operations. `GetJobsRequest` supports oneof query modes by job id plus path, exact path, or path prefix.

The generated `bee_remote_client::BeeRemoteClient` provides async methods for `submit_job`, `update_paths`, `update_jobs`, `get_jobs`, `update_work`, `get_rst_config`, `get_stub_contents`, and `get_capabilities`. The generated `bee_remote_server::BeeRemote` trait is the implementation surface for servers, with streaming associated types for `UpdatePaths` and `GetJobs`.

## Control Flow and State Behavior

Client methods wait for inner tonic readiness, create a prost codec, attach a `GrpcMethod` extension, and call unary or server-streaming RPCs by fixed path. Server dispatch matches the HTTP/2 gRPC path and wraps implementor methods in unary or streaming service adapters. Unknown paths return gRPC `Unimplemented`.

The file itself does not persist data, but comments state the intended persistence split: `Job` records are stored separately from work results, and jobs are looked up by path or id in key/value stores. Job status transitions include `UNASSIGNED`, `SCHEDULED`, `RUNNING`, `ERROR`, `FAILED`, `CANCELLED`, `COMPLETED`, and `OFFLOADED`. Start/stop mtimes support detection of local file changes across a synchronization job, but consumers must also inspect job state.

## Dependencies and Integration Points

This module depends on `tonic`, `tonic_prost`, `prost`, `prost_types::Timestamp`, `http`, `bytes`, and generated `flex` types. It integrates with BeeRemote servers, CLI/UI clients, BeeSync or other worker nodes, and remote storage target configuration providers. `GetCapabilities` reuses the `flex` capability model.

## Risks and Edge Cases

Generated structs permit absent optional fields that service logic may require. Job and work status messages can grow if callers concatenate history without bounds; comments explicitly warn against retaining all retry history. Streaming `UpdatePaths` and `GetJobs` can return many rows and require client stream handling. `UpdateWork` is intended only for worker nodes, but the generated API does not enforce caller identity. Force-update and force-submit flags can bypass normal completed-job protections, so server-side validation is critical.

## Test Signals

Useful tests include tonic client/server contract tests for unary and streaming calls, status transition tests, query filtering tests over job/path/RST indexes, authorization tests for worker-only `UpdateWork`, and persistence round trips that confirm jobs, work requests, and work results can be reconstructed without embedding large result payloads into every job record.
