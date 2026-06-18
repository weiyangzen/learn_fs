# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/ZKFCProtocol.java

Purpose: Defines the RPC protocol exposed by a ZooKeeper Failover Controller for graceful failover coordination.

Important APIs and types: Public-private `ZKFCProtocol` has `versionID = 1L` and idempotent methods `cedeActive(int millisToCede)` and `gracefulFailover()`, both secured with the Hadoop service Kerberos principal annotation.

Control flow: A remote controller or admin client calls `cedeActive()` to force a ZKFC to leave or delay joining the election, or `gracefulFailover()` to ask the target ZKFC to coordinate becoming active. `ZKFCRpcServer` implements this interface and delegates to `ZKFailoverController` after admin access checks.

State and persistence: Interface has no state. Implementations mutate ZKFC election participation, local service HA state, and ZooKeeper breadcrumb/lock behavior.

Dependencies and integration points: Used by `HAServiceTarget.getZKFCProxy()`, `HAAdmin.gracefulFailoverThroughZKFCs()`, `ZKFailoverController`, and protobuf ZKFC translators/server side files outside this work item.

Risks: Idempotent retry can repeat cede/failover commands. Access control must be enforced server-side. Incorrect cede durations can delay recovery or let old nodes rejoin too early.

Test signals: ZKFC graceful failover tests, access-control tests, and protocol translator tests should cover cede timing, rejoin behavior, already-active no-op behavior, and failure propagation.
