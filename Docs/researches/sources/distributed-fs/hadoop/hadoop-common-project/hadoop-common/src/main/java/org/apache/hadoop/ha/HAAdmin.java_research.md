# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HAAdmin.java

Purpose: Abstract command-line tool for invoking `HAServiceProtocol` operations: transition to active/standby, get state, list all states, check health, and print help. Subclasses supply service-id resolution and optional multi-target enumeration.

Important APIs and types: `HAAdmin extends Configured implements Tool`. Key hooks are `resolveTarget()`, `getTargetIds()`, `getUsageString()`, `checkManualStateManagementOK()`, `gracefulFailoverThroughZKFCs()`, `runCmd()`, `getAllServiceState()`, `parseOpts()`, and nested `UsageInfo`. CLI flags include `--forceactive` and hidden `--forcemanual`.

Control flow: `run()` wraps `runCmd()` and converts exceptions to nonzero status. `runCmd()` validates command syntax, parses options, prompts for forced manual state changes if auto failover is enabled, then dispatches to transition/status/health/help handlers. `transitionToActive()` checks other targets for an existing active unless forced.

State and persistence: Holds output streams for tests, `rpcTimeoutForChecks`, and current `RequestSource`. Persistent effects are remote HA state transitions. CLI output is user-facing but not persisted.

Dependencies and integration points: Uses Commons CLI, `HAServiceTarget`, `HAServiceProtocolHelper`, `ZKFCProtocol`, `FailoverController` timeout helpers, Hadoop `ToolRunner`, and service-specific subclasses such as HDFS HA admin tools.

Risks: Manual transitions with auto failover can create split-brain, so `--forcemanual` confirmation is critical. `--forceactive` bypasses readiness checks against other nodes. Zero timeout transition proxies can wait indefinitely depending on IPC behavior.

Test signals: `TestHAAdmin` and HDFS admin mini-cluster tests cover argument validation, output, forced manual confirmation, active conflict checks, health failures, all-service-state output, and ZKFC graceful failover.
