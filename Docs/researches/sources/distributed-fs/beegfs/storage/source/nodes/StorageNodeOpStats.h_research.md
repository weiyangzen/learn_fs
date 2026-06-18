<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/nodes/StorageNodeOpStats.h -->
## sources/distributed-fs/beegfs/storage/source/nodes/StorageNodeOpStats.h

### Purpose
Extends node operation statistics with per-user storage operation counters and byte accounting.

### Important APIs, Types, And Functions
UserStorageOpStats holds atomic numOps, numBytesWritten, and numBytesRead. StorageNodeOpStats derives from NodeOpStats and overloads updateNodeOp() for operation-only and byte-counted read/write updates.

### Control Flow
Each update takes a read lock, finds counters by peer IP cookie and user ID, upgrades to a write lock if either counter is absent, inserts missing StorageOpCounter objects, then increments operation or byte counters and unlocks.

### State, Persistence, And Dependencies
Runtime state is inherited maps for clientCounterMap and userCounterMap. No persistence occurs here; counters live in memory for monitoring/stat reporting. Depends on NodeOpStats, OpCounter, IPAddress, AtomicUInt64, SafeRWLock, and StorageOpCounterTypes.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include iterator reuse after lock upgrade based on pre-upgrade lookups, duplicated include of OpCounter.h, and accepting byte updates for operation types documented as read/write only without local assertion.

### Test Signals
Test signals include first-update insertion, concurrent updates for same and different users, byte accounting, and map consistency after lock upgrade races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/nodes/StorageNodeOpStats.h -->
