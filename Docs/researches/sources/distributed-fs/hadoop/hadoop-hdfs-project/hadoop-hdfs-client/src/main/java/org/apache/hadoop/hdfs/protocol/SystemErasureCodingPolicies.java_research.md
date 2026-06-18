# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/SystemErasureCodingPolicies.java

## Purpose
`SystemErasureCodingPolicies` defines Hadoop HDFS's built-in erasure coding policies. Although the class is private, its policy IDs are effectively stable wire/storage compatibility points because older clients and NameNodes rely on consistent IDs.

## Important APIs, Types, and Functions
The class defines byte IDs for `RS_6_3`, `RS_3_2`, `RS_6_3_LEGACY`, `XOR_2_1`, and `RS_10_4`, all with a default 1 MiB cell size. It also defines a special replication policy using `ErasureCodeConstants.REPLICATION_POLICY_ID`.

`SYS_POLICIES` is an unmodifiable list of the EC policies, excluding the replication policy. Static maps `SYSTEM_POLICIES_BY_NAME` and `SYSTEM_POLICIES_BY_ID` are populated at class load. Public static accessors are `getPolicies`, `getByID`, `getByName`, and `getReplicationPolicy`.

## Control Flow
The static initializer iterates over `SYS_POLICIES` and builds name/id lookup maps. Runtime calls are simple lookups or list returns.

## State and Persistence Behavior
All state is static and process-local. Policy IDs and schema names must remain stable across releases because they are stored in metadata and exchanged with clients. `getPolicies` returns an unmodifiable list, and maps are private.

## Dependencies and Integration Points
It depends on `ErasureCodingPolicy` and `ErasureCodeConstants`. It integrates with NameNode policy management, client APIs that list/query EC policies, PB conversion, and DataTransferProtocol block-group checksum paths.

## Risks and Edge Cases
Changing IDs, removing policies, or changing default cell size for existing IDs can create cross-version inconsistency. `getByID` and `getByName` return `null` for unknown values, so callers need validation. The replication policy is not included in `getPolicies`, which is intentional and should be documented in callers.

## Test Signals
Erasure-coding API tests should assert built-in names, IDs, and lookup behavior. Compatibility tests should pin the exact ID-to-schema mapping and replication-policy special handling.
