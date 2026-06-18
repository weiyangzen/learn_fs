# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ErasureCodingPolicy.java

## Purpose
`ErasureCodingPolicy` is a lightweight immutable policy object describing how an erasure-coded file is written, read, and reconstructed. It is cached by `SystemErasureCodingPolicies` and can be returned in `HdfsFileStatus`.

## APIs and Behavior
Constructors require non-null name/schema and a positive 1024-aligned cell size. `composePolicyName()` builds names as `CODEC-data-parity-cellk`. Getters expose name, `ECSchema`, cell size, data/parity unit counts, codec, and policy ID. `isReplicationPolicy()` compares the ID with the special replication policy, and `isSystemPolicy()` checks whether the ID is below the user-defined start ID. Equality and hash code include name, schema, cell size, and ID.

## State, Dependencies, and Integration
The class is serializable and immutable. It depends on erasure-code schema constants and integrates with EC policy management RPCs, `HdfsFileStatus`, `LocatedBlocks`, and topology verification.

## Risks and Test Signals
Name composition is part of user/admin-visible policy identity, so schema and cell-size changes can affect compatibility. Tests should cover invalid cell sizes, replication/system ID classification, equality with same schema but different ID/name, serialization, and policy propagation through file status and RPC conversion.
