<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetQuotaRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetQuotaRespMsg.h

### Purpose
`SetQuotaRespMsg` returns the result of setting explicit quota limits.

### Important APIs, Types, And Functions
It subclasses `SimpleIntMsg` with type `NETMSGTYPE_SetQuotaResp`.

### Control Flow
The response uses inherited single-integer serialization.

### State, Persistence, And Dependencies
There is no persistent state in the response. It depends on simple message serialization.

### Integration Points
Quota administration tools consume it after `SetQuotaMsg`.

### Risks
No typed result getter is defined. Tests should cover result-code round-trip and caller casting to `FhgfsOpsErr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetQuotaRespMsg.h -->
