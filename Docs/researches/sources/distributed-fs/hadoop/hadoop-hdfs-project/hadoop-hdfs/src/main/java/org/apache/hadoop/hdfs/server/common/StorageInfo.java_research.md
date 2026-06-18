<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/StorageInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/StorageInfo.java

## Purpose

`StorageInfo` holds the common identity and compatibility fields read from HDFS storage `VERSION` files: layout version, namespace ID, cluster ID, creation time, and node type.

## Important APIs and types

It exposes getters, `setStorageInfo`, string conversions, colon-separated parsing helpers, `readProperties`, `readPreviousVersionProperties`, `setFieldsFromProperties`, validation setters for layout, namespace, cluster ID, cTime, and storage type, plus service layout-version/feature-map accessors. `readPropertiesFile` loads Java properties from a `RandomAccessFile`.

## Control flow

Reading a VERSION file loads properties, then sets layout version, namespace ID, cTime, cluster ID if federation is supported, and validates storage type. Future layout versions are rejected with `IncorrectVersionException`; incompatible namespace or cluster IDs raise `InconsistentFSStateException`; missing properties raise `InconsistentFSStateException`.

## State and persistence behavior

Fields are mutable and reflect the currently loaded storage directory set. The data is persisted in `VERSION` files written by `Storage`. Cluster ID is only required for layout versions supporting federation.

## Dependencies and integration points

It integrates with `Storage.StorageDirectory`, `HdfsServerConstants.NodeType`, DataNode and NameNode layout-version feature maps, `LayoutVersion`, and storage startup.

## Risks and edge cases

Colon-separated parsing blindly splits on `:`, so malformed strings throw runtime parsing exceptions. `readPropertiesFile` opens files as `rws`, which can imply write intent for a read operation. Namespace/cluster compatibility allows zero/empty values as unset placeholders.

## Test signals

Tests should cover missing properties, incompatible namespace/cluster IDs, future layout rejection, storage type mismatch, federation and pre-federation cluster ID handling, previous version reads, and string/colon round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/StorageInfo.java -->
