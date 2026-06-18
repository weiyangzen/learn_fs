# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestBootstrapAliasmap.java

## Purpose

`TestBootstrapAliasmap` verifies that a provided-storage in-memory LevelDB aliasmap can be downloaded from a NameNode and started from the downloaded directory with the same block pool ID and entries.

## Important APIs, Types, and Functions

The setup calls `MiniDFSCluster.setupNamenodeProvidedConfiguration`, assigns a free aliasmap RPC port, and starts a one-DataNode cluster. The test uses `InMemoryLevelDBAliasMapServer`, `Block`, `ProvidedStorageLocation`, `TransferFsImage.downloadAliasMap`, `DFSUtil.getInfoServerWithDefaultHost`, and a new server constructed with `InMemoryAliasMap::init`.

## Control Flow

The test writes two block-to-location mappings into the running NameNode aliasmap server, downloads the aliasmap over the NameNode HTTP image-transfer path into a fresh directory, configures a second aliasmap server to use that directory and a free RPC address, starts it, then lists and reads mappings.

## State and Persistence Behavior

Aliasmap entries are persisted in the LevelDB directory copied by `downloadAliasMap`. The test also verifies the block pool ID survives into the new server.

## Dependencies and Integration Points

It integrates provided storage configuration, aliasmap RPC/server lifecycle, NameNode HTTP transfer, LevelDB-backed aliasmap persistence, and block pool identity.

## Risks and Edge Cases

The test assumes the HTTP endpoint transfers a complete aliasmap snapshot and that the new server can start independently from the copied directory. Free port selection avoids default port conflicts.

## Test Signals

Signals are exactly two listed file regions, non-null reads for both blocks, and `newServer.getBlockPoolId()` equal to the source NameNode block pool ID.
