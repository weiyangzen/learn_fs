# sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FixInodeOwnersInDentryMsg.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FixInodeOwnersInDentryMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FixInodeOwnersInDentryMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FixInodeOwnersInDentryMsg.h` defines the `FixInodeOwnersInDentryMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('FixInodeOwnersInDentryMsg', 'NetMessageSerdes<FixInodeOwnersInDentryMsg>')], message type(s) NETMSGTYPE_FixInodeOwnersInDentry, getters, constructors for outbound and deserialization use, and serialization fields: dentries, parsed, owners. Detected classes are [('FixInodeOwnersInDentryMsg', 'NetMessageSerdes<FixInodeOwnersInDentryMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/fsck/FsckDirEntry.h`, `common/net/message/NetMessage.h`. Important local state or payload members include `FsckDirEntryList* dentries`, `NumNodeIDList* owners`, `FsckDirEntryList dentries`, `NumNodeIDList owners`, `return *dentries`, `return *owners`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_FixInodeOwnersInDentry`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FixInodeOwnersInDentryMsg.h -->
