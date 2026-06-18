# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/stream/BlockWorkerDataReaderTest.java

Purpose: integration-style unit tests for client-side `BlockWorkerDataReader` backed by a local `DefaultBlockWorker`, including local-block reads and UFS fallback reads.

Important APIs and helpers: setup builds a one-tier worker store, mocked block/master/session clients, a real local UFS manager, and `BlockWorkerDataReader.Factory`. Tests cover missing-block create failures, reader creation at an offset, repeated create/close for lock release, UFS chunk reads, full local file reads, and partial reads.

Control flow and state: local tests create and commit blocks through `mBlockWorker`, append increasing-byte buffers through `BlockWriter`, then read chunks and validate position. UFS tests write a real temp file, construct persisted `URIStatus`/`FileBlockInfo`, use `ReadPType.NO_CACHE`, and read through `Paged`/worker UFS path.

Dependencies and integration: depends on worker block store, `MonoBlockStore`, `TieredBlockStore`, `UnderFileSystem`, `InStreamOptions`, `FileSystemContext`, and `BufferUtils`.

Risks and test signals: strong signal for reader lifecycle, chunk sizing, offsets, and lock churn. It depends on global modifiable configuration and real temp filesystem behavior, but not a live master.
