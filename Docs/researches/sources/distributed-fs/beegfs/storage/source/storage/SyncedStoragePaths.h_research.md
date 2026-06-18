<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/SyncedStoragePaths.h -->
## sources/distributed-fs/beegfs/storage/source/storage/SyncedStoragePaths.h

### Purpose
Provides per-target path serialization and monotonic storage version generation for operations that need synchronized dynamic attributes.

### Important APIs, Types, And Functions
APIs are constructor, lockPath(path, targetID), unlockPath(path, targetID), initStorageVersion(), and incStorageVersion().

### Control Flow
lockPath() builds a target-qualified path string, waits until it can insert it into a set, increments storageVersion, and returns the new version. unlockPath() erases the target-qualified path and broadcasts to waiters.

### State, Persistence, And Dependencies
Runtime state is a mutex, condition variable, storageVersion initialized from current seconds shifted left 32, and a set of locked path keys. No disk persistence occurs; versions are returned in responses for metadata reconciliation. Depends on LogContext, System time, Condition, Mutex, StringTk hex conversion, and Common.h.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include inconsistent StringTk::uint64ToHexStr in lockPath versus uintToHexStr in unlockPath, which could break unlock for some target IDs if formatting differs, and no RAII guard for lock/unlock pairing.

### Test Signals
Test signals include concurrent lock wait/unlock wake, monotonically increasing versions, unlock of unknown path logging, and target-qualified independence for same path on different targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/SyncedStoragePaths.h -->
