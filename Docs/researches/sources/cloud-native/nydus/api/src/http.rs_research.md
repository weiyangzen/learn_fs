# sources/cloud-native/nydus/api/src/http.rs

## Purpose
This module defines the typed request, response, command, and error vocabulary shared between Nydus HTTP handlers and backend API services.

## Important APIs, Types, and Functions
- Command structs: `ApiMountCmd`, `ApiUmountCmd`, `DaemonConf`, `BlobCacheObjectId`, and `Config` alias.
- `ApiRequest` enumerates daemon control, mount/remount/umount, metrics, v1 config/filesystem queries, and v2 blob object operations.
- Error types include `MetricsError`, `DaemonErrorKind`, `MetricsErrorKind`, `ApiError`, and `HttpError`.
- `ApiResponsePayload` enumerates string JSON payload categories, empty responses, config maps, and v2 blob object lists.
- `ApiResult<T>` and `ApiResponse` are result aliases.
- `ErrorMessage` serializes API error codes/messages and converts into a JSON byte vector.

## Control Flow
HTTP endpoint handlers parse requests into `ApiRequest` variants and send them through an API service channel or callback. Backend services return `ApiResponsePayload` or `ApiError`; HTTP handler code maps `ApiError` into `HttpError` variants and status codes. `ErrorMessage` is serialized when producing client-facing error bodies.

## State and Persistence
The module itself has no mutable state. It defines data that can cause daemon state changes when interpreted by the service: mount operations, daemon start/exit/config, blob object create/delete, and config updates.

## Dependencies and Integration Points
It depends on serde, thiserror, channel send/recv errors, serde_json errors, and `BlobCacheEntry` from the config module. It is the central integration contract between OpenAPI documents, `http_endpoint_common.rs`, other endpoint modules, and daemon/service implementations.

## Risks and Edge Cases
`HttpError` debug formatting is noted as implicitly part of the API, so renaming variants can be a breaking change. Many payloads are raw `String` rather than strongly typed schemas, making mismatches with OpenAPI easier. `ApiMountCmd.prefetch_files` is `Option<Vec<String>>`, while the v1 OpenAPI document describes a string. Boxed send errors reduce enum size but can complicate matching.

## Test Signals
No tests are in this file. It is indirectly tested through endpoint handler tests, service tests, OpenAPI compatibility, and smoke workflows that exercise HTTP API operations.
