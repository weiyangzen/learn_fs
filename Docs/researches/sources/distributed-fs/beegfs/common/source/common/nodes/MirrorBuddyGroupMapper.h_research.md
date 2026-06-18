<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroupMapper.h -->
## sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroupMapper.h

### Purpose
`MirrorBuddyGroupMapper.h` declares the mirror buddy group mapping service and buddy-state enum.

### Important APIs, Types, And Functions
`MirrorBuddyState` has unmapped, primary, and secondary states. The mapper exposes mapping/unmapping, sync-from-lists, list extraction, target-to-group and target-to-buddy queries, buddy-state queries, and attachment points for meta capacity pools, storage pools, and usable node stores. Inline getters return group details, map copies, size, and local group data under read locks.

### Control Flow
Public methods acquire read/write locks around map access. Friend target-state stores can perform atomic state/group transitions with protected internals.

### State, Persistence, And Dependencies
Protected state includes `TargetMapper*`, optional pool/node stores, `RWLock`, `MirrorBuddyGroupMap`, and `localGroupID`. Dependencies include capacity pools, target mapper, safe RW locks, node stores, and buddy group value types.

### Integration Points
Mirroring, management, and target state code use this mapper for role resolution and mapping synchronization from management.

### Risks
Inline unlocked helpers require callers to hold locks. `localGroupID` is a single group ID, so multi-membership assumptions would not fit. Tests should cover all query APIs and lock-safe copy/list extraction behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroupMapper.h -->
