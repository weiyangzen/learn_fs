<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/RenameMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/RenameMsg.h

### Purpose
`RenameMsg` requests a metadata rename from one directory/name to another, carrying entry type, optional file-event logging data, and buddy-mirror second-phase timestamps.

### Important APIs, Types, And Functions
The class derives from `MirroredMessageBase<RenameMsg>` with `NETMSGTYPE_Rename`. The header feature flag `RENAMEMSG_FLAG_HAS_EVENT` gates `FileEvent` serialization. The payload contains `DirEntryType`, source/destination `EntryInfo`, old/new names, optional event, and optional mirrored timestamps for source directory and renamed inode. `supportsMirroring()` returns true.

### Control Flow
Serialization always writes entry type and directory/name fields. Optional event and buddy-secondary timestamp sections are written only when their flags are present.

### State, Persistence, And Dependencies
The message is transient but triggers persistent namespace and inode timestamp changes. Dependencies include `EntryInfo`, `FileEvent`, `StatData`, and mirrored-message infrastructure.

### Integration Points
Client metadata rename operations and mirrored replay paths use this request.

### Risks
Source and destination directory info are non-owned on send. Event flag mismatches can shift the wire layout. Buddy-second timestamp replay must be exact for mirror consistency. Tests should cover same-directory rename, cross-directory rename, file and directory entry types, event/no-event cases, buddy-secondary replay, and conflict/error responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/RenameMsg.h -->
