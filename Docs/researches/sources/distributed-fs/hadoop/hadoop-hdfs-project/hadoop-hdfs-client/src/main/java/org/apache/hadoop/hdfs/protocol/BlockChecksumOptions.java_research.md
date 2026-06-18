# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/BlockChecksumOptions.java

## Purpose
`BlockChecksumOptions` carries options controlling how lower-level chunk checksums are combined into a block-level checksum.

## Important APIs, types, and functions
Constructors accept a `BlockChecksumType` and optional stripe length. Getters expose type and stripe length. `toString` formats both fields.

## Control flow
There is no behavior beyond construction and formatting.

## State and persistence behavior
State is final checksum type and stripe length. No local persistence occurs.

## Dependencies and integration points
It depends on `BlockChecksumType` and is used by HDFS block checksum APIs, especially when composite CRCs or striped checksum behavior are requested.

## Risks and test signals
Tests should cover default stripe length of 0, explicit stripe lengths, string formatting, and caller validation for unsupported combinations. The class does not validate stripe length itself.
