<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetDefaultQuotaRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetDefaultQuotaRespMsg.h

### Purpose
`SetDefaultQuotaRespMsg` returns the integer result of setting default quota limits.

### Important APIs, Types, And Functions
It subclasses `SimpleIntMsg` with `NETMSGTYPE_SetDefaultQuotaResp`.

### Control Flow
Single integer result serialization is inherited.

### State, Persistence, And Dependencies
The response has no persistent state and depends on simple-message behavior.

### Integration Points
Quota administration callers consume this after `SetDefaultQuotaMsg`.

### Risks
The class does not add a typed `getResult()` helper, so callers must use inherited `getValue()` consistently. Tests should cover success and common validation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetDefaultQuotaRespMsg.h -->
