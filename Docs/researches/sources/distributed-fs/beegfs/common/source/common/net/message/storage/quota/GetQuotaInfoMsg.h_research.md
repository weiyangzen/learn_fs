<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/GetQuotaInfoMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/GetQuotaInfoMsg.h

### Purpose
`GetQuotaInfoMsg` requests quota data for users or groups, scoped by query shape, target-selection mode, and storage pool.

### Important APIs, Types, And Functions
It derives from `NetMessageSerdes<GetQuotaInfoMsg>` with type `NETMSGTYPE_GetQuotaInfo`. `QuotaQueryType` covers none, single ID, ID range, ID list, and all IDs. Serialization writes query type and quota data type, then conditionally writes range/list/single-ID payload, followed by target selection, target ID, and `StoragePoolId`. Setter methods configure the query and target-selection modes.

### Control Flow
Handlers read `queryType` first to decide which ID field to consume. Target-selection values come from `GetQuotaConfig` constants and can request one target, one request per target, or all targets in one request.

### State, Persistence, And Dependencies
The message is transient. It depends on quota data enums, storage-pool IDs, management/storage target selection conventions, and NetMessage serdes.

### Integration Points
Management tools and quota collectors use this for quota scans, user/group lookups, and per-target storage quota retrieval.

### Risks
The constructor does not initialize `queryType`, `idRangeStart`, or `idRangeEnd`; callers must set a query before sending. ID-list size limits are not enforced in this header. Tests should cover every query type, target-selection setter, uninitialized/default construction safety, and payload limit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/GetQuotaInfoMsg.h -->
