<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetExceededQuotaMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetExceededQuotaMsg.h

### Purpose
`SetExceededQuotaMsg` updates the set of quota IDs known to have exceeded a limit for a storage pool, data type, and limit type.

### Important APIs, Types, And Functions
It derives from `NetMessageSerdes<SetExceededQuotaMsg>` with type `NETMSGTYPE_SetExceededQuota`, and it also has constructors that allow subclasses to set a different message type. Serialization writes `storagePoolId`, `quotaDataType`, `exceededType`, and `UIntList exceededQuotaIDs`. Constants derive maximum ID counts from `NETMSG_MAX_PAYLOAD_SIZE`.

### Control Flow
Senders fill the exceeded ID list through `getExceededQuotaIDs()`. Receivers deserialize the same list and update quota state.

### State, Persistence, And Dependencies
The message is transient but updates persistent or cached quota-exceeded stores. It depends on `StoragePoolStore`, `QuotaData`, and list serdes.

### Integration Points
Management/storage quota synchronization uses this message, and `RequestExceededQuotaRespMsg` reuses it as a base payload.

### Risks
The ID list is mutable by pointer, so callers can exceed maximum advisory counts unless checked elsewhere. Subclass message-type constructors rely on the same layout. Tests should cover empty and max-sized lists, storage pool IDs, user/group and size/inode combinations, and subclass serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetExceededQuotaMsg.h -->
