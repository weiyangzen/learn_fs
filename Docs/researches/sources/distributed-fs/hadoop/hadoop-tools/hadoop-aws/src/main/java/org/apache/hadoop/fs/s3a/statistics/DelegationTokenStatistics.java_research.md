<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/DelegationTokenStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/DelegationTokenStatistics.java

Purpose: statistics contract for S3A delegation token issuance.

Important APIs/types/functions: extends `S3AStatisticInterface`; `tokenIssued()` records creation/issuance of a token.

Control flow: delegation token integration calls `tokenIssued()` when issuing a token.

State/persistence: interface only.

Dependencies/integration: created by `S3AStatisticsContext.newDelegationTokenStatistics()`.

Risks/test signals: token issuance metrics are security/operational diagnostics. Tests should verify token issuance increments in real implementation and no-op behavior in empty context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/DelegationTokenStatistics.java -->
