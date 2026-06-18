<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/namenode_info.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/namenode_info.h

## Purpose
Declares resolved namenode metadata and resolver helpers used by connection and failover code.

## Important APIs, Types, And Functions
`ResolvedNamenodeInfo` extends `NamenodeInfo` with a vector of Boost TCP endpoints plus assignment and `str()`. Free functions `BulkResolve` and `ResolveInPlace` perform asynchronous DNS resolution using an `IoService`.

## Control Flow
Implementation lives in `namenode_info.cc`; callers pass configured namenodes and receive endpoint-populated copies.

## State And Persistence
State is returned in value objects. No persistent cache is declared here.

## Dependencies And Integration Points
Used by filesystem connection logic after `HdfsConfiguration` parses `NamenodeInfo` records from Hadoop XML.

## Risks
The header comment for `BulkResolve` does not perfectly match implementation behavior for failed resolutions, so callers should check `endpoints`.

## Test Signals
Tests should validate endpoint vectors and string formatting for resolved and unresolved nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/namenode_info.h -->
