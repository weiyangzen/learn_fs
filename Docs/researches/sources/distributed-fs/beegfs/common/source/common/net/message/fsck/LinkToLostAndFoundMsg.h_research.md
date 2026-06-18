# sources/distributed-fs/beegfs/common/source/common/net/message/fsck/LinkToLostAndFoundMsg.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/LinkToLostAndFoundMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/LinkToLostAndFoundMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/LinkToLostAndFoundMsg.h` defines the `LinkToLostAndFoundMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('LinkToLostAndFoundMsg', 'NetMessageSerdes<LinkToLostAndFoundMsg>')], message type(s) NETMSGTYPE_LinkToLostAndFound, getters, constructors for outbound and deserialization use, and serialization fields: entryType, lostAndFoundInfoPtr, lostAndFoundInfo, dirInodes, parsed, fileInodes. Detected classes are [('LinkToLostAndFoundMsg', 'NetMessageSerdes<LinkToLostAndFoundMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/fsck/FsckDirInode.h`, `common/net/message/NetMessage.h`, `common/toolkit/FsckTk.h`. Important local state or payload members include `FsckDirEntryType entryType; // to indicate, whether dir inodes or file inodes should be`, `FsckDirInodeList* dirInodes; // not owned by this object`, `FsckFileInodeList* fileInodes; // not owned by this object`, `EntryInfo* lostAndFoundInfoPtr; // not owned by this object`, `EntryInfo lostAndFoundInfo`, `FsckDirInodeList dirInodes`, `FsckFileInodeList fileInodes`, `return *dirInodes`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_LinkToLostAndFound`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/LinkToLostAndFoundMsg.h -->
