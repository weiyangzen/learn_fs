# sources/distributed-fs/beegfs/common/source/common/fsck/FsckTargetID.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/fsck/FsckTargetID.h -->
## sources/distributed-fs/beegfs/common/source/common/fsck/FsckTargetID.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/fsck/FsckTargetID.h` defines the `FsckTargetID` fsck record type used by consistency scans, database comparisons, and fsck messages. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important APIs include list typedefs, constructors including deserialization constructors, getters/setters, comparison operators, and serialize(). Classes/enums: [('FsckTargetID', '')] ['FsckTargetIDType']. Key stored fields include id, targetIDType, id, targetIDType, true, true, false, false, false, true. Detected classes are [('FsckTargetID', '')]; structs ['ListSerializationHasLength']; enums ['FsckTargetIDType']; notable out-of-line methods none.

### Control Flow
Control flow is value-object behavior: construct, compare/order, optionally mutate repair fields, print in a few types, and serialize through BeeGFS serdes. ListSerializationHasLength=false marks list wire format expectations for these fsck objects.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/Common.h`, `common/toolkit/serialization/Serialization.h`. Important local state or payload members include `uint16_t id`, `FsckTargetIDType targetIDType`, `return id`, `return targetIDType`, `return true`, `return true`, `return false`, `return false`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include ordering/equality consistency with serialized fields. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/fsck/FsckTargetID.h -->
