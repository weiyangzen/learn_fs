<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/MirrorMetadataMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/MirrorMetadataMsg.h

### Purpose
`MirrorMetadataMsg` is the abstract common-base message for metadata mirroring tasks. It intentionally does not implement payload serialization because `MirrorerTask` lives in the metadata server component rather than common code.

### Important APIs, Types, And Functions
The class derives directly from `NetMessage` with type `NETMSGTYPE_MirrorMetadata`. It stores a non-owned `MirrorerTaskList*`, the number of list elements, and the total serialized length.

### Control Flow
Only protected constructors exist: one for send-side task-list metadata and one for deserialization. Concrete metadata-server code is expected to subclass and implement actual task serialization.

### State, Persistence, And Dependencies
The header carries transient references to mirroring tasks that represent persistent metadata changes to replay elsewhere. It depends only on `NetMessage` and forward declarations in common code.

### Integration Points
`MirrorMetadataMsgEx` or equivalent metadata-server extensions provide serialization and handlers. The common base lets the message type be known without dragging metadata-server task definitions into the common library.

### Risks
Because serialization is deferred to derived code, factory registration and handler downcasts must stay aligned. Non-owned task-list lifetime is critical. Tests should target the derived message implementation and verify task count/serialized-length consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/MirrorMetadataMsg.h -->
