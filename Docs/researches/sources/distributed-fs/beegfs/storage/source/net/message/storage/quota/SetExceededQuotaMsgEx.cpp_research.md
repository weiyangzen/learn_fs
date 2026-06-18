<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/quota/SetExceededQuotaMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/quota/SetExceededQuotaMsgEx.cpp

### Purpose
Receives quota-exceeded ID sets from management and updates local exceeded-quota stores for targets in the referenced storage pool.

### Important APIs, Types, And Functions
processIncoming() checks Config::getQuotaEnableEnforcement(), resolves the StoragePool by getStoragePoolId(), iterates local StorageTargets, and calls ExceededQuotaStores::get(targetID)->updateExceededQuota() for pool members. It responds with SetExceededQuotaRespMsg.

### Control Flow
If enforcement is disabled it logs a configuration mismatch and returns INTERNAL. If the pool is unknown it logs a warning and returns UNKNOWNPOOL. Otherwise it updates each matching target store and returns SUCCESS.

### State, Persistence, And Dependencies
Runtime quota-enforcement state is mutated in per-target exceeded quota stores. Persistence depends on the store implementation outside this file; no disk IO is performed directly here. Depends on Program/App, Config, StoragePoolStore, StoragePool membership, StorageTargets, ExceededQuotaStores, quota data type/exceeded type fields, and common response message.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include silent success when a known pool contains no local targets, configuration skew between management and storage nodes, and all-or-nothing response not identifying per-target update failures.

### Test Signals
Test signals include enforcement disabled, unknown pool, pool with multiple local targets, pool with no local targets, user/group quota types, and replacement of previous exceeded ID sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/quota/SetExceededQuotaMsgEx.cpp -->
