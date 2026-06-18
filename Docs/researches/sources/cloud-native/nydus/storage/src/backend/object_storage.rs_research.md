# sources/cloud-native/nydus/storage/src/backend/object_storage.rs

## Purpose
This module is the generic object-storage backend foundation used by OSS and S3-like implementations. It separates provider-specific URL/signing state from common blob read, size, stream, metrics, and shutdown behavior.

## Important APIs, Types, and Functions
`ObjectStorageState` requires `url`, `sign`, and `retry_limit`. `ObjectStorage<T>` is the backend wrapper over `request::Request`, provider state, metrics, and optional ID. `ObjectStorageReader<T>` implements `BlobReader`. `ObjectStorageError` covers auth/signing, header construction, transport, and response validation errors. `new_object_storage` wires request, state, metrics, and ID into the generic backend.

## Control Flow
`blob_size` signs and sends a HEAD request, then parses `Content-Length`. `try_read_ctx` builds a closed byte range, signs GET, calls the request layer with the provided context, and copies the response body to the caller buffer. `try_stream_read` signs GET and omits `Range` at offset `0` so Dragonfly can cache the full blob; for nonzero offsets it sends an open-ended range. `get_reader` requires metrics to exist and returns unsupported otherwise.

## State and Persistence Behavior
The backend does not cache object data. It stores shared request/client state, immutable provider state, optional metrics, and reader-local blob IDs. Persistent data lives in the remote object store, while request retries and proxy behavior are delegated to the request/connection layers.

## Dependencies and Integration Points
This module depends on `reqwest` headers/methods, common backend traits, `request.rs`, and provider states such as `OssState`. It is where object-storage providers inherit Dragonfly proxy behavior, exact-read enforcement, and metrics.

## Risks
`try_read_ctx` computes `offset + buf.len() as u64 - 1`, which underflows for zero-length buffers and can overflow for extreme offsets. `blob_size` requires `Content-Length`; chunked or metadata-poor providers fail. `get_reader` fails when constructed without metrics, while constructors allow `id: None`. Stream status checking is probably redundant when `catch_status` is true but remains defensive.

## Test Signals
Tests use a mock `ObjectStorageState` and local TCP server to cover error formatting, backend lifecycle, missing metrics, retry limit propagation, HEAD size reads, missing content length, ranged reads, signing failures, and stream reads with and without Range headers.
