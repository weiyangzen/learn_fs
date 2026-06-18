<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/SetMetadataMirroringRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/SetMetadataMirroringRespMsg.h

### Purpose
`SetMetadataMirroringRespMsg` returns the result of enabling metadata mirroring.

### Important APIs, Types, And Functions
It subclasses `SimpleIntMsg` with type `NETMSGTYPE_SetMetadataMirroringResp`; `getResult()` casts to `FhgfsOpsErr`.

### Control Flow
The response is a simple status payload.

### State, Persistence, And Dependencies
No response state persists. It depends on `StorageErrors` and simple-message wrappers.

### Integration Points
Management code consumes this after sending `SetMetadataMirroringMsg`.

### Risks
Only a result code is available, so detailed migration state must be logged or queried separately. Tests should cover success, already mirrored, not-owner, and internal-error cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/SetMetadataMirroringRespMsg.h -->
