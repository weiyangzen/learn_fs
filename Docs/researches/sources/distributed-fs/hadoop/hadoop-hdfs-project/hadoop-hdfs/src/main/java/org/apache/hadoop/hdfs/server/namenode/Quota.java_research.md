# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/Quota.java

## Purpose
`Quota` defines the two core NameNode quota dimensions: namespace object count and storage space bytes including replication.

## Important APIs, types, and functions
Enum values are `NAMESPACE` and `STORAGESPACE`. Nested `Quota.Counts` extends `EnumCounters<Quota>` and provides zero and explicit-value factories. `isViolated(quota, usage)` checks current usage, while the package-private delta form checks whether a positive delta would exceed the quota.

## Control flow
A quota is violated only when it is set (`quota >= 0`) and usage is strictly greater than quota. The delta helper ignores nonpositive deltas and uses `usage > quota - delta` to avoid overflow from `usage + delta`.

## State and persistence behavior
The enum has no persistence. `Quota.Counts` is a mutable in-memory counter used by quota calculations; durable quota state lives in inode features, edit logs, and fsimage data elsewhere.

## Dependencies and integration points
It depends on `EnumCounters` and is used by `QuotaCounts`, `FSDirectory`, `INode`, directory quota features, and quota edit/RPC logic.

## Risks and invariants
Boundary semantics are critical: equality to quota is allowed, unset quota is never violated, and only positive deltas can create new violations. Changing these helpers affects all quota enforcement.

## Test signals
`TestQuota`, `TestDiskspaceQuotaUpdate`, snapshot quota tests, EC quota tests, and rename quota tests should catch regressions. Unit checks should cover unset, exact boundary, crossing deltas, zero/negative deltas, and large values.
