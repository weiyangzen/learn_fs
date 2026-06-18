## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/LocalBlockStore.java

### Purpose
`LocalBlockStore` defines the contract for a local worker block store that owns block/temp-block metadata, local block files, block locks, allocation, movement, removal, access notifications, session cleanup, pin-list updates, and storage health handling.

### Important APIs and Types
- Creation and temp lifecycle: `createBlock`, `createBlockWriter`, `requestSpace`, `commitBlock`, `commitBlockLocked`, `abortBlock`.
- Reading and locking: `pinBlock`, `createBlockReader(session, block, offset)`, default UFS-aware overload.
- Mutation: `moveBlock`, `removeBlock`, `removeInaccessibleStorage`.
- Metadata: `getVolatileBlockMeta`, `getTempBlockMeta`, `getBlockStoreMeta`, `getBlockStoreMetaFull`, `hasBlockMeta`, `hasTempBlockMeta`.
- Events/session: `accessBlock`, `cleanupSession`, `registerBlockStoreEventListener`, `updatePinnedInodes`.

### Control Flow
This is an interface, but its documentation establishes the expected lifecycle: create temp metadata and temp path; write privately; request additional space as needed; commit to make visible; pin before reading committed blocks; move/remove under appropriate locks; cleanup sessions by unlocking and deleting temp data.

### State and Persistence
Implementations are expected to maintain local metadata and physical block/temp files. The interface extends `SessionCleanable` and `Closeable`.

### Dependencies and Integration Points
`TieredBlockStore` is the main implementation in this subset. `MonoBlockStore` composes it with UFS access, and `DefaultBlockWorker` exposes it through the higher-level `BlockStore` API.

### Risks
- `getVolatileBlockMeta` explicitly returns metadata without a lock guarantee, so callers must handle movement/removal races.
- The default UFS-aware reader throws `UnsupportedOperationException`; only higher layers/implementations that support fallback should call it.
- `commitBlockLocked` transfers lock ownership to the caller, making close discipline essential.

### Test Signals
All local store behavior is exercised through `TieredBlockStore` tests, `UnderFileSystemBlockReaderTest`, `MonoBlockStoreCommitBlockTest`, and grpc block read/write tests.
