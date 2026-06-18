<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/MovingDirInsertRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/MovingDirInsertRespMsg.h

### Purpose
`MovingDirInsertRespMsg` returns the result of inserting a moved directory entry.

### Important APIs, Types, And Functions
It subclasses `SimpleIntMsg` with `NETMSGTYPE_MovingDirInsertResp`; `getResult()` casts to `FhgfsOpsErr`.

### Control Flow
Single-result-code serialization is inherited.

### State, Persistence, And Dependencies
No response state persists. It depends on simple-message serialization and storage error conventions.

### Integration Points
Move/rename orchestration consumes this to decide whether source-side cleanup can continue.

### Risks
It does not include conflict detail or overwritten metadata. Tests should cover success, exists/conflict, not-owner, and communication failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/MovingDirInsertRespMsg.h -->
