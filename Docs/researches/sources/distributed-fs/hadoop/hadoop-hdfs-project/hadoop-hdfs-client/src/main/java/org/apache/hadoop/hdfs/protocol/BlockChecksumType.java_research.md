# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/BlockChecksumType.java

## Purpose
`BlockChecksumType` enumerates supported algorithms for computing block-level checksums from chunk checksums or CRCs.

## Important APIs, types, and functions
Values are `MD5CRC`, representing an MD5 digest over chunk CRCs, and `COMPOSITE_CRC`, representing chunk-independent CRC computation, optionally striped.

## Control flow
There is no executable behavior beyond enum value use.

## State and persistence behavior
Enum constants are stable protocol values. No local persistence occurs in this file.

## Dependencies and integration points
It is used by `BlockChecksumOptions` and HDFS checksum request/response paths.

## Risks and test signals
Tests should verify serialization/protobuf mappings elsewhere and behavior for each checksum type. Adding enum values requires compatibility review.
