<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/GetQuotaInfoRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/GetQuotaInfoRespMsg.h

### Purpose
`GetQuotaInfoRespMsg` returns quota data records and quota-inode support status.

### Important APIs, Types, And Functions
The class derives from `NetMessageSerdes<GetQuotaInfoRespMsg>` with `NETMSGTYPE_GetQuotaInfoResp`. It defines maximum payload-derived quota record counts. Serialization writes `quotaInodeSupport` and a backed `QuotaDataList`. Getters expose the data list and cast inode support to `QuotaInodeSupport`.

### Control Flow
Management-server responses can use `QuotaInodeSupport_UNKNOWN`; storage-server responses can set concrete support. Deserialization populates `parsed.quotaData`.

### State, Persistence, And Dependencies
The message is a transient quota snapshot. It depends on `QuotaData`, `Quota`, `NETMSG_MAX_PAYLOAD_SIZE`, and list serdes.

### Integration Points
Quota reporting, enforcement refresh, and management queries consume this response.

### Risks
Maximum record constants are advisory here; senders must enforce list sizing before serialization. The send-side list pointer is non-owned. Tests should cover empty lists, maximum-sized lists, inode-support states, and over-limit rejection in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/GetQuotaInfoRespMsg.h -->
