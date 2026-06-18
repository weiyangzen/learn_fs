<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/FindOwnerMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/FindOwnerMsg.h

### Purpose
`FindOwnerMsg` drives recursive owner discovery for a path or entry. It carries a path, maximum search depth, current recursion depth, and the current `EntryInfo` context.

### Important APIs, Types, And Functions
The class derives from `NetMessageSerdes<FindOwnerMsg>` with type `NETMSGTYPE_FindOwner`. Serialization writes `searchDepth`, `currentDepth`, backed `EntryInfo`, and backed `Path`. Getters expose the path, depths, and parsed `EntryInfo`.

### Control Flow
Senders supply non-owned `Path*` and `EntryInfo*`; deserialization populates internal `Path parsed.path` and `EntryInfo entryInfo`. Receivers use the depth fields to continue or stop owner traversal.

### State, Persistence, And Dependencies
State is transient. Dependencies include `Path`, `EntryInfo`, the abstract message factory friend, and BeeGFS serdes backed-pointer support.

### Integration Points
Metadata lookup code uses this message to walk ownership across distributed directory partitions.

### Risks
Depth fields are unsigned on the wire while the constructor accepts an `int currentDepth`, so negative caller input would wrap. Pointer lifetimes matter on send. Tests should include zero and maximum depths, multi-component paths, deserialization of `EntryInfo`, and receiver behavior when search depth is exhausted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/FindOwnerMsg.h -->
