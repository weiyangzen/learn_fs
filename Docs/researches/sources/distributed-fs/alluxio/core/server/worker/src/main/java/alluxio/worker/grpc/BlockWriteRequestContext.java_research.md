# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/BlockWriteRequestContext.java

## Purpose
`BlockWriteRequestContext` extends the generic write context with block-write-specific resources: the local `BlockWriter`, reserved-space accounting, local-vs-UFS fallback mode, UFS resource/output stream, and UFS path.

## Important APIs, Types, and Functions
The constructor wraps a gRPC `WriteRequest` as `BlockWriteRequest` and records initial bytes reserved. Accessors/mutators manage `BlockWriter`, `mBytesReserved`, `mIsWritingToLocal`, `mUfsResource`, `mOutputStream`, and `mUfsPath`.

## Control Flow, State, and Persistence
For normal local writes, `mBlockWriter` and `mBytesReserved` drive append and reservation state. For fallback writes, `mIsWritingToLocal` flips false and UFS fields hold the open under-storage resource and target output stream. The class itself persists nothing; handlers close, commit, abort, or delete resources.

## Dependencies and Integration Points
It is shared by `BlockWriteHandler` and `UfsFallbackBlockWriteHandler`, and relies on `WriteRequestContext`, `BlockWriter`, `CloseableResource<UnderFileSystem>`, and `OutputStream`.

## Risks and Test Signals
The context is `@NotThreadSafe`, so the owning `AbstractWriteHandler` lock must protect cross-thread state. Fallback mode transitions are subtle because local writer cleanup and UFS output creation can both be active during a switch. Tests should cover fallback after partial local write, fallback from short-circuit with bytes already in block store, cancel cleanup, and resource-close ordering.
