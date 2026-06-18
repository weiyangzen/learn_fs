<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/ChunkLockStore.h -->
## sources/distributed-fs/beegfs/storage/source/storage/ChunkLockStore.h

### Purpose
Provides abstract per-target chunk ID locking used mainly to serialize mirrored chunk modifications during buddy resync.

### Important APIs, Types, And Functions
ChunkLockStoreContents contains lockedChunks, lockedChunksMutex, and chunkUnlockedCondition. ChunkLockStore exposes lockChunk(), unlockChunk(), and debug-only size/copy helpers, with private getOrInsertTargetLockStore() and findTargetLockStore().

### Control Flow
lockChunk() inserts the chunk ID into a target-specific set, waiting on a condition variable while another holder owns it. unlockChunk() removes the ID and broadcasts to waiters. Target lock-store maps are inserted under an RWLock.

### State, Persistence, And Dependencies
Runtime state is the target-to-lock-store map and per-target locked chunk sets. No persistence occurs. Depends on Mutex, Condition, RWLock/UniqueRWLock, StringSet, logging/backtrace utilities, and target IDs.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include no ownership token, so any caller can unlock any chunk ID; missing target store on unlock only logs; and condition waits rely on Mutex/Condition semantics rather than std::condition_variable predicates.

### Test Signals
Test signals include multiple waiters on same chunk, independent targets using same chunk ID, unlock of unknown target/chunk, and stress tests for target-store insertion races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/ChunkLockStore.h -->
