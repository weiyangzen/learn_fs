<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/RequestExceededQuotaRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/RequestExceededQuotaRespMsg.h

### Purpose
`RequestExceededQuotaRespMsg` returns exceeded quota IDs using the same base payload shape as `SetExceededQuotaMsg`, plus an explicit error code.

### Important APIs, Types, And Functions
It subclasses `SetExceededQuotaMsg` but overrides payload serialization by defining `serializePayload()`, `deserializePayload()`, and a local static `serialize()` that serializes the base plus `error`. It reuses the base maximum-size constants.

### Control Flow
The base portion carries storage pool, quota data type, exceeded type, and ID list; the trailing `error` communicates whether the request succeeded. The default constructor uses message type `NETMSGTYPE_RequestExceededQuotaResp` and initializes error to `FhgfsOpsErr_INVAL`.

### State, Persistence, And Dependencies
The response is transient. It depends on `SetExceededQuotaMsg`, quota enums, and explicit serializer/deserializer override behavior.

### Integration Points
Quota query callers use it to receive exceeded IDs from stores while still getting request status.

### Risks
Subclassing a serdes message and overriding payload serialization is delicate; dispatch must use this class's serialize, not the base version. Tests should cover base-list round-trip, error-code round-trip, empty exceeded list, and payload-size limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/RequestExceededQuotaRespMsg.h -->
