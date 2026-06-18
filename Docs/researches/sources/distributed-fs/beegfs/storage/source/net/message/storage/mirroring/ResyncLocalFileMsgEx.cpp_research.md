<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/ResyncLocalFileMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/ResyncLocalFileMsgEx.cpp

### Purpose
Applies resync data for a chunk file, optionally forwarding chunk-balancing mirrored writes to the secondary and setting final file attributes.

### Important APIs, Types, And Functions
Core functions are processIncoming(), doWrite(), doWriteSparse(), doTrunc(), and forwardToSecondary(). The handler reads data buffer, relative path, count, offset, target IDs, and flags such as NODATA, CHECK_SPARSE, TRUNC, SETATTRIBS, BUDDYMIRROR, and CHUNKBALANCE_BUDDYMIRROR.

### Control Flow
For chunk-balance mirrored resync it derives the buddy group from a concrete target ID, chooses primary or secondary, and forwards to the secondary unless already marked SECOND. Locally it chooses chunk or mirror FD, opens or creates the chunk through ChunkStore, truncates on offset zero data writes, writes all bytes or skips sparse zero blocks, optionally truncates to offset+count, applies chmod/chown attributes, closes the FD, and responds with ResyncLocalFileRespMsg.

### State, Persistence, And Dependencies
Persistent effects are chunk contents, sparse holes, truncation length, mode, uid, and gid. On open, write, truncate, chmod, or chown failure it marks the StorageTarget BAD. Secondary offline communication marks buddyNeedsResync rather than failing local processing. Depends on ChunkStore, SessionQuotaInfo, MsgHelperIO::pwrite, StorageTargets, MirrorBuddyGroupMapper, MessagingTk, GenericResponseMsg, StorageTarget state mutation, and common resync response messages.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include not checking forwardToSecondary() return before continuing local writes, fchown/fchmod errors still attempting close and response, sparse write loop assumptions about zero block size, logging invalid target IDs using !targetID instead of targetID, and target BAD transitions on transient disk errors.

### Test Signals
Test signals include full and short write loops, sparse all-zero buffer requiring ftruncate at EOF, NODATA attribute-only sync, truncation flag, secondary-forward success/failure/offline, invalid buddy mapping, quota-open failures, and target BAD marking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/ResyncLocalFileMsgEx.cpp -->
