<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/RequestExceededQuotaMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/RequestExceededQuotaMsg.h

### Purpose
`RequestExceededQuotaMsg` asks for IDs that exceeded a specific quota type, either scoped by storage pool or by target ID.

### Important APIs, Types, And Functions
It derives from `NetMessageSerdes<RequestExceededQuotaMsg>` with `NETMSGTYPE_RequestExceededQuota`. Constructors set `QuotaDataType`, `QuotaLimitType`, `StoragePoolId`, and target ID variants. Serialization writes quota data type, exceeded type, storage pool ID, and target ID.

### Control Flow
The receiver interprets whether the request is pool-scoped or target-scoped based on the storage pool/target values. Getters cast integer enum fields back to quota types.

### State, Persistence, And Dependencies
The message is transient and depends on `StoragePoolStore`, `QuotaData`, and `StoragePoolId`.

### Integration Points
Quota enforcement and monitoring paths use it to query exceeded user/group IDs from management or storage components.

### Risks
Invalid combinations of storage pool and target ID are possible at the message level. Tests should cover pool-scoped and target-scoped constructors, invalid pool/target handling, and paired response list limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/RequestExceededQuotaMsg.h -->
