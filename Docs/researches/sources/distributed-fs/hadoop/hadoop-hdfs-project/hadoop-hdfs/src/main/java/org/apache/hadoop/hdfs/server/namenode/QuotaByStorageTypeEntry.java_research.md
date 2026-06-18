# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/QuotaByStorageTypeEntry.java

## Purpose
`QuotaByStorageTypeEntry` is a small value object for a quota assigned to one `StorageType`.

## Important APIs, types, and functions
It stores `StorageType type` and `long quota`, exposes getters, implements `equals`, `hashCode`, and `toString`, and provides a builder with `setStorageType`, `setQuota`, and `build`.

## Control flow
There is no complex control flow. `toString` asserts non-null type and renders lower-case storage type plus `:` plus quota.

## State and persistence behavior
The entry is effectively immutable after construction. Durable storage of per-type quota values happens in namespace metadata and conversion layers elsewhere.

## Dependencies and integration points
It depends on `StorageType`, Hadoop third-party Guava `Objects`, and `StringUtils`. It integrates with quota-by-storage-type reports, RPCs, and CLI display paths.

## Risks and invariants
The builder does not validate null type or quota sentinel legality, so downstream validation must catch invalid entries. The compact string format is likely user-visible.

## Test signals
Cover builder output, equality/hash consistency, string rendering for storage types, null type behavior, and CLI/report integration for storage-type quotas.
