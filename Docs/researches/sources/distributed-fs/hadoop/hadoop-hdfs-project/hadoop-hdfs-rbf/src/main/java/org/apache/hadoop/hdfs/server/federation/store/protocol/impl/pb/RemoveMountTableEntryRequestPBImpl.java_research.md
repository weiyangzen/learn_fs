<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/RemoveMountTableEntryRequestPBImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/RemoveMountTableEntryRequestPBImpl.java

## Purpose
PB request for removing a mount table entry by source path.

## APIs, Types, and Functions
Implements `PBRecord` for `RemoveMountTableEntryRequestProto`. The domain API is `getSrcPath()` and `setSrcPath(String)`, mapped to proto field `srcPath`.

## Control Flow, State, and Persistence
Admin code normalizes a source path, builds this request, and sends it to `MountTableManager.removeMountTableEntry()`. The server uses `srcPath` as the primary key for deleting a `MountTable` record from the State Store and refreshing caches as needed.

## Dependencies and Integration
Used by `RouterAdmin.removeMount()`, Router admin protocol translators, and mount-table cache refresh tests. It depends on generated federation protos and the common PB translator.

## Risks and Test Signals
This class does not normalize or validate paths; callers and server-side stores must enforce valid absolute mount paths. Tests that remove entries through the admin API and then verify cache/listing behavior are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/RemoveMountTableEntryRequestPBImpl.java -->
