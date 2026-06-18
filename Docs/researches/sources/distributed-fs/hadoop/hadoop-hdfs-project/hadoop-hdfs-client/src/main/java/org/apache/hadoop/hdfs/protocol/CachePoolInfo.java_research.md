# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CachePoolInfo.java

## Purpose
`CachePoolInfo` describes a centralized cache pool, including ownership, permissions, byte limit, default replication, and maximum directive relative expiry. It is used in RPCs and can be stored in the edit log.

## Important APIs, types, and functions
Constants define unlimited limit, default limit, default replication, and relative-expiry-never. The constructor requires a pool name. Chainable setters/getters cover owner, group, mode, limit, default replication, and max relative expiry. `toString`, `equals`, and `hashCode` cover all fields. Static `validate(CachePoolInfo)` checks null info, non-negative limit/default replication, max relative expiry bounds, and valid pool name. `validateName` rejects null or empty names.

## Control flow
Setters mutate the same object and return it for chaining. Validation throws `InvalidRequestException` or `IOException` for invalid fields. Empty names are rejected because listing all pools starts from an empty previous key and an empty pool name would be ambiguous.

## State and persistence behavior
State is mutable pool metadata. The type is serializable through HDFS RPC/edit-log conversion layers, though this class itself has no serialization code.

## Dependencies and integration points
It depends on `FsPermission`, `InvalidRequestException`, `CacheDirectiveInfo.Expiration`, nullable annotations, and Apache Commons builders. It is used by cache pool create/modify/list APIs and `CachePoolEntry`.

## Risks and test signals
Tests should cover all validation failures, null optional fields for partial modification, equals/hash with nullable fields, string permission formatting, max expiry boundaries, unlimited limit, and default replication semantics. The negative replication check uses `< 0`, so zero is accepted by this class and must be interpreted by higher layers.
