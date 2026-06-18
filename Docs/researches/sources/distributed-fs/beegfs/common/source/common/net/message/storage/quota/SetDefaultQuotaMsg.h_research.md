<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetDefaultQuotaMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetDefaultQuotaMsg.h

### Purpose
`SetDefaultQuotaMsg` sets default quota limits for a storage pool and quota data type.

### Important APIs, Types, And Functions
It derives from `NetMessageSerdes<SetDefaultQuotaMsg>` with `NETMSGTYPE_SetDefaultQuota`. Serialization writes `storagePoolId`, `size`, `inodes`, and integer `type`. Getters expose size, inodes, and quota data type.

### Control Flow
Senders construct with pool, type, size, and inode limits. The default constructor supports deserialization.

### State, Persistence, And Dependencies
The message is transient but updates persistent quota configuration on the receiver. It depends on `QuotaData` and `StoragePoolId`.

### Integration Points
Quota administration tools use it to change default user or group quota limits.

### Risks
There is no getter for `storagePoolId` in this header even though it is serialized. Unlimited/sentinel values must be interpreted consistently by handlers. Tests should cover user/group types, zero/unlimited values, invalid pool IDs, and response result handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetDefaultQuotaMsg.h -->
