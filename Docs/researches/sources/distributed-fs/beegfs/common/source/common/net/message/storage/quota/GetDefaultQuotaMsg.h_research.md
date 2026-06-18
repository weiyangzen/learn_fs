<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/GetDefaultQuotaMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/GetDefaultQuotaMsg.h

### Purpose
`GetDefaultQuotaMsg` requests default quota limits for a specific storage pool.

### Important APIs, Types, And Functions
It derives from `NetMessageSerdes<GetDefaultQuotaMsg>` with `NETMSGTYPE_GetDefaultQuota`; serialization writes `StoragePoolId storagePoolId`.

### Control Flow
The send constructor sets the pool ID. The no-arg constructor supports deserialization.

### State, Persistence, And Dependencies
The message is transient and depends on `StoragePoolId` and NetMessage serdes.

### Integration Points
Management quota tools send it to retrieve default user/group quota limits for a pool.

### Risks
There is no public getter in this base header, so handlers may rely on protected access through subclassing/friend context or direct deserialization conventions. Tests should verify pool ID round-trip, invalid pool handling, and paired response behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/GetDefaultQuotaMsg.h -->
