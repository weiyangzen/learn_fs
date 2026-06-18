# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNode.java

## Purpose
`NameNode` is the top-level HDFS metadata server process. In this class, the emphasis is process orchestration: command-line startup modes, security login, metrics/monitors, HTTP and RPC services, `FSNamesystem` loading, HA state transitions, shared-edits initialization, rollback/recovery commands, JMX status, and runtime reconfiguration.

## Important APIs and Types
- `OperationCategory` categorizes RPC operations as `UNCHECKED`, `READ`, `WRITE`, `CHECKPOINT`, or `JOURNAL` for HA-state gating.
- Static config-key arrays (`NAMENODE_SPECIFIC_KEYS`, `NAMESERVICE_SPECIFIC_KEYS`) drive nameservice/namenode-specific key resolution.
- Constructors create tracing, determine HA and client address state, initialize generic keys, run `initialize`, enter the initial HA state, and register metrics.
- Lifecycle methods include `initialize`, `startCommonServices`, `stopCommonServices`, `stop`, `join`, `startHttpServer`, `startTrashEmptier`, and `startMetricsLogger`.
- Command helpers include `parseArguments`, `createNameNode`, `format`, `initializeSharedEdits`, `doRollback`, `doRecovery`, and `printMetadataVersion`.
- HA methods include `monitorHealth`, `transitionToActive`, `transitionToStandby`, `transitionToObserver`, `getServiceStatus`, `checkHaStateChange`, and inner `NameNodeHAContext`.
- Reconfiguration is centralized in `reconfigurePropertyImpl` and specific helpers for heartbeat, replication, slow-node tracking, SPS, block placement, IPC slow RPC logging, lock metrics, and max directory items.

## Control Flow
`createNameNode` parses generic Hadoop arguments, maps NameNode-specific startup options, stores the startup option in configuration, and either executes a one-shot command (format, rollback, bootstrap standby, initialize shared edits, recovery, metadata version, generate cluster ID) or starts a `NameNode`/`BackupNode`. Normal construction initializes config keys, logs in as the NameNode Kerberos principal, initializes metrics and startup progress, starts JVM/GC monitors, starts HTTP early for normal NameNodes, loads `FSNamesystem` from disk, optionally starts the provided-storage alias map, creates RPC servers, configures client addresses, wires HTTP servlet attributes, starts common namesystem/RPC/plugin services, and enters the initial HA state.

HA transitions are synchronized and privilege-checked. Active startup starts active services, provisions snapshot trash roots, and starts the trash emptier; standby/observer startup starts standby services with observer awareness. Failures inside HA service transitions call `doImmediateShutdown` because continuing after a partial transition can corrupt availability semantics.

Runtime reconfiguration dispatches by exact property name. Mutations that affect block management generally take the namesystem BM write lock. Some changes update RPC servers directly, some refresh `BlockManager` policy, some call into `DatanodeManager`, and SPS mode changes are allowed only on active NameNodes.

## State and Persistence Behavior
`NameNode` itself mostly owns runtime state: `namesystem`, `rpcServer`, `httpServer`, HA `state`, monitors, metrics, service plugins, alias map server, MBean name, and the `started` flag. Persistent metadata loading and saving are delegated to `FSNamesystem`, `FSImage`, `FSEditLog`, and `NNStorage`. One-shot commands mutate persistent storage: format destroys and writes namespace dirs; shared-edits initialization formats shared edits and copies edit segments after the most recent checkpoint; rollback restores previous storage state; recovery loads and saves namespace metadata.

## Dependencies and Integration Points
This class is the integration hub for `FSNamesystem`, `FSImage`, `FSEditLog`, `NameNodeRpcServer`, `NameNodeHttpServer`, HA state classes, `BootstrapStandby`, `NameNodeMetrics`, `StartupProgressMetrics`, `DefaultMetricsSystem`, Kerberos `SecurityUtil`, Hadoop IPC `Server`, service plugins, `DatanodeManager`, `BlockManager`, and many DFS configuration keys. It also implements `NameNodeStatusMXBean` and `TokenVerifier<DelegationTokenIdentifier>`.

## Risks and Edge Cases
- Startup order is delicate: HTTP may start before `FSNamesystem` load for normal NameNodes, but servlet attributes are populated only after image load.
- `verifyToken` and `queueExternalCall` intentionally return retriable failures during startup; callers must retry.
- Format/recovery/rollback are destructive or potentially data-losing and rely on confirmation flags and config gates.
- `initializeSharedEdits` must recover unclosed streams and copy exactly the edits after the last checkpoint; mistakes break HA standby bootstrap.
- HA transition failures terminate the process immediately to avoid split-brain or half-active states.
- Runtime reconfiguration mixes boolean parsing, numeric parsing, locking, and active-only constraints; invalid values should raise `ReconfigurationException` without partial mutation.
- `getClientMachine` and client id/call id can trust caller context only for configured proxy users.

## Test Signals
Broad coverage exists across `TestNameNodeOptionParsing`, `TestNameNodeConfiguration`, `TestNameNodeReconfigure`, `TestClientNameNodeAddress`, `TestNameNodeStatusMXBean`, `TestNameNodeMXBean`, `TestNameNodeHttpServer`, `TestNameNodeHttpServerXFrame`, `TestNameNodeRespectsBindHostKeys`, `TestNameNodeRecovery`, `TestStartup`, HA tests, and metrics tests. High-value signals are startup option parsing, MiniDFSCluster restart/format flows, HA state transitions, reconfiguration validation, shared-edits bootstrap, and JMX/HTTP exposure.
