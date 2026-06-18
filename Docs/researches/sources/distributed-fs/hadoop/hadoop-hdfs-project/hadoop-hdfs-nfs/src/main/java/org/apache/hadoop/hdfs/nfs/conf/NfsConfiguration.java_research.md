<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/conf/NfsConfiguration.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/conf/NfsConfiguration.java

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/conf/NfsConfiguration.java` extends `HdfsConfiguration` for the NFS gateway and registers deprecated configuration key mappings. The source was read as a complete 73-line file for this report.

## Important APIs, Types, and Functions

`NfsConfiguration` has a static initializer that calls `addDeprecatedKeys()`. The helper registers `Configuration.DeprecationDelta` mappings from older `nfs3.*`, `dfs.nfs3.*`, and related keys to current `NfsConfigKeys`, `Nfs3Constant`, and `IdMappingConstant` names.

## Control Flow

When the class is loaded, Hadoop's global configuration deprecation table is updated. Gateway startup then uses this subclass so old XML properties remain readable under new keys.

## State and Persistence Behavior

No instance state is added beyond `HdfsConfiguration`. The persistent effect is process-global deprecation metadata inside Hadoop configuration handling.

## Dependencies and Integration Points

It integrates HDFS configuration defaults, NFS constants, and user/group ID mapping constants. `Mountd` and `Nfs3` create this configuration at startup.

## Risks and Edge Cases

Missing a deprecation mapping silently breaks compatibility for existing deployments. Since mappings are process-global, test isolation must account for static registration.

## Test Signals

Configuration tests should set deprecated keys and assert current keys resolve to the same values; gateway startup with legacy XML names is the best integration signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/conf/NfsConfiguration.java -->
