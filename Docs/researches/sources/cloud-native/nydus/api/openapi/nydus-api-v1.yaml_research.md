# sources/cloud-native/nydus/api/openapi/nydus-api-v1.yaml

## Purpose
This OpenAPI 3.0.2 document describes the public Nydus v1 HTTP management API under `http://localhost/api/v1`.

## Important APIs, Types, and Functions
Endpoints include `/daemon` GET/PUT, `/daemon/events`, `/daemon/backend`, `/daemon/exit`, `/mount` POST/PUT/DELETE, `/metrics`, `/metrics/files`, `/metrics/pattern`, `/metrics/backend`, `/metrics/blobcache`, and `/metrics/inflight`. Schemas include `DaemonInfo`, `DaemonConf`, `DaemonFsBackend`, `MountCmd`, `ErrorMsg`, `RafsMetrics`, `RafsFilesMetrics`, `RafsLatestReadFiles`, `RafsFilesAccessPatterns`, `RafsBackend`, `Blobcache`, `FuseInflight`, and `Events`.

## Control Flow
Clients issue JSON HTTP requests to daemon endpoints. Mutating operations such as configure, exit, mount, remount, and unmount return `204` on success. Read operations return JSON schemas or error messages. Query parameters select mountpoint or optional filesystem id.

## State and Persistence
The API exposes and mutates daemon runtime state: log level, daemon lifecycle, mounts, backend configuration, metrics, file access state, and inflight requests. It does not itself define persistence semantics.

## Dependencies and Integration Points
The contract maps to Rust types in `api/src/http.rs` and endpoint handlers in `api/src/http_endpoint_common.rs` plus other handler modules outside this subset. It is used by clients, docs, and compatibility checks.

## Risks and Edge Cases
Some schema details are loose: many metric payloads are generic objects or string/integer arrays, `MountCmd.prefetch_files` is documented as string while Rust uses `Option<Vec<String>>`, and many failures are represented as `500` even for bad input. Drift between this file and handler behavior is a compatibility risk.

## Test Signals
Tests should compare OpenAPI operations with registered HTTP routes and Rust request/response types. Existing endpoint unit tests cover some method/query behavior but do not validate the OpenAPI file directly.
