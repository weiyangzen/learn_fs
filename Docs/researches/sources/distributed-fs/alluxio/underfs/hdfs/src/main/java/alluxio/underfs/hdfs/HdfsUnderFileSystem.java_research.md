## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsUnderFileSystem.java

### Purpose
`HdfsUnderFileSystem` is Alluxio's HDFS-backed `ConsistentUnderFileSystem`. It implements file creation, deletion, status, listing, space reporting, locations, reads, writes, renames, permissions, Kerberos login, ACL delegation, and ActiveSync delegation.

### Important APIs, Types, And Functions
`createInstance` builds Hadoop configuration. The constructor initializes Hadoop UGI/classloader state, optional EC support, a cached `FileSystem`, reflected `HdfsAclProvider`, and reflected `HdfsActiveSyncProvider`. Key overrides include `createDirect`, `deleteDirectory`, `exists`, `getAclPair`, `getBlockSizeByte`, `getDirectoryStatus`, `getFileLocations`, `getFileStatus`, `getSpace`, `getStatus`, `listStatus`, `mkdirs`, `open`, `renameFile`, `renameDirectory`, `setOwner`, `setMode`, and active-sync methods.

### Control Flow
Configuration loads `UNDERFS_HDFS_CONFIGURATION`, `UNDERFS_HDFS_IMPL`, mount-specific options, and disables HDFS client caching by default. Create/delete/mkdir/open/rename operations retry up to `MAX_TRY`. Atomic creates return `AtomicFileOutputStream`; direct creates call Hadoop `FileSystem.create` and optionally set ACLs. Reads choose positioned pread streams for remote/short/nonlocal reads and normal seekable streams otherwise. Open can try lease recovery on specific block-length errors. Recursive directory creation builds missing parents explicitly to set permissions and owner.

### State, Persistence, And Dependencies
State includes UFS configuration, a Guava `LoadingCache` of `FileSystem` by user key, ACL provider, active-sync provider, and Hadoop configuration captured by the loader. Persistent state is in HDFS. Dependencies are Hadoop FS/security/HDFS APIs, Alluxio UFS status/options, retry policies, networking utilities, and generated `UfsConstants`.

### Integration Points
`HdfsUnderFileSystemFactory` creates this class for configured HDFS prefixes. The HDFS stream wrappers provide read/write behavior. ACL and ActiveSync support are optional profile-dependent classes loaded by reflection, allowing older Hadoop deployments to run with no-op providers.

### Risks
The file-system cache currently uses a constant empty user key, so true per-user Hadoop clients are not implemented. Close intentionally does not close Hadoop `FileSystem` singletons. Version gating for EC uses string comparison. Many operations log and retry broad IOExceptions, which can duplicate non-idempotent attempts if Hadoop semantics change. Permission changes may be ignored when configured to allow owner failures.

### Test Signals
`HdfsUnderFileSystemTest` validates type, configuration preparation, and positioned-read heuristics. Factory and version tests cover discovery and version parsing, but many behaviors such as ACLs, ActiveSync, Kerberos login, lease recovery, and real HDFS space/location calls need integration coverage.
