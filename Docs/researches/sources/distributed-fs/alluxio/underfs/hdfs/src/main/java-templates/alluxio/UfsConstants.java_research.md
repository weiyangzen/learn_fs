## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java-templates/alluxio/UfsConstants.java

### Purpose
This template generates compile-time constants for the HDFS UFS module.

### Important APIs, Types, And Functions
It defines `UfsConstants.UFS_HADOOP_VERSION`, filled from Maven property `${ufs.hadoop.version}`, and has a private constructor.

### Control Flow
The templating plugin filters this source into generated Java sources during the Maven build.

### State, Persistence, And Dependencies
There is no runtime mutable state. The generated constant persists in the compiled extension jar.

### Integration Points
`HdfsUnderFileSystemFactory.getVersion` returns this value, and `HdfsUnderFileSystem` compares it to the EC minimum version when initializing Hadoop erasure-coding classes.

### Risks
String comparison is later used for a semantic version gate, so nonstandard version strings could produce incorrect ordering. A missing template filtering step would leave the placeholder literal in the runtime class.

### Test Signals
`HdfsVersionTest` checks parsing/matching behavior around Hadoop labels, indirectly protecting callers that compare configured versions to this constant.
