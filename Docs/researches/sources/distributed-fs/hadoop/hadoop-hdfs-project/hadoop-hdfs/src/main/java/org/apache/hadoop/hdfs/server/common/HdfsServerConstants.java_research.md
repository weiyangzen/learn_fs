<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/HdfsServerConstants.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/HdfsServerConstants.java

## Purpose

`HdfsServerConstants` centralizes internal HDFS server constants and enums for startup modes, node roles, replica states, block-under-construction states, layout versions, reserved paths, xattrs, and block ID encoding.

## Important APIs and types

Key enums are `NodeType`, `RollingUpgradeStartupOption`, `StartupOption`, `NamenodeRole`, `ReplicaState`, and `BlockUCState`. Constants include path limits, invalid transaction ID, legacy generation-stamp reservation, NameNode layout versions, reserved path components, crypto/security/xattr names, mover ID path, block-group index mask, maximum blocks per group, and maximum DataNode bandwidth.

## Control flow

`RollingUpgradeStartupOption.fromString` rejects the removed `downgrade` option and parses allowed values. `StartupOption` stores mutable option-specific state such as cluster ID, rolling-upgrade option, force/noninteractive format flags, and recovery force level; `getEnum` parses persisted enum strings with rolling-upgrade suboptions. `ReplicaState` serializes by ordinal byte and validates ordinals on read.

## State and persistence behavior

Most constants are static. `StartupOption` enum instances contain mutable fields, so option parsing changes enum singleton state. `ReplicaState` ordinal serialization is persisted/on-wire sensitive and must remain append-compatible with layout-version gating.

## Dependencies and integration points

It integrates with NameNode startup, rolling upgrade, recovery, storage layout versions, FSDirectory reserved names, replica state reports, block construction, xattrs, and EC block group encoding.

## Risks and edge cases

Mutable enum fields can leak between parses/tests if not reset. `ReplicaState` ordinal changes are compatibility-sensitive. The rolling upgrade downgrade rejection embeds documentation text. Block-group constants must match `BlockIdManager` and sequential group ID generation.

## Test signals

Tests should cover startup option parsing/stringification, rolling-upgrade invalid values, recovery context creation, replica state read/write and invalid ordinals, reserved path/xattr constants, and EC block index mask assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/HdfsServerConstants.java -->
