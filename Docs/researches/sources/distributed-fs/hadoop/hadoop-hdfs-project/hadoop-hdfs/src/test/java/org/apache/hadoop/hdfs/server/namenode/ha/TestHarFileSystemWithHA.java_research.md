# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHarFileSystemWithHA.java

## Purpose
`TestHarFileSystemWithHA` verifies that `HarFileSystem` can resolve archives stored on an HA HDFS logical URI whose underlying HDFS URI has no explicit port.

## Important APIs, Types, And Functions
The single test is `testHarUriWithHaUriWithNoPort`; helper `createEmptyHarArchive` creates the minimal HAR structure. It uses `HdfsConfiguration`, `MiniDFSCluster`, `MiniDFSNNTopology.simpleHATopology`, `HATestUtil.setFailoverConfigurations`, `HATestUtil.configureFailoverFs`, `FileSystem.getDefaultUri`, `HarFileSystem.VERSION`, and `Path.getFileSystem`.

## Control Flow
The test starts a one-DataNode HA cluster, transitions NN0 active, configures HA failover, creates an empty HAR directory with `_masterindex` and `_index`, constructs a `har://hdfs-<logical-authority>/input.har` path, and asks that path for its filesystem.

## State And Persistence
Persistent state is the minimal HAR archive directory and metadata files in HDFS. Runtime state is the default logical HA URI in the configuration and the HAR filesystem URI parser/resolver.

## Dependencies And Integration Points
This test integrates HAR URI handling with HA logical HDFS authorities, default URI configuration, and failover filesystem setup.

## Risks
The bug class is URI parsing: HAR prepends `hdfs-` to the authority, and HA logical URIs often omit a physical port. Incorrect parsing can reject or misroute a valid archive path.

## Test Signals
The test passes if `Path.getFileSystem(conf)` succeeds for the constructed HAR path without throwing during resolution or archive initialization.
