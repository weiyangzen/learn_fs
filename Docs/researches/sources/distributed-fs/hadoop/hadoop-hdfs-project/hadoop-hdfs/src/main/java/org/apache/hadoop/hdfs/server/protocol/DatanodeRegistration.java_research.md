<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeRegistration.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeRegistration.java

## Purpose

`DatanodeRegistration` carries the identity and compatibility information a DataNode sends to the NameNode for registration and subsequent RPCs. It combines network identity from `DatanodeID` with storage layout metadata, block-token keys, software version, and optional namespace info.

## Important APIs and types

The class extends `DatanodeID` and implements `NodeRegistration`. Fields include `StorageInfo storageInfo`, mutable `ExportedBlockKeys exportedKeys`, `softwareVersion`, and mutable `NamespaceInfo nsInfo`. It exposes getters, `setExportedKeys`, `setNamespaceInfo`, `getRegistrationID()`, `getAddress()`, `getVersion()`, and a detailed `toString()`.

## Control flow

DataNodes construct registrations from their ID, storage info, exported keys, and software version. The NameNode may return updated registration data including block keys. Registration ID is derived from storage info using `Storage.getRegistrationID`.

## State and persistence behavior

The object mirrors persistent DataNode storage metadata but does not persist it. Equality and hash code defer entirely to `DatanodeID`, so storage info and exported keys are not part of equality.

## Dependencies and integration points

It integrates `DatanodeID`, `StorageInfo`, `Storage`, `ExportedBlockKeys`, `NamespaceInfo`, and registration checks in NameNode code. Tests use the visible-for-testing constructor to substitute UUIDs.

## Risks and test signals

Risks include equality ignoring storage state, stale exported keys, namespace info being unset, and registration IDs changing with layout/namespace metadata. Tests should cover registration round trips, block-key update propagation, storage compatibility checks, and equality/hash behavior when UUIDs differ but storage fields match.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeRegistration.java -->
