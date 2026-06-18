# sources/distributed-fs/beegfs/common/source/common/fsck/FsckDuplicateInodeInfo.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/fsck/FsckDuplicateInodeInfo.h -->
## sources/distributed-fs/beegfs/common/source/common/fsck/FsckDuplicateInodeInfo.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/fsck/FsckDuplicateInodeInfo.h` defines the `FsckDuplicateInodeInfo` fsck record type used by consistency scans, database comparisons, and fsck messages. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important APIs include list typedefs, constructors including deserialization constructors, getters/setters, comparison operators, and serialize(). Classes/enums: [('FsckDuplicateInodeInfo', ''), ('to', ''), ('FsckDuplicateInodeInfo', '')] []. Key stored fields include FsckDuplicateInodeInfo, entryID, parentDirID, saveNodeID, isInlined, isBuddyMirrored, dirEntryType. Detected classes are [('FsckDuplicateInodeInfo', ''), ('to', ''), ('FsckDuplicateInodeInfo', '')]; structs ['ListSerializationHasLength']; enums none; notable out-of-line methods none.

### Control Flow
Control flow is value-object behavior: construct, compare/order, optionally mutate repair fields, print in a few types, and serialize through BeeGFS serdes. ListSerializationHasLength=false marks list wire format expectations for these fsck objects.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/Common.h`, `common/toolkit/serialization/Serialization.h`. Important local state or payload members include `class FsckDuplicateInodeInfo`, `std::string entryID`, `std::string parentDirID`, `uint32_t saveNodeID`, `bool isInlined`, `bool isBuddyMirrored`, `DirEntryType dirEntryType`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include ordering/equality consistency with serialized fields. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/fsck/FsckDuplicateInodeInfo.h -->
