# sources/cloud-native/nydus/storage/src/remote/client.rs

## Purpose
Implements the client-side proxy for a remote blob manager: it connects over a Unix socket control plane, receives blob file descriptors, tracks generation tokens, and asks the server to materialize uncompressed ranges into the shared data plane file.

## Important APIs, Types, And Functions
`RemoteBlobMgr` is the public manager with `new()`, `connect()`, `start()`, `shutdown()`, `ping()`, and `get_blob_object()`. `RemoteBlobs` caches active `RemoteBlob`s and maintains a generation counter. `RemoteBlob` implements `BlobObject` using a received `File`, base offset, token, and `BlobRangeMap`. `Request`, `RequestStatus`, and `RequestResult` model synchronous request/reply waiting. `ServerConnection` owns the socket endpoint, request map, reconnect logic, and handlers for `GetBlob` and `FetchRange` replies.

## Control Flow
A caller creates and starts `RemoteBlobMgr`; `ServerConnection::start()` spawns a reply thread that waits for a connection and dispatches replies by tag. `get_blob_object()` reuses cached blobs or sends `GetBlob`, then constructs a `RemoteBlob` with a range map in the workdir. `fetch_range_uncompressed()` checks local range readiness and sends `FetchRange` if needed. Requests wait on condvars with a four-second timeout and retry when reconnect/generation mismatch is observed.

## State And Persistence
Persistent/cache state is the `BlobRangeMap` file under `workdir/<blob_id>`, which tracks uncompressed range readiness at 256 KiB granularity. Runtime state includes active blob cache, generation counter, per-blob token, request tags, pending request map, socket endpoint, and a shared file descriptor from the remote manager.

## Dependencies And Integration Points
Uses `remote::connection::Endpoint` for Unix-socket messages and fd passing, `remote::message` wire types, `BlobInfo`, `BlobObject`, `BlobIoRange`, `BlobRangeMap`, `nix::select`, and `vm_memory::ByteValued`. It is the bridge between remote control messages and higher-level blob IO.

## Risks
`call_fetch_range()` constructs a `FetchRangeRequest` but sets the header body size to `size_of::<GetBlobRequest>()`, which is a protocol-risk bug if the sizes differ. On non-success fetch replies, it returns `from_raw_os_error(count as i32)` instead of the result code, likely masking server errors. `reopen_blob()` updates only the token and ignores the new file/base, so reconnection assumes the original fd remains usable. The reply thread ignores `handle_reply()` errors and loops, relying on reconnect paths for recovery.

## Test Signals
The local unit test covers `Request` timeout, reconnect, and finished transitions. There are no direct tests for socket protocol exchange, generation mismatch, range-map persistence, or fetch-range error mapping in this file. Source size reviewed: 771 lines.
