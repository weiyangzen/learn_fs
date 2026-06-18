<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterFederationRename.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterFederationRename.java

## Purpose
`RouterFederationRename` implements the exceptional case where a router rename crosses nameservices. Normal HDFS rename cannot move data between namespaces, so this class validates the request, checks permissions, builds a FedBalance job with DistCp and trash phases, submits it to the router's rename scheduler, and waits for completion.

## Important APIs, Types, and Functions
`routerFedRename` is the main API. It requires cross-namespace rename to be enabled, exactly one source and one destination `RemoteLocation`, no `.snapshot` component, and write access to both parents. `checkPermission` runs permission checks either as a proxy user in secure mode or as the remote user in simple mode. `buildRouterRenameJob` validates configuration and constructs `FedBalanceContext`, `DistCpProcedure`, `TrashProcedure`, and `BalanceJob`. `getRouterFederationRenameCount`, `countIncrement`, and `countDecrement` expose and maintain the number of active rename jobs.

## Control Flow
`routerFedRename` rejects disabled or ambiguous requests, validates snapshot and permission constraints, switches to the router login user, creates a `BalanceJob`, increments the active counter, submits the job to `BalanceProcedureScheduler`, waits synchronously until done, checks `job.getError()`, and decrements the counter in a `finally` block. Interrupted waits become `InterruptedIOException`.

## State and Persistence Behavior
The class holds only the router RPC server, configuration, and an in-memory `AtomicInteger` counter. Durable data movement and cleanup are delegated to FedBalance procedures and the scheduler. The job context reads policy from router configuration, including map count, bandwidth, delay, diff threshold, trash policy, and force-close behavior.

## Dependencies and Integration Points
It depends on `RouterRpcServer` for enablement and scheduler access, `RemoteLocation` for resolved source/destination locations, `UserGroupInformation` and `NameNode.getRemoteUser` for identity handling, HDFS `Path` and `FileSystem.access` for permission checks, and `org.apache.hadoop.tools.fedbalance` classes for the actual data move.

## Risks
The operation is synchronous from the RPC handler perspective while the FedBalance job runs, so long data moves can tie up request handling. Configuration validation rejects negative map, bandwidth, delay, or diff values, but operational correctness still depends on FedBalance semantics. Permission checking uses parent write access only and separate filesystems for source/destination; changes between validation and execution are possible. Snapshot path detection is string based on `.snapshot/`. The active counter must remain balanced on all submit/wait failures.

## Test Signals
Tests should cover disabled cross-namespace rename, source/destination cardinality checks, snapshot path rejection, secure and simple-mode permission checks, invalid configuration values, job build fields, scheduler submit/wait success and failure, interruption conversion, and active counter decrement on exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterFederationRename.java -->
