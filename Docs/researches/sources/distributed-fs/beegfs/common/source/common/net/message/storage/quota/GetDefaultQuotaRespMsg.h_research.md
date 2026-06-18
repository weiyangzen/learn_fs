<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/GetDefaultQuotaRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/GetDefaultQuotaRespMsg.h

### Purpose
`GetDefaultQuotaRespMsg` returns the default quota limits for a storage pool.

### Important APIs, Types, And Functions
It derives from `NetMessageSerdes<GetDefaultQuotaRespMsg>` with `NETMSGTYPE_GetDefaultQuotaResp`. Serialization writes a `QuotaDefaultLimits` object. `getDefaultLimits()` returns the parsed mutable reference.

### Control Flow
The response either default-constructs for deserialization or copies provided default limits for sending.

### State, Persistence, And Dependencies
The message is a transient snapshot of quota configuration. It depends on `QuotaDefaultLimits`.

### Integration Points
Quota management code uses it after `GetDefaultQuotaMsg` to display or validate defaults.

### Risks
No explicit result/error field is included; errors must be represented by communication failure or encoded defaults elsewhere. Tests should cover user/group defaults, unlimited values, and invalid storage-pool handling in the surrounding request path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/GetDefaultQuotaRespMsg.h -->
