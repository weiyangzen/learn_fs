<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/storage/StoragePoolId.c -->
## sources/distributed-fs/beegfs/client_module/source/common/storage/StoragePoolId.c

**Purpose:** Implements serialization for storage pool IDs. **APIs/functions:** `StoragePoolId_serialize` writes the 16-bit value; `StoragePoolId_deserialize` reads it and returns false on buffer failure. **Control flow/state:** no allocation or validation beyond decoding. **Dependencies/integration:** used in stripe-pattern headers even when the client currently does not use pool IDs, preserving protocol compatibility. **Risks/tests:** width must remain in sync with server `StoragePoolId`; tests should round-trip invalid pool ID 0 and normal pool IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/storage/StoragePoolId.c -->
