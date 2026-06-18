## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsVersion.java

### Purpose
`HdfsVersion` enumerates supported Hadoop/HDFS major-minor versions and normalizes several version string formats to canonical values.

### Important APIs, Types, And Functions
Enum values cover Hadoop 1.0, 1.2, 2.2 through 2.10, and 3.0 through 3.3. `find(String)` returns the enum whose regex matches. `matches(String, String)` accepts exact equality or both strings resolving to the same enum. `getCanonicalVersion()` returns labels like `hadoop-3.3`.

### Control Flow
`find` iterates enum values in declaration order and uses precompiled regex patterns. `matches` first checks direct equality, then compares normalized enum values.

### State, Persistence, And Dependencies
State is immutable enum metadata and compiled regexes. It depends only on Java regex and nullable annotations.

### Integration Points
`HdfsUnderFileSystemFactory.supportsPath` uses it to compare user-requested UFS version with the module's compiled Hadoop version.

### Risks
Only declared versions are recognized; newer Hadoop versions require enum updates. Regexes are permissive for suffixes but only by major-minor family, not patch-level compatibility rules.

### Test Signals
`HdfsVersionTest` validates canonical names plus plain and `hadoop-`/`hadoop` labels with snapshot suffixes across all enum values.
