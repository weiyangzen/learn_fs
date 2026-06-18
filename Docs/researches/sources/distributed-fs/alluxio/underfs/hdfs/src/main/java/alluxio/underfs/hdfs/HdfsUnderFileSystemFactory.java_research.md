## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsUnderFileSystemFactory.java

### Purpose
`HdfsUnderFileSystemFactory` registers and creates HDFS UFS instances for configured HDFS-like path prefixes.

### Important APIs, Types, And Functions
It implements `UnderFileSystemFactory`. `create` returns `HdfsUnderFileSystem.createInstance`. `supportsPath(String)` checks global `UNDERFS_HDFS_PREFIXES`. `supportsPath(String, UnderFileSystemConfiguration)` also honors user-set `UNDERFS_VERSION` through `HdfsVersion.matches`. `getVersion` returns generated Hadoop UFS version.

### Control Flow
Path support scans configured prefixes and accepts the first prefix match. The configuration-aware overload additionally rejects mismatched user-requested Hadoop versions.

### State, Persistence, And Dependencies
The factory is stateless. It depends on global Alluxio configuration for prefixes, per-mount UFS configuration for version constraints, `HdfsVersion`, and generated `UfsConstants`.

### Integration Points
The UFS factory registry uses this factory to route `hdfs://` and other configured HDFS-compatible schemes to the HDFS module.

### Risks
The no-configuration overload uses global configuration only, and comments note programmatic prefix updates may not work as expected. Prefix matching is simple `startsWith`, so configuration quality matters. Version matching depends on `HdfsVersion` patterns.

### Test Signals
`HdfsUnderFileSystemFactoryTest` verifies `hdfs://` is accepted and S3/Alluxio paths are rejected.
