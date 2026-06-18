## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/NoopHdfsAclProvider.java

### Purpose
`NoopHdfsAclProvider` is the fallback ACL provider when HDFS ACL support is unavailable or excluded from the build.

### Important APIs, Types, And Functions
`getAcl` returns a pair of null ACLs. `setAclEntries` accepts entries but performs no operation.

### Control Flow
All calls return immediately with unsupported/no-op behavior.

### State, Persistence, And Dependencies
There is no state and no HDFS mutation. It depends on the provider interface and Alluxio ACL types.

### Integration Points
`HdfsUnderFileSystem` uses this provider by default before trying to reflectively instantiate `SupportedHdfsAclProvider`.

### Risks
Silent no-op behavior can hide missing build profiles or disabled Hadoop ACL support unless logs from provider selection are monitored.

### Test Signals
No direct tests are present. Provider fallback is exercised when the supported ACL class is absent from the classpath.
