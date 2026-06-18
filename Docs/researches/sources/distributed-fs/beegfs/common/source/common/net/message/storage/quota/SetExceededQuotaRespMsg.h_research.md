<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetExceededQuotaRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetExceededQuotaRespMsg.h

### Purpose
`SetExceededQuotaRespMsg` returns the result of updating exceeded-quota state.

### Important APIs, Types, And Functions
It subclasses `SimpleIntMsg` with `NETMSGTYPE_SetExceededQuotaResp`.

### Control Flow
Only the integer result is serialized.

### State, Persistence, And Dependencies
The message has no persistent state. It depends on `SimpleIntMsg`.

### Integration Points
Quota synchronization callers use this after `SetExceededQuotaMsg`.

### Risks
No typed getter is provided. Tests should verify result-code handling, especially partial or validation failures in the receiver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetExceededQuotaRespMsg.h -->
