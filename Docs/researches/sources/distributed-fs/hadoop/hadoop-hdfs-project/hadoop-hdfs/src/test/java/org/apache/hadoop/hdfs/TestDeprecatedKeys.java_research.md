# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDeprecatedKeys.java

## Purpose
`TestDeprecatedKeys` validates backward-compatible Hadoop configuration key aliases used by HDFS. It ensures deprecated property names still populate the modern `DFSConfigKeys` names and, for some keys, that old and new names read back the same configured value.

## Important APIs, Types, and Functions
The single test method `testDeprecatedKeys()` uses `HdfsConfiguration`, `Configuration.set`, `setInt`, `setBoolean`, `setDouble`, and corresponding getters. It checks `DFSConfigKeys.NET_TOPOLOGY_SCRIPT_FILE_NAME_KEY`, `DFS_NAMENODE_REDUNDANCY_INTERVAL_SECONDS_KEY`, `DFS_NAMENODE_REDUNDANCY_CONSIDERLOAD_KEY`, and `DFS_NAMENODE_REDUNDANCY_CONSIDERLOAD_FACTOR`.

## Control Flow
The test creates a new `HdfsConfiguration`, writes deprecated keys such as `topology.script.file.name`, `dfs.replication.interval`, `dfs.replication.considerLoad`, and `dfs.namenode.replication.considerLoad.factor`, then immediately reads modern and legacy aliases. Assertions verify string, integer, boolean, and double values are propagated through the deprecation map.

## State and Persistence Behavior
All state is in-memory `Configuration` state. No cluster, filesystem, XML file, or persistent store is created. The test relies on HDFS configuration initialization registering deprecated keys before lookups occur.

## Dependencies and Integration Points
This is integration coverage between `HdfsConfiguration` static deprecation registration and the generic `Configuration` alias-resolution system. The downstream integration point is any HDFS code that reads only the modern `DFSConfigKeys` constants while users still configure old property names.

## Risks
The test is small but high leverage: removing or renaming deprecated aliases can silently change user deployments. The direct floating-point equality check is safe because the test writes and reads the same literal `5.0`, not a computed value. Additions to deprecation handling should include old-to-new and old-to-old readback when legacy keys remain documented.

## Test Signals
Passing means deprecated topology, redundancy interval, load-consideration, and load-factor keys resolve as expected. Failure indicates a compatibility regression in configuration alias registration or lookup precedence.
