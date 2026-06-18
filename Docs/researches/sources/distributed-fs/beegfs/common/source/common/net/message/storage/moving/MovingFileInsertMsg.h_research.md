<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/MovingFileInsertMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/MovingFileInsertMsg.h

### Purpose
`MovingFileInsertMsg` tells a remote metadata server to insert a moved file into a destination directory. It carries source file info, destination directory info, new name, serialized file metadata, optional streamed xattrs, and buddy-mirror timestamps.

### Important APIs, Types, And Functions
It derives from `MirroredMessageBase<MovingFileInsertMsg>` with `NETMSGTYPE_MovingFileInsert`. The feature flag `MOVINGFILEINSERTMSG_FLAG_HAS_XATTRS` enables an extra xattr stream via `registerStreamoutHook()`. Serialization writes source/destination `EntryInfo`, aligned name, raw serialized inode buffer, and optional dir/file timestamps for buddy second-phase replay.

### Control Flow
The core message sends metadata in the normal payload. When xattrs are present, the request/response framework streams extra data through `MsgHelperXAttr::StreamXAttrState::streamXattrFn`.

### State, Persistence, And Dependencies
The message is transient but creates or replaces persistent file metadata at the destination. Dependencies include `EntryInfo`, `MessagingTk`, `MsgHelperXAttr`, and mirrored timestamps.

### Integration Points
Cross-directory rename/move logic, metadata migration, and buddy mirroring consume this message.

### Risks
The serialized inode buffer and xattr extra stream must stay consistent; a receiver that sees the feature flag must read the extra data exactly once. Non-owned pointers require send-side lifetime. Tests should cover moves with/without xattrs, buddy-secondary replay, overwrite cases, malformed buffer lengths, and stream failures after payload delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/MovingFileInsertMsg.h -->
