# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/UfsFallbackBlockWriteHandlerTest.java

Purpose: concrete write-handler tests for fallback from a partially written local block to a UFS block file.

Important APIs and helpers: setup builds a real `MonoBlockStore`/`TieredBlockStore`, mocked `BlockWorker`, mocked `UnderFileSystem`, and an output stream. It pre-creates a partial local temp block of `PARTIAL_WRITTEN` bytes. Helpers create fallback init requests containing `CreateUfsBlockOptions`.

Control flow and state: `noTempBlockFound` removes the partial block before fallback and expects an error. `tempBlockWritten` starts fallback at the partial length, streams more data, completes, and verifies the combined output through the inherited checksum helper. `getLocation` asserts UFS block paths start under `/.alluxio_ufs_blocks`.

Dependencies and integration: depends on `UfsFallbackBlockWriteHandler`, `UfsManager`, `UnderFileSystem`, `MonoBlockStore`, block master worker ID, and abstract write-handler behavior.

Risks and test signals: strong for hybrid local/UFS recovery and offsets. It uses mocked UFS create behavior and a local in-memory stream, not a real remote object store.
