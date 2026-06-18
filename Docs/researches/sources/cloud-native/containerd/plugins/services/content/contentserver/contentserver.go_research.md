# sources/cloud-native/containerd/plugins/services/content/contentserver/contentserver.go

## Purpose
Implements the gRPC content service over a containerd content store, including info/update/list/delete/read/write/status/abort operations.

## Important APIs, Types, And Functions
`service` holds a `content.Store`. `New` returns an API server. Methods include `Info`, `Update`, `List`, `Delete`, `Read`, `Status`, `ListStatuses`, `Write`, and `Abort`. `readResponseWriter`, `infoToGRPC`, and `infoFromGRPC` handle streaming and conversion. `bufPool` reuses 1 MiB buffers.

## Control Flow
Read validates digest, bounds offset/size, opens a reader, and streams chunks through `readResponseWriter`. Write receives an initial ref message, opens a content writer, loops over stat/write/commit actions, validates offsets, truncates when restarting at zero, detects existing expected digests, writes data, commits with labels on commit, and sends status responses. List batches content info in groups of 100.

## State And Persistence
Persists content blobs, ingest status, and labels through the content store. Write may abort ingests on duplicate expected digest. Read/list/status are read-only.

## Dependencies And Integration Points
Used by the content gRPC plugin. Depends on content store APIs, OCI descriptors, digest parsing, errgrpc, protobuf timestamps, and gRPC streaming.

## Risks
Streaming write protocol is stateful and sensitive to offset mismatches. Duplicate expected digest aborts the current ref. Final defer attempts to send the last message only on success. Buffer reuse must not retain mutable response data beyond send semantics.

## Test Signals
No direct tests in this subset; content service integration tests cover protocol behavior.
