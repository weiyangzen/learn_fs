<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/storage/StatData.c -->
## sources/distributed-fs/beegfs/client_module/source/common/storage/StatData.c

**Purpose:** Deserializes server-provided stat metadata into `StatData`. **APIs/functions:** `StatData_deserialize`. **Control flow:** reads flags, mode, block count, creation/access/modification/ctime, file size, link count, metadata version, uid, and gid in protocol order, returning false on the first decode failure. **State/persistence:** materializes wire stat data for conversion to kernel-facing `fhgfs_stat`. **Dependencies/integration:** used by lookup/stat response parsing and `LookupIntentInfoOut`. **Risks/tests:** field order must stay in sync with server/common code; tests should verify all timestamp/size/uid fields and failure on truncated buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/storage/StatData.c -->
