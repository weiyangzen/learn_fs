<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/storage/StatData.h -->
## sources/distributed-fs/beegfs/client_module/source/common/storage/StatData.h

**Purpose:** Defines file stat metadata and conversion to the client VFS-facing stat structure. **APIs/types:** `STATDATA_FEATURE_SPARSE_FILE`, block-size shift, `StatData` fields, `StatData_deserialize`, and inline `StatData_getOsStat`. **Control flow/state:** conversion copies mode, size, blocks, uid/gid, nlink, atime/mtime/ctime seconds with zero nsec, and metadata version into `fhgfs_stat`. **Dependencies/integration:** uses storage definitions and BeeGFS stat types; consumed by lookup intent and stat paths. **Risks/tests:** only second-resolution times are preserved; tests should cover sparse flag propagation where used and exact `fhgfs_stat` field mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/storage/StatData.h -->
