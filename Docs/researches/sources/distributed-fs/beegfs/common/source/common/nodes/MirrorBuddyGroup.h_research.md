<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroup.h -->
## sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroup.h

### Purpose
`MirrorBuddyGroup.h` defines the simple value object representing a mirror buddy group as primary and secondary target IDs.

### Important APIs, Types, And Functions
`MirrorBuddyGroup` stores `firstTargetID` and `secondTargetID`, provides constructors, equality comparison, and a serializer that writes both IDs. It defines `MirrorBuddyGroupList`, `MirrorBuddyGroupMap`, and iterator typedefs.

### Control Flow
There is no behavioral control flow; consumers interpret first as primary and second as secondary.

### State, Persistence, And Dependencies
State is two 16-bit IDs. The type is serialized in management mappings and used in memory by mappers.

### Integration Points
`MirrorBuddyGroupMapper`, `MirrorBuddyGroupCreator`, management messages, and storage/metadata mirroring logic use this type.

### Risks
The field names `firstTargetID`/`secondTargetID` are semantically primary/secondary by convention; misuse can invert roles. Tests should cover serialization and equality, and higher-level tests should verify primary/secondary role handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroup.h -->
