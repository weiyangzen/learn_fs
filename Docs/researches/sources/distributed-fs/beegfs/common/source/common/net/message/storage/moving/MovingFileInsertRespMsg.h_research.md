<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/MovingFileInsertRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/MovingFileInsertRespMsg.h

### Purpose
`MovingFileInsertRespMsg` returns the result of a moved-file insertion and, if a destination entry was overwritten, returns the overwritten inode buffer and entry info.

### Important APIs, Types, And Functions
It derives from `NetMessageSerdes<MovingFileInsertRespMsg>` with `NETMSGTYPE_MovingFileInsertResp`. Serialization writes `result`, `inodeBufLen`, raw `inodeBuf`, and `overWrittenEntryInfo`.

### Control Flow
Senders provide result plus optional overwritten inode data. Receivers inspect `inodeBufLen` to determine whether an overwritten file exists.

### State, Persistence, And Dependencies
The response is transient but can carry serialized metadata needed for cleanup or rollback. It depends on `EntryInfo`, raw-block serdes, and storage error codes.

### Integration Points
Rename/move orchestration uses it after remote insertion to handle replaced files and source-side finalization.

### Risks
If `inodeBufLen` and `inodeBuf` disagree, serialization can read invalid memory. The overwritten `EntryInfo` is documented as default/unused when no overwrite occurred but is always serialized. Tests should cover no-overwrite, overwrite with inode buffer, error result with/without buffer, and deserialization of zero-length raw blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/MovingFileInsertRespMsg.h -->
