## sources/distributed-fs/alluxio/underfs/hdfs/src/test/java/alluxio/underfs/hdfs/HdfsVersionTest.java

### Purpose
`HdfsVersionTest` validates version-string normalization for all supported Hadoop version families.

### Important APIs, Types, And Functions
`find()` checks invalid input and canonical version strings. `findByHadoopLabel()` checks plain numeric, snapshot, `hadoop-`, `hadoop-<patch>`, and `hadoop<major.minor>` labels for every enum value.

### Control Flow
Assertions directly call `HdfsVersion.find` and compare returned enum values.

### State, Persistence, And Dependencies
No state is mutated. It depends only on JUnit and `HdfsVersion`.

### Integration Points
The test protects factory version compatibility checks that use `HdfsVersion.matches`.

### Risks
It does not test `matches` directly or newer versions beyond the enum list.

### Test Signals
Failures indicate a regex or canonical label drift that can prevent correctly versioned HDFS UFS modules from matching mount configuration.
