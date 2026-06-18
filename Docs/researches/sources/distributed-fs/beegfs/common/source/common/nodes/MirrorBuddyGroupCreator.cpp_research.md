<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroupCreator.cpp -->
## sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroupCreator.cpp

### Purpose
`MirrorBuddyGroupCreator.cpp` implements manual and automatic mirror buddy group creation. It validates target combinations, talks to management to create groups, selects target pairs for automatic mode, warns about uneven target sizes, and handles storage-pool constraints.

### Important APIs, Types, And Functions
`addGroup()` validates metadata root ownership, calls `addGroupComm()`, logs user-facing success/errors, and returns `FhgfsOpsErr`. `addGroupComm()` sends `SetMirrorBuddyGroupMsg` to management and reads `SetMirrorBuddyGroupRespMsg`. `createMirrorBuddyGroups()` applies generated groups unless dry-run. `removeTargetsFromExistingMirrorBuddyGroups()` removes already grouped targets from the local mapper. `findNextTarget()` chooses a target from the node with most remaining targets, optionally excluding a node and filtering by storage pool. ID helpers generate normal or unique group IDs. `checkSizeOfTargets()` queries `StorageTargetInfo::statStoragePath()`. `selectPrimaryTarget()` balances primary-target counts. `generateMirrorBuddyGroups()` pairs targets automatically while respecting storage pools and metadata root rules.

### Control Flow
Automatic generation repeatedly selects a primary candidate, determines its storage pool, tries to select a secondary on a different node in the same pool, falls back to same-node pairing with warnings, ensures metadata root owner is primary, allocates a group ID, and updates output lists until fewer than two targets remain.

### State, Persistence, And Dependencies
The creator mutates local target mapper copies during selection; actual persistent group creation occurs through management messages. Dependencies include node stores, target mappers, storage pool store, root info, `MessagingTk`, `NodesTk`, `StorageTargetInfo`, and `ZipIterator`.

### Integration Points
Management CLI/tools use this class for mirror buddy group setup in storage and metadata contexts.

### Risks
Automatic selection is heuristic and ignores size mismatches beyond warnings. `findNextTarget()` unmaps `retVal` even when zero. Storage-pool lookups assume the primary target belongs to a pool. Communication failures during multi-group creation can leave partial changes. Tests should cover manual create errors, root-owner secondary rejection, dry-run/force modes, odd target counts, same-node fallback, storage-pool filtering, unique-ID conflicts with target IDs, and partial failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroupCreator.cpp -->
