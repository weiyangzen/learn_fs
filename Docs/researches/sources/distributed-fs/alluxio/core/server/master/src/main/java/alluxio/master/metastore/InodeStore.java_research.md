# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/InodeStore.java

## Purpose
`InodeStore` defines the mutable metadata store contract for filesystem inodes and parent-child edges. It extends read-only access with write, remove, checkpoint, and optional batch-write APIs.

## Important APIs and Types
- Extends `ReadOnlyInodeStore`, `Checkpointed`, and `Closeable`.
- `getMutable(long, ReadOption)` returns mutable inode metadata; default `get` wraps it as immutable `Inode`.
- `remove`, `writeInode`, `writeNewInode`, `clear` mutate inode entries.
- `addChild` and `removeChild` mutate parent-child edge entries.
- `supportsBatchWrite`/`createWriteBatch` expose optional batched writes.
- `getInodePathString` traverses parent links for corruption diagnostics.
- Nested `WriteBatch` supports inode and edge operations plus `commit`.
- Nested `Factory` maps an `InodeLockManager` to an `InodeStore`.

## Control Flow
The interface documents required external locking: inode mutations require inode locks and edge mutations require edge locks. Default methods implement convenience wrappers, combined inode-and-edge removal, and debug parent traversal capped at 100 iterations.

## State and Persistence
Actual state is implementation-specific. Checkpointing is required by the interface. Write batches may or may not be atomic depending on the implementation.

## Dependencies and Integration Points
Core dependency for `InodeTree`/file master metadata. Integrates with `InodeLockManager`, `MutableInode`, `InodeView`, `Checkpointed`, and read-only traversal APIs.

## Risks and Edge Cases
- Violating the external lock contract can race with asynchronous cache flush or concurrent store updates.
- `writeInode` semantics are implementation-dependent; the heap implementation currently uses `putIfAbsent`, while Rocks overwrites.
- `removeInodeAndParentEdge` is not atomic unless the implementation/caller provides atomicity.
- Batch write atomicity is explicitly not guaranteed by the interface.

## Test Signals
Contract tests should validate lock-sensitive mutation behavior, child edge consistency, `writeNewInode` optimizations, batch-write support flags, checkpoint round-trips, and debug traversal on malformed parent chains.
