<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/InvalidBlockReportLeaseException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/InvalidBlockReportLeaseException.java

## Purpose

`InvalidBlockReportLeaseException` reports that a full block report was rejected because the supplied lease ID is invalid, expired, or otherwise not accepted by the NameNode.

## Important APIs and types

The class extends `IOException` and formats the block-report ID and lease ID as hexadecimal in its message.

## Control flow

DataNodes may request a full block-report lease in heartbeat. When they later submit `blockReport`, the NameNode validates the lease and throws this exception on mismatch.

## State and persistence behavior

The exception is transient. The relevant state is the NameNode's in-memory block-report lease table and block-report tracking.

## Dependencies and integration points

It integrates with `DatanodeProtocol.blockReport`, `HeartbeatResponse.getFullBlockReportLeaseId()`, and NameNode block-manager lease admission.

## Risks and test signals

Risks include incorrectly rejecting valid reports or accepting stale reports that defeat throttling. Tests should cover valid lease use, expired leases, duplicate lease reuse, missing leases, and DataNode retry behavior after rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/InvalidBlockReportLeaseException.java -->
