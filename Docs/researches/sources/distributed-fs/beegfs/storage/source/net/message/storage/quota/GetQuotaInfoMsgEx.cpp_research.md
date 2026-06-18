<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/quota/GetQuotaInfoMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/quota/GetQuotaInfoMsgEx.cpp

### Purpose
Handles quota information queries against one or more local storage target block devices.

### Important APIs, Types, And Functions
processIncoming() reads target selection, query type, ID range/list, quota type, and targetNumID from GetQuotaInfoMsg. It builds a QuotaBlockDeviceMap, tracks QuotaInodeSupport, uses a ZfsSession, and calls QuotaTk helpers before sending GetQuotaInfoRespMsg.

### Control Flow
For all-target requests it iterates StorageTargets and records each QuotaBlockDevice, deriving inode-quota support as none/some/all. For per-target and single-target requests it adds only the requested target if present. It then handles single ID, ID range, or ID list queries through QuotaTk and returns the accumulated QuotaDataList even when no block devices were found.

### State, Persistence, And Dependencies
No storage data is mutated. Runtime state is the transient ZfsSession, which may initialize libzfs handles for the request. The response carries quota usage and inode support classification. Depends on Program/App, StorageTargets, QuotaBlockDevice, QuotaTk, ZfsSession, quota config enums, and common response serialization.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include logging but not returning an explicit error for empty target/block-device selection, potentially expensive range queries, and mixed inode quota support requiring callers to interpret QuotaInodeSupport correctly.

### Test Signals
Test signals include all-target aggregation, single-target missing, ID list/range/single query types, mixed filesystem inode support, ZFS session initialization failure, and ext/XFS quotactl errors mapped by QuotaTk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/quota/GetQuotaInfoMsgEx.cpp -->
