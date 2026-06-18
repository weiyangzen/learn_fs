<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NamenodeRegistration.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NamenodeRegistration.java

## Purpose

`NamenodeRegistration` carries subordinate NameNode identity during registration with an active NameNode. It includes RPC/HTTP addresses, storage information, and the subordinate node role.

## Important APIs and types

The class extends `StorageInfo` and implements `NodeRegistration`. Fields are `rpcAddress`, `httpAddress`, and `NamenodeRole role`. Methods include `getAddress()`, `getHttpAddress()`, `getRegistrationID()`, `getVersion()`, `getRole()`, `isRole()`, and `toString()`.

## Control flow

A backup or checkpoint NameNode builds this object and calls `NamenodeProtocol.registerSubordinateNamenode`. The active NameNode uses storage identity and role to validate and track the subordinate.

## State and persistence behavior

The object is transient, reflecting persistent NameNode storage layout, namespace ID, cluster ID, and creation time inherited from `StorageInfo`.

## Dependencies and integration points

It depends on `Storage`, `StorageInfo`, `HdfsServerConstants.NamenodeRole`, and `NodeRegistration`. It integrates with checkpoint/backup NameNode registration and diagnostics.

## Risks and test signals

Risks include stale storage identity, wrong role checks, and address mismatches. Tests should cover registration ID derivation, role matching, toString output, and rejection of incompatible storage info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NamenodeRegistration.java -->
