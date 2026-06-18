<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/storage/StorageErrors.h -->
## sources/distributed-fs/beegfs/client_module/source/common/storage/StorageErrors.h

**Purpose:** Defines the BeeGFS operation error enum shared with common/server code. **APIs/types:** `FhgfsOpsErrListEntry`, extern error table, signed `FhgfsOpsErr` enum from success through remote I/O, and conversion functions. **Control flow/state:** the negative dummy forces a signed enum because some code casts errors to negative integer widths. **Dependencies/integration:** returned by metadata/storage messages, `MessagingTk`, target/mirror management, and VFS translation. **Risks/tests:** adding enum values requires updating the table in exact order and external protocol compatibility; tests should check signedness behavior and conversion bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/storage/StorageErrors.h -->
