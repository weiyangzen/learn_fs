<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/ResyncRawInodesRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/ResyncRawInodesRespMsg.h

### Purpose
`ResyncRawInodesRespMsg` returns the status of raw inode resynchronization.

### Important APIs, Types, And Functions
It subclasses `SimpleIntMsg` using `NETMSGTYPE_ResyncRawInodesResp`; `getResult()` casts to `FhgfsOpsErr`.

### Control Flow
Serialization and deserialization are inherited single-integer behavior.

### State, Persistence, And Dependencies
The response itself is transient; the operation it acknowledges repairs persistent inode state.

### Integration Points
Metadata buddy resync code consumes this response after raw inode transfer or comparison work.

### Risks
The response does not carry per-inode failure detail. Tests should verify error-code round-trip and higher-level retry behavior on non-success results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/ResyncRawInodesRespMsg.h -->
