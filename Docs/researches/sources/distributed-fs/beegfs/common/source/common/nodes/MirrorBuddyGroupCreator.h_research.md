<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroupCreator.h -->
## sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroupCreator.h

### Purpose
`MirrorBuddyGroupCreator.h` declares the helper used to create mirror buddy groups manually or automatically.

### Important APIs, Types, And Functions
The class stores node type, management nodes, target mappers, node stores, local/system target mappers, existing buddy lists, config flags (`cfgForce`, `cfgDryrun`, `cfgUnique`), storage pool store, and metadata root info. Public methods include `addGroup()`, `createMirrorBuddyGroups()`, `removeTargetsFromExistingMirrorBuddyGroups()`, `generateMirrorBuddyGroups()`, and static `generateID()`. Private/protected helpers handle communication, target selection, unique IDs, size checks, and primary selection.

### Control Flow
Consumers configure the creator with current system mappings and flags, generate candidate groups, then optionally create them through management.

### State, Persistence, And Dependencies
The class holds references/pointers to external stores and copies of target mappers. Persistence happens through management messages, not directly in the creator. Dependencies include node stores, target mappers, buddy-group mapper, root info, and storage pool store.

### Integration Points
Command-line management and administrative workflows use this abstraction to set up mirroring.

### Risks
Most dependencies are raw pointers/references and must outlive the creator. Config flags materially alter behavior. Tests should cover constructor setup, flag combinations, null/invalid store assumptions, and generated output lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroupCreator.h -->
