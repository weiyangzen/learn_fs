<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetQuotaMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetQuotaMsg.h

### Purpose
`SetQuotaMsg` sends explicit quota limits for a storage pool as a list of `QuotaData` records.

### Important APIs, Types, And Functions
It derives from `NetMessageSerdes<SetQuotaMsg>` with `NETMSGTYPE_SetQuota`. Serialization writes `storagePoolId` and `QuotaDataList quotaData`. Constants estimate maximum quota records per payload. `insertQuotaLimit()` appends records, and getters expose the pool ID and data list.

### Control Flow
Senders construct with a storage pool ID and append quota records before sending. The protected default constructor supports deserialization through factories/subclasses.

### State, Persistence, And Dependencies
The message is transient but causes persistent quota limit updates. It depends on `QuotaData` and NetMessage payload sizing.

### Integration Points
Quota administration paths use it to update per-user or per-group quota limits.

### Risks
The header does not enforce maximum record count. The protected default constructor may require factory access. Tests should cover empty lists, max-sized lists, mixed user/group records if allowed by handlers, invalid pool IDs, and persistence confirmation via subsequent `GetQuotaInfoMsg`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetQuotaMsg.h -->
