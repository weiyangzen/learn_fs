# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/BatchedDirectoryListing.java

## Purpose
`BatchedDirectoryListing` is an internal struct for partial batched directory listing responses between HDFS client and NameNode.

## Important APIs, types, and functions
The constructor stores an array of `HdfsPartialListing`, a `hasMore` flag, and a `startAfter` continuation byte array. Getters expose each field. `toString` uses `ToStringBuilder`.

## Control flow
There is no behavior beyond field access.

## State and persistence behavior
State is the referenced listing array, pagination flag, and continuation key. No local persistence occurs.

## Dependencies and integration points
It depends on `HdfsPartialListing`, Apache Commons `ToStringBuilder`, and HDFS client/NameNode batched listing APIs.

## Risks and test signals
Tests should cover empty and multi-entry listing arrays, continuation behavior with `hasMore`, byte-array preservation, and string diagnostics. Arrays are not defensively copied, so mutability should be considered by callers.
