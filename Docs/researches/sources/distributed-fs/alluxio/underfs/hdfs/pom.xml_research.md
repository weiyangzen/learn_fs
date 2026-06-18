## sources/distributed-fs/alluxio/underfs/hdfs/pom.xml

### Purpose
This Maven module builds the HDFS under file system extension and packages it against a configurable shaded Hadoop dependency.

### Important APIs, Types, And Functions
The artifact is `alluxio-underfs-hdfs`. Properties define `ufs.hadoop.version` and the versioned library jar name. Profiles choose `ufs-hadoop-2` or default `ufs-hadoop-3` and include `alluxio-shaded-hadoop`. Additional profiles optionally include ACL and ActiveSync support classes. The templating plugin generates `UfsConstants`.

### Control Flow
By default, compilation excludes `SupportedHdfsAclProvider` and `SupportedHdfsActiveSyncProvider`. Activating `hdfsAcl`, `hdfsActiveSync`, or `hdfsAclandActiveSync` overrides exclusions. Build plugins shade, copy/rename, filter templates, and preprocess sources.

### State, Persistence, And Dependencies
The build persists compiled extension artifacts and generated Java templates. Runtime code depends on `alluxio-core-common`, shaded Hadoop, and commons-lang3.

### Integration Points
The generated `alluxio.UfsConstants.UFS_HADOOP_VERSION` is read by HDFS factory/version logic and by HDFS EC class loading checks.

### Risks
Feature classes are excluded unless the right Maven profile is active, so runtime reflection in `HdfsUnderFileSystem` may silently fall back to no-op providers. Versioned jar naming must match deployment expectations.

### Test Signals
Module tests compile against the selected profile and validate factory discovery, version parsing, HDFS configuration, and positioned-read switching.
