# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/resources/hdfs-site.xml

## Purpose
Test HDFS site override used by HttpFS/HDFS tests.

## Important APIs, Types, And Functions
Defines `dfs.namenode.fs-limits.min-block-size=0` in Hadoop XML configuration format.

## Control Flow
Loaded by Hadoop configuration machinery from test resources; there is no procedural control flow.

## State, Persistence, And Dependencies
The property changes in-memory test configuration and allows very small block sizes. It does not persist runtime state.

## Integration Points
Applies to tests that create tiny files or blocks in MiniDFS/HttpFS scenarios where production NameNode minimum block-size validation would otherwise reject inputs.

## Risks
Behavior differs from production defaults, so tests may pass with unrealistically small blocks. XML shape must remain standard `<configuration><property><name>...`.

## Test Signals
Failures involving tiny block-size creation can indicate this resource was not on the test classpath or the property was overridden later.
