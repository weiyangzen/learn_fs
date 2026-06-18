# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CacheDirectiveInfo.java

## Purpose
`CacheDirectiveInfo` describes a path-based cache directive for HDFS centralized cache management. Its fields are nullable so the same type can represent create, modify, filter, and list payloads.

## Important APIs, types, and functions
The nested `Builder` supports id, path, replication, pool, and expiration setters plus copy-construction. `Expiration` represents relative or absolute expiration, has `NEVER`, `MAX_RELATIVE_EXPIRY_MS`, factory methods `newRelative`, `newAbsolute(Date)`, `newAbsolute(long)`, and accessors for raw millis, absolute date, and absolute millis. The outer class exposes getters, `equals`, `hashCode`, and a compact `toString` that includes only non-null fields.

## Control flow
Builder methods return `this` for chaining and `build()` creates a new info object. Relative expiration validates that the duration does not exceed `Long.MAX_VALUE / 4` to avoid overflow. `getAbsoluteMillis` converts relative expirations using the local current time; `toString` uses human-readable duration or ISO date formatting.

## State and persistence behavior
State is final directive fields. `Expiration` is immutable. No local persistence happens here, but objects are serialized in RPC/edit-log-related cache directive paths.

## Dependencies and integration points
It depends on Hadoop `Path`, `DFSUtilClient` formatting helpers, Apache Commons equality/hash builders, and Hadoop preconditions. It is consumed by cache directive create/modify/list APIs and by `CacheDirectiveIterator` filters.

## Risks and test signals
Tests should cover nullable partial directives, builder copy semantics, relative/absolute expiration formatting, `NEVER`, overflow validation, equality/hash with nulls, `toString` field omission, and time-sensitive behavior of relative expiration conversion. Client/server clocks matter because the server-side clock is authoritative for actual expiry.
