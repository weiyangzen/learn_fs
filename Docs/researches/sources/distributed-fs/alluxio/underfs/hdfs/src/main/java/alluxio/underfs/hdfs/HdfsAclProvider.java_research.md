## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsAclProvider.java

### Purpose
`HdfsAclProvider` defines the abstraction for retrieving and setting HDFS ACLs without forcing all builds to compile against ACL-capable Hadoop APIs.

### Important APIs, Types, And Functions
`getAcl(FileSystem, String)` returns an Alluxio ACL/default-ACL pair or null values when ACLs are unsupported. `setAclEntries(FileSystem, String, List<AclEntry>)` writes Alluxio ACL entries to HDFS.

### Control Flow
This interface has no implementation flow. Callers use it through either `SupportedHdfsAclProvider` or `NoopHdfsAclProvider`.

### State, Persistence, And Dependencies
No state is defined. It depends on Hadoop `FileSystem` and Alluxio authorization types.

### Integration Points
`HdfsUnderFileSystem` instantiates a provider by reflection and delegates `getAclPair` and `setAclEntries`.

### Risks
Returning a pair of nulls for unsupported ACLs requires callers to distinguish unsupported from an empty ACL. Implementations must handle files and directories differently for default ACLs.

### Test Signals
There are no direct interface tests. Coverage comes from UFS ACL behavior when supported providers are active.
