<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/StorageTargets.h -->
## sources/distributed-fs/beegfs/storage/source/storage/StorageTargets.h

### Purpose
Declares StorageTarget, the per-target runtime/persistent state object, and StorageTargets, the immutable map wrapper for local targets.

### Important APIs, Types, And Functions
StorageTarget APIs expose path, ID, chunk/mirror FDs, quota block device, consistency state, buddy resync in-progress/needed state, clean shutdown, offline timeout, last buddy communication, setState(), prepareTargetDir(), and isTargetDir(). StorageTargets exposes decideResync(), checkBuddyNeedsResync(), generateTargetInfoList(), fillTargetStateMap(), getTarget(), and getTargets().

### Control Flow
The header defines persistent buddy-resync flags and LastBuddyComm serialization, plus the state-transition hooks used by cpp implementation.

### State, Persistence, And Dependencies
State includes Path, target ID, FDHandles, PreallocatedFile values, QuotaBlockDevice, TimerQueue references, management and buddy mapper references, atomics, RWLock-protected consistency/clean/offline state, and optional retry timer handle. Depends on TargetStateStore types, StorageTargetInfo, PreallocatedFile, TimerQueue, Config, QuotaBlockDevice, boost::optional, chrono, and atomics.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include const StorageTargetMap preventing target insertion/removal after construction, raw target pointer returns, and timer callbacks coupled to object lifetime.

### Test Signals
Test signals include getters/setters under concurrent access, PreallocatedFile serialization compatibility, offline timeout expiry, and target map lookup semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/StorageTargets.h -->
