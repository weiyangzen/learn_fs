# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/UfsFallbackBlockWriteHandler.java

## Purpose
`UfsFallbackBlockWriteHandler` writes a block to local worker storage when possible and falls back to writing the block into UFS when local space is exhausted or when the request is already a fallback from short-circuit write.

## Important APIs, Types, and Functions
`createRequestContext()` requires `CreateUfsBlockOptions`, initializes metrics, and optionally creates a local temp block. `writeBuf()` first delegates to `BlockWriteHandler`; on `ResourceExhaustedRuntimeException`, it flips to UFS mode, closes the local writer, creates the UFS block, transfers existing temp bytes with `Files.copy`, cancels local temp state, and writes remaining bytes to the UFS stream. `handleCommand()` supports fallback initialization with existing `bytesInBlockStore`. `completeRequest()` either commits local block or calls `commitBlockInUfs`. `cancelRequest()` aborts local or deletes the UFS file.

## Control Flow, State, and Persistence
The handler can transition mid-stream from local temporary block persistence to under-storage file persistence. In UFS mode it creates an atomic, parent-creating UFS output stream and records UFS-tagged metrics. Completion persists either an Alluxio local block or a UFS block-master record.

## Dependencies and Integration Points
It composes `BlockWriteHandler`, `DefaultBlockWorker`, `UfsManager`, `UnderFileSystem`, `BlockUtils.getUfsBlockPath`, `CreateOptions`, worker metrics, and protobuf `CreateUfsBlockOptions`.

## Risks and Test Signals
This is high-risk code because it mixes two persistence modes. Risks include partial transfer mismatch, output-stream/resource leaks, duplicate UFS creation, deleting the wrong UFS path on cancel, and position accounting when `bytesInBlockStore` is supplied. Tests should cover local success, local-to-UFS transition, short-circuit fallback initialization, cancel in both modes, flush in both modes, metrics switch, and transfer failure cleanup.
