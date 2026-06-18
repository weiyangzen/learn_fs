<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockReportContext.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockReportContext.java

## Purpose

`BlockReportContext` carries metadata for a DataNode block report RPC: how many RPC chunks make up the report, which chunk this is, the report id, and the lease id used for block-report rate limiting.

## Important APIs and types

Fields are immutable: `totalRpcs`, `curRpc`, `reportId`, and `leaseId`. Getters expose each value.

## Control flow

The DataNode sends this context with block reports. The NameNode uses it to correlate split reports and enforce/report lease handling.

## State and persistence behavior

The object is an immutable RPC context and does not persist anything. Lease effects are handled by block-report lease logic elsewhere.

## Dependencies and integration points

Used by `DatanodeProtocol` block report calls and NameNode block-report processing. Related tests include block report lease/rate-limiting coverage.

## Risks and edge cases

The class does no validation: invalid chunk indexes, inconsistent totals, duplicate report ids, or stale lease ids must be rejected by higher-level block-report handling.

## Test signals

`TestBlockReportLease` and block-report processing tests should cover lease ids, multi-RPC reports, bypass lease id zero, and invalid report context rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockReportContext.java -->
