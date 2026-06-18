<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/storage/StoragePoolId.h -->
## sources/distributed-fs/beegfs/client_module/source/common/storage/StoragePoolId.h

**Purpose:** Defines the client storage pool ID wrapper. **APIs/types:** `StoragePoolId` contains `uint16_t value`; inline helpers set, compare, stringify, plus serialize/deserialize externs; `STORAGEPOOLID_INVALIDPOOLID` is 0. **Control flow/state:** simple value object with caller-owned string returned by `StoragePoolId_str`. **Dependencies/integration:** included by stripe pattern serialization/deserialization. **Risks/tests:** protocol compatibility depends on server-side value width; tests should cover comparison and string conversion ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/storage/StoragePoolId.h -->
