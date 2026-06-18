<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroupMapper.cpp -->
## sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroupMapper.cpp

### Purpose
`MirrorBuddyGroupMapper.cpp` manages in-memory mirror buddy group mappings, validates additions, updates related capacity/storage pools, tracks the local group, and answers target-to-buddy queries.

### Important APIs, Types, And Functions
Constructors initialize optional target mapper references and attached stores. `mapMirrorBuddyGroup()` validates target existence, self-pairing, group ID conflicts, update permission, and target reuse before inserting/updating a `MirrorBuddyGroup`. `unmapMirrorBuddyGroup()` removes a group and updates attached pool stores. `syncGroupsFromLists()` replaces mappings from list payloads. Query methods return mappings as lists, find buddy group IDs, buddy target IDs, and buddy states. `generateID()` finds the next free group ID with gap handling.

### Control Flow
Mapping validation runs mostly before taking the write lock, including target existence and current group membership checks. Under the write lock, group ID zero triggers generated ID allocation, the map is updated, attached pools are updated, and `localGroupID` is set if the local node is a member. Sync builds a new map without holding the write lock, then swaps it in.

### State, Persistence, And Dependencies
State is the `mirrorBuddyGroups` map and `localGroupID`, protected by `RWLock`. Attached `NodeCapacityPools`, `StoragePoolStore`, and `NodeStore` are updated as side effects but persistence is handled by surrounding management code. Dependencies include `TargetMapper`, `NodeStore`, capacity pools, storage pools, and `MirrorBuddyGroup`.

### Integration Points
Management target-state stores, storage/metadata services, and mirroring logic use this mapper to resolve primary/secondary roles and buddy targets.

### Risks
Some validation before acquiring the write lock can race with concurrent map updates. `getBuddyGroupIDUnlocked()` unconditionally writes through `outTargetIsPrimary`, so callers must pass a non-null pointer. `unmapMirrorBuddyGroup()` indexes `mirrorBuddyGroups[buddyGroupID]`, which can insert a default group before erase if the ID is absent. Tests should cover create/update conflicts, generated IDs at boundaries, local group tracking, pool attachment side effects, absent-group unmap, sync replacement, and concurrent readers/writers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroupMapper.cpp -->
