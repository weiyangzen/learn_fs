## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/UnderFileSystemBlockStore.java

### Purpose
`UnderFileSystemBlockStore` manages virtual UFS blocks opened by worker sessions. It tracks per-session/block UFS access state, creates UFS block readers, closes/releases those readers, cleans up sessions, and owns per-mount `UfsIOManager` instances for load operations.

### Important APIs and Types
- `acquireAccess(sessionId, blockId, OpenUfsBlockOptions)` creates a `UnderFileSystemBlockMeta` and stores `BlockInfo`.
- `createBlockReader(sessionId, blockId, offset, positionShort, options)` resolves UFS block paths, registers access, creates metrics, and creates `UnderFileSystemBlockReader`.
- `closeBlock` closes the reader inside `BlockInfo`.
- `releaseAccess` removes maps for a session/block.
- `cleanupSession` closes/releases all blocks for a session.
- `getOrAddUfsIOManager(long mountId)` lazily creates and starts per-mount UFS IO managers.
- `isNoCache` reads UFS block metadata flag.
- Inner `Key`, `BytesReadMetricKey`, and `BlockInfo` support map keys, metrics keys, and reader state.

### Control Flow
Access is registered under a `ReentrantLock` in both `mBlocks` and `mSessionIdToBlockIds`. Reader creation resolves fallback UFS block path when only `blockInUfsTier` is set, acquires access, retrieves `BlockInfo`, returns any still-open cached reader for that block/session, otherwise builds mount/user metrics and an `UnderFileSystemBlockReader`, then stores it in `BlockInfo`. Cleanup takes a snapshot-like reference to session block ids, then closes and releases each one; comments acknowledge a low-impact race.

### State and Persistence
State includes locked maps of active UFS blocks and session memberships, UFS read counters/meters, local store reference, UFS manager, per-mount IO manager map, and UFS input stream cache. It persists no block data directly; `UnderFileSystemBlockReader` may create local temp blocks through `LocalBlockStore`.

### Dependencies and Integration Points
Composed by `MonoBlockStore`; integrates with `UfsManager`, `UnderFileSystemBlockMeta`, `UnderFileSystemBlockReader`, `LocalBlockStore`, metrics, and session cleaner.

### Risks
- The lock protects maps only; `BlockInfo` reader state has its own synchronization. New code must preserve this split.
- `acquireAccess` rejects duplicate `(sessionId, blockId)` opens; clients opening multiple readers for the same pair can fail.
- `cleanupSession` iterates a set that can become stale after release; current behavior logs extra warnings rather than crashing.
- `BytesReadMetricKey.equals` calls `mUser.equals(that.mUser)`, which can throw if `mUser` is null despite null-user keys being possible.

### Test Signals
`UnderFileSystemBlockStoreTest` covers access acquisition/release, duplicate block handling, cleanup, reader creation, and no-cache state. `UnderFileSystemBlockReaderTest` covers reader-side behavior.
