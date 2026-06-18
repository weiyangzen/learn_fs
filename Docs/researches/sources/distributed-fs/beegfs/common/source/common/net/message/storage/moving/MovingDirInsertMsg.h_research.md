<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/MovingDirInsertMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/MovingDirInsertMsg.h

### Purpose
`MovingDirInsertMsg` inserts a serialized directory entry/link into a destination directory during cross-directory or cross-node rename/move handling, with support for buddy-mirror second-phase timestamps.

### Important APIs, Types, And Functions
It derives from `MirroredMessageBase<MovingDirInsertMsg>` with `NETMSGTYPE_MovingDirInsert`. Serialization writes destination `EntryInfo`, aligned new name, serialized buffer length, raw serialized buffer, and optional `dirTimestamps` when `Flag_BuddyMirrorSecond` is set. `supportsMirroring()` returns true.

### Control Flow
Senders provide destination directory info and a non-owned serialized directory-link buffer. Receivers deserialize the destination info and raw buffer, then perform insertion.

### State, Persistence, And Dependencies
The message is transient but creates persistent namespace metadata at the destination. It depends on `EntryInfo`, `StatData`, mirrored timestamps, and raw-block serdes.

### Integration Points
Rename/move workflows use it when the target directory is handled by a different metadata node or when replaying mirrored operations.

### Risks
Serialized buffer validity is trusted by downstream code; length and pointer must be correct. Buddy second-phase timestamp handling must match primary-side changes. Tests should cover normal insert, buddy-secondary insert, zero-length/invalid buffers, and overwritten/duplicate target-name behavior in handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/MovingDirInsertMsg.h -->
