# Research Report: subset-b-007352

This grouped report covers Hadoop `viewfs` AbstractFileSystem adapters and the common HA election, failover, fencing, health-monitor, admin, and protobuf RPC client files. Each source file has a source-tree-aligned section delimited for reconciliation into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ViewFs.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ViewFs.java

Purpose: Implements the `viewfs://` `AbstractFileSystem` client-side mount table. It composes multiple target file systems behind one namespace, builds an in-memory `InodeTree<AbstractFileSystem>` from Hadoop configuration, and delegates file operations to `ChRootedFs` targets while presenting paths in the viewfs namespace.

Important APIs and types: Main public surface is the `ViewFs` class, `MountPoint`, `getMountPoints()`, `getDelegationTokens()`, and `AbstractFileSystem` overrides for create, delete, status, listing, mkdir, open, truncate, rename, symlink, ACL, xattr, snapshot, and storage policy operations. Internal helpers include `readOnlyMountTable()`, `WrappingRemoteIterator`, and `InternalDirOfViewFs`.

Control flow: Construction reads authority-specific mount table configuration, creates target `AbstractFileSystem` instances under the creating UGI, wraps them as `ChRootedFs`, and creates `InternalDirOfViewFs` objects for internal mount directories. Most operations resolve `getUriPath(path)` through `fsState.resolve()`, then call the same operation on `res.targetFileSystem` with `res.remainingPath`. Status and listing paths are rewritten to qualified viewfs paths with `ViewFsFileStatus` or `ViewFsLocatedFileStatus`.

State and persistence: Runtime state is client-local: `creationTime`, creator `ugi`, `config`, cached `homeDir`, static `showMountLinksAsSymlinks`, `renameStrategy`, and the in-memory `fsState`. Persistent filesystem mutations occur only in target filesystems or the configured root fallback filesystem. Internal mount table nodes are read-only unless fallback handling redirects create/mkdir/rename/block-location work.

Dependencies and integration points: Depends on `InodeTree`, `ChRootedFs`, `Constants`, `ConfigUtil`, `ViewFileSystem.RenameStrategy`, Hadoop `AbstractFileSystem`, `FileContext`, ACL/xattr/snapshot/storage policy APIs, delegation token APIs, and UGI. It integrates with viewfs tests and HDFS-local viewfs contract tests.

Risks: Path rewriting is subtle for chrooted targets, fallback paths, internal directories, and mount links shown as symlinks versus resolved objects. Rename is high risk because it may cross mount points and relies on configured strategy checks. Internal directory mutators must consistently reject changes unless fallback is present. The static symlink-display flag is process-wide and can be surprising with multiple configurations.

Test signals: `ViewFsBaseTest`, `TestViewFsLocalFs`, `TestViewFsHdfs`, fallback tests, ACL/xattr/truncate/storage-policy tests, delegation-token tests, and rename-strategy tests should cover resolution, listing, read-only mount table behavior, fallback precedence, path qualification, and target delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ViewFs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ViewFsFileStatus.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ViewFsFileStatus.java

Purpose: Wraps a target filesystem `FileStatus` while replacing only the visible path with the corresponding viewfs-qualified path. This works around status implementations, especially local filesystem status objects, whose owner/group resolution may depend on the original target status object.

Important APIs and types: Package-private `ViewFsFileStatus extends FileStatus` stores `myFs` and `modifiedPath`. It overrides metadata accessors such as length, file/directory/symlink flags, block size, replication, modification/access time, permissions, owner, group, path, `setPath()`, and `getSymlink()`.

Control flow: Construction captures the original status and new path. Every metadata call delegates to `myFs` except `getPath()`/`setPath()`, which read and mutate `modifiedPath`. Equality and hash code defer to `FileStatus` superclass behavior.

State and persistence: It is a transient adapter with no persistence. State is the referenced status plus mutable display path. Mutating `setPath()` affects only the wrapper path, not the target filesystem object.

Dependencies and integration points: Used by `ViewFs.getFileStatus()`, `ViewFs.listStatus()`, and `WrappingRemoteIterator` to present target results under viewfs. It depends on `FileStatus`, `Path`, and `FsPermission`.

Risks: Because equality and comparison behavior comes from `FileStatus`, wrapper identity depends on superclass use of overridden accessors. If new `FileStatus` fields are added, this wrapper may need more delegates. The target status object remains live, so lazy target-specific behavior can still execute.

Test signals: ViewFs status/listing tests should assert path qualification, owner/group behavior on local targets, symlink preservation, and stable behavior after `setPath()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ViewFsFileStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ViewFsLocatedFileStatus.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ViewFsLocatedFileStatus.java

Purpose: Provides the located-status equivalent of `ViewFsFileStatus`, preserving target `LocatedFileStatus` metadata and block locations while substituting the visible viewfs path.

Important APIs and types: Package-private `ViewFsLocatedFileStatus extends LocatedFileStatus` stores a target `LocatedFileStatus` and mutable `modifiedPath`. It delegates all normal file metadata, symlink get/set, and `getBlockLocations()` while overriding `getPath()` and `setPath()`.

Control flow: Created by `ViewFs.listLocatedStatus()` through `WrappingRemoteIterator`. Iterator results from the target filesystem are transformed one by one into wrappers whose paths are reconstructed from the resolved viewfs path and the target suffix.

State and persistence: No persistent state. It retains the target located status and a mutable display path. Block locations are target-provided and are not rewritten.

Dependencies and integration points: Integrates with `ViewFs.listLocatedStatus()` and Hadoop `LocatedFileStatus` consumers such as file scanners and block-location-aware tools.

Risks: Block locations may expose target filesystem details while paths expose viewfs paths, so callers must tolerate that split. As with `ViewFsFileStatus`, new `LocatedFileStatus` fields can require delegate updates.

Test signals: Tests should cover `listLocatedStatus()` path rewriting, block location preservation, symlink status, equality/hash behavior, and listing through mount links and non-internal target directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ViewFsLocatedFileStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/package-info.java

Purpose: Declares package-level documentation and stability annotations for `org.apache.hadoop.fs.viewfs`, identifying it as the package for `ViewFileSystem` and `ViewFileSystemOverloadScheme` classes.

Important APIs and types: Provides package annotations `@InterfaceAudience.LimitedPrivate({"MapReduce", "HBase", "Hive" })` and `@InterfaceStability.Stable`. It exports no runtime classes or functions itself.

Control flow: None. The file only affects package metadata and generated documentation.

State and persistence: No state or persistence.

Dependencies and integration points: Imports Hadoop classification annotations. Tooling, downstream consumers, and generated Javadocs use these package annotations to understand intended audience and compatibility expectations.

Risks: Package-level stability communicates compatibility promises. Changing these annotations affects downstream expectations even though runtime behavior is unchanged.

Test signals: Compile and Javadoc generation are the relevant checks; functional tests are unnecessary for this metadata-only file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/ActiveStandbyElector.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/ActiveStandbyElector.java

Purpose: Implements a ZooKeeper-backed active/standby leader election library. It uses one ephemeral lock znode to elect the active service and a persistent breadcrumb znode to identify the last active for fencing before a new active proceeds.

Important APIs and types: Public surface includes `ActiveStandbyElector`, `ActiveStandbyElectorCallback`, constructors, `joinElection()`, `quitElection()`, `parentZNodeExists()`, `ensureParentZNode()`, `clearParentZNode()`, `getActiveData()`, `terminateConnection()`, `getHAZookeeperConnectionState()`, and test hooks. Internal state enums are `State` and `ConnectionState`; callback processing implements ZooKeeper `StatCallback` and `StringCallback`.

Control flow: `joinElection()` copies app data and asynchronously creates the lock znode. A successful create fences any breadcrumb owner, writes/updates the breadcrumb, calls `appClient.becomeActive()`, and monitors the lock. `NODEEXISTS` means standby plus a watch on the active lock. Deletion or session changes trigger neutral mode, session recreation, and rejoining if appropriate. ZooKeeper operations are retried for connection loss and operation timeout up to `maxRetryNum`.

State and persistence: Local synchronized state tracks ZooKeeper client, watcher, election desire, app data, retry counts, monitor request status, and current ACTIVE/STANDBY/NEUTRAL/INIT state. Persistent ZooKeeper state is the parent znode, ephemeral `ActiveStandbyElectorLock`, and persistent `ActiveBreadCrumb`.

Dependencies and integration points: Used by `ZKFailoverController`. Depends on ZooKeeper, ACL/auth configuration, Hadoop `SecurityUtil` SSL/TLS setup, `ZKUtil`, and the callback's transition/fencing implementation.

Risks: Split-brain avoidance depends on session semantics, breadcrumb writes, stale-client filtering, callback speed, and application fencing correctness. Lock ordering and synchronized callbacks are sensitive. Short session timeouts can cause flapping, while stale breadcrumbs can force fencing after graceful-release failures.

Test signals: `TestActiveStandbyElector`, `TestActiveStandbyElectorRealZK`, ZKFC integration tests, session-expiry tests, ACL/auth tests, retry-path tests, and fencing/breadcrumb tests validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/ActiveStandbyElector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/BadFencingConfigurationException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/BadFencingConfigurationException.java

Purpose: Signals invalid fencing configuration, such as an unparsable method line, missing shell argument, invalid SSH port, unavailable class, or a class not implementing `FenceMethod`.

Important APIs and types: Public `BadFencingConfigurationException extends IOException` with string and string-plus-cause constructors.

Control flow: No internal logic beyond constructor delegation. It is thrown by `NodeFencer`, `FenceMethod.checkArgs()`, and runtime fencer validation paths, then handled by failover setup or fencer iteration.

State and persistence: Serializable exception state only, with `serialVersionUID = 1L`.

Dependencies and integration points: Integrated with `HAServiceTarget.checkFencingConfigured()`, `NodeFencer.create()`, `FailoverController`, `ZKFailoverController`, and concrete fencing methods.

Risks: Since it is an `IOException`, callers may conflate configuration failures with transport failures unless they catch it specifically. Good messages are important because operators must repair HA fencing before safe failover.

Test signals: `TestNodeFencer`, `TestShellCommandFencer`, `TestSshFenceByTcpPort`, and ZKFC startup tests should cover thrown messages and failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/BadFencingConfigurationException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/FailoverController.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/FailoverController.java

Purpose: Coordinates manual or controller-driven failover between two HA service targets. It performs preflight checks, tries graceful standby transition of the old active, fences if needed, transitions the target to active, and optionally attempts failback when activation fails.

Important APIs and types: Public `FailoverController(Configuration, RequestSource)`, static timeout helpers `getGracefulFenceTimeout()` and `getRpcTimeoutToNewActive()`, package-visible `tryGracefulFence()`, and public `failover()`. Internal `preFailoverChecks()` validates target state, readiness, and health.

Control flow: `failover()` requires a fencer, checks the destination is standby and healthy unless forced, tries `transitionToStandby()` on the source with low-retry graceful fencing config, fences the source if graceful fencing failed or force-fence is requested, then calls `transitionToActive()` on the destination. If activation fails and the old active was not fenced, it recursively fails back with forced fencing/activation.

State and persistence: Holds configuration, a graceful-fence configuration copy with reduced IPC retries, request source, and timeout values. It does not persist state; persistent effects are service HA state transitions and external fencing side effects.

Dependencies and integration points: Uses `HAServiceTarget`, `HAServiceProtocol`, `HAServiceProtocolHelper`, `NodeFencer`, Hadoop IPC timeout keys, `RPC.stopProxy()`, and request source metadata. Called by CLI/admin code and ZKFC old-active fencing.

Risks: Fencing and activation ordering is safety-critical. Force-active can activate a target that reports not ready. Failback recursion is intentionally aggressive and can fence the failed target. Timeout tuning changes split-brain risk and recovery latency.

Test signals: `TestFailoverController` covers preflight failures, graceful fencing, forced fencing, activation failure, failback, and fencer invocation counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/FailoverController.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/FailoverFailedException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/FailoverFailedException.java

Purpose: Represents a failed HA failover operation, including unsafe target state, failed health checks, failed fencing, failed activation, or failed failback.

Important APIs and types: Public `FailoverFailedException extends Exception` with message and message-plus-cause constructors.

Control flow: Thrown by `FailoverController.preFailoverChecks()` and `failover()`, then surfaced to admin tools or tests as an operational failure rather than an RPC-specific exception.

State and persistence: Exception message and optional cause only, with `serialVersionUID = 1L`.

Dependencies and integration points: Used by `FailoverController` and related tests. It deliberately does not extend `IOException`, which separates orchestration failures from lower-level RPC failures.

Risks: Callers must preserve causes to avoid hiding whether failure came from health, fencing, or activation. Messages are operator-facing and affect diagnosis.

Test signals: Manual failover tests should assert this exception for self-failover, non-standby target, unhealthy target, failed fencer, failed active transition, and failed failback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/FailoverFailedException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/FenceMethod.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/FenceMethod.java

Purpose: Defines the plugin contract for HA fencing mechanisms. Implementations forcibly prevent an old active from making progress, for example by killing a process, denying storage access, or power cycling.

Important APIs and types: Public unstable `FenceMethod` extends the optional `Configurable` pattern by documentation. It declares `checkArgs(String)` for startup validation and `tryFence(HAServiceTarget, String)` for runtime fencing.

Control flow: `NodeFencer` instantiates implementations, calls `checkArgs()` while parsing configuration, and later invokes `tryFence()` in order until one succeeds.

State and persistence: Interface itself has no state. Implementations may receive Hadoop `Configuration` through `ReflectionUtils.newInstance()` if they implement `Configurable`.

Dependencies and integration points: Implemented by `ShellCommandFencer`, `SshFenceByTcpPort`, `PowerShellFencer`, and operator-provided classes. Uses `HAServiceTarget` for address and fencer environment details.

Risks: A `true` result is trusted as sufficient split-brain protection. Implementations need clear timeout, idempotence, and failure semantics. Bad argument validation can defer misconfiguration until an emergency failover path.

Test signals: Tests should parse custom and built-in methods, validate argument failures, check ordered fallback, and verify methods receive target metadata and configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/FenceMethod.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HAAdmin.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HAAdmin.java

Purpose: Abstract command-line tool for invoking `HAServiceProtocol` operations: transition to active/standby, get state, list all states, check health, and print help. Subclasses supply service-id resolution and optional multi-target enumeration.

Important APIs and types: `HAAdmin extends Configured implements Tool`. Key hooks are `resolveTarget()`, `getTargetIds()`, `getUsageString()`, `checkManualStateManagementOK()`, `gracefulFailoverThroughZKFCs()`, `runCmd()`, `getAllServiceState()`, `parseOpts()`, and nested `UsageInfo`. CLI flags include `--forceactive` and hidden `--forcemanual`.

Control flow: `run()` wraps `runCmd()` and converts exceptions to nonzero status. `runCmd()` validates command syntax, parses options, prompts for forced manual state changes if auto failover is enabled, then dispatches to transition/status/health/help handlers. `transitionToActive()` checks other targets for an existing active unless forced.

State and persistence: Holds output streams for tests, `rpcTimeoutForChecks`, and current `RequestSource`. Persistent effects are remote HA state transitions. CLI output is user-facing but not persisted.

Dependencies and integration points: Uses Commons CLI, `HAServiceTarget`, `HAServiceProtocolHelper`, `ZKFCProtocol`, `FailoverController` timeout helpers, Hadoop `ToolRunner`, and service-specific subclasses such as HDFS HA admin tools.

Risks: Manual transitions with auto failover can create split-brain, so `--forcemanual` confirmation is critical. `--forceactive` bypasses readiness checks against other nodes. Zero timeout transition proxies can wait indefinitely depending on IPC behavior.

Test signals: `TestHAAdmin` and HDFS admin mini-cluster tests cover argument validation, output, forced manual confirmation, active conflict checks, health failures, all-service-state output, and ZKFC graceful failover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HAAdmin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HAServiceProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HAServiceProtocol.java

Purpose: Defines the public RPC contract used by HA controllers and tools to monitor a service and request state transitions.

Important APIs and types: `HAServiceProtocol` has `versionID = 1L`, enum `HAServiceState` with `INITIALIZING`, `ACTIVE`, `STANDBY`, `OBSERVER`, and `STOPPING`, enum `RequestSource`, nested `StateChangeRequestInfo`, and idempotent methods `monitorHealth()`, `transitionToActive()`, `transitionToStandby()`, package-visible `transitionToObserver()`, and `getServiceStatus()`.

Control flow: Implementations receive calls from admin tools, health monitors, failover controllers, and protobuf translators. Request source metadata allows implementations to distinguish user, forced user, and ZKFC transitions.

State and persistence: Interface has no state, but calls mutate service HA state and may gate persistent service behavior such as write ownership. `HAServiceStatus` returned by `getServiceStatus()` includes readiness for activation.

Dependencies and integration points: Annotated for Kerberos principal lookup and idempotent retry. Implemented by HA services and exposed through protobuf RPC via `HAServiceProtocolPB` and translators.

Risks: Idempotence annotations mean callers and retry layers may repeat operations; service implementations must tolerate repeats. Observer support is not public in the same way as active/standby and must be handled carefully by implementers.

Test signals: Protocol translator tests, service implementation HA state transition tests, failover controller tests, health monitor tests, and admin command tests validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HAServiceProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HAServiceProtocolHelper.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HAServiceProtocolHelper.java

Purpose: Wraps `HAServiceProtocol` calls and unwraps Hadoop `RemoteException` instances into the domain-specific exceptions expected by callers.

Important APIs and types: Static helpers are `monitorHealth()`, `transitionToActive()`, `transitionToStandby()`, and `transitionToObserver()`. Each accepts an `HAServiceProtocol` proxy and state-change info where relevant.

Control flow: Each helper invokes the corresponding protocol method in a try/catch and, on `RemoteException`, calls `unwrapRemoteException()` for `HealthCheckFailedException` or `ServiceFailedException`.

State and persistence: Stateless utility class. Persistent effects are only the remote protocol call effects.

Dependencies and integration points: Used by `FailoverController`, `ZKFailoverController`, and `HAAdmin` to avoid scattering remote-exception handling. Depends on Hadoop IPC `RemoteException`.

Risks: `monitorHealth()` accepts `reqInfo` but does not use it because the protocol method has no request-info parameter. If server-side exception classes change, unwrap behavior may stop preserving typed failures.

Test signals: Tests should exercise remote service failure propagation through failover/admin paths and verify callers receive `HealthCheckFailedException` or `ServiceFailedException` rather than raw `RemoteException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HAServiceProtocolHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HAServiceStatus.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HAServiceStatus.java

Purpose: Carries an HA service's current state and readiness-to-become-active reason from `getServiceStatus()` to controllers and admin tools.

Important APIs and types: `HAServiceStatus` stores `HAServiceState state`, `readyToBecomeActive`, and `notReadyReason`. It exposes `getState()`, fluent `setReadyToBecomeActive()`, `setNotReadyToBecomeActive(String)`, `isReadyToBecomeActive()`, and `getNotReadyReason()`.

Control flow: Services construct and return it from `HAServiceProtocol.getServiceStatus()`. `FailoverController` rejects failover to a standby that is not ready unless forced. `HealthMonitor` reports statuses to ZKFC service-state callbacks.

State and persistence: Mutable in-memory DTO only. It is serialized into protobuf responses by server-side translators and reconstructed by client-side translators.

Dependencies and integration points: Depends on `HAServiceProtocol.HAServiceState`; integrates with protobuf translation and controller readiness checks.

Risks: Default readiness is false until explicitly set, so service implementations must call one of the readiness setters. Missing not-ready reasons reduce operator diagnosis.

Test signals: Failover preflight tests should cover ready and not-ready statuses, forced activation, protobuf round trips, and service-state callback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HAServiceStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HAServiceTarget.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HAServiceTarget.java

Purpose: Abstracts a concrete HA service endpoint for admin, health monitor, failover, ZKFC, and fencing code.

Important APIs and types: Subclasses implement `getAddress()`, `getZKFCAddress()`, `getFencer()`, and `checkFencingConfigured()`. Optional hooks include `getHealthMonitorAddress()`, `isAutoFailoverEnabled()`, `supportObserver()`, and `addFencingParameters()`. Proxy factories include `getProxy()`, `getHealthMonitorProxy()`, and `getZKFCProxy()`. It also stores `transitionTargetHAStatus` for fencing context.

Control flow: Controllers resolve targets, create protocol translators using configured socket factories and IPC retries, pass target metadata to fencers, and optionally use a dedicated health-monitor address. ZKFC proxies are used for graceful failover coordination.

State and persistence: Holds only the intended transition target state. Endpoint addresses and fencer configuration are supplied by subclasses. No persistence in this base class.

Dependencies and integration points: Uses `HAServiceProtocolClientSideTranslatorPB`, `ZKFCProtocolClientSideTranslatorPB`, `NetUtils`, Hadoop IPC retry keys, and fencer parameter maps.

Risks: Incorrect addresses route control-plane RPCs to the wrong service. Fencing parameter keys feed shell environments and scripts. `transitionTargetHAStatus` is mutable and must be set consistently when source/destination-specific fencing commands are used.

Test signals: Dummy HA service tests, health monitor dedicated-address tests, admin/failover tests, and fencer environment tests validate target behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HAServiceTarget.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HealthCheckFailedException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HealthCheckFailedException.java

Purpose: Indicates that an HA service responded to a health-check RPC but reported itself unhealthy.

Important APIs and types: Public `HealthCheckFailedException extends IOException` with message and message-plus-cause constructors.

Control flow: Thrown by `HAServiceProtocol.monitorHealth()` implementations, unwrapped by `HAServiceProtocolHelper`, and interpreted by `HealthMonitor` as `SERVICE_UNHEALTHY` rather than transport-level nonresponse.

State and persistence: Exception message and optional cause only, with `serialVersionUID = 1L`.

Dependencies and integration points: Used across protocol translators, health monitor, admin check-health command, and failover preflight checks.

Risks: Distinguishing this from generic `IOException` matters: health failure keeps the monitor connected but exits election, while IO failure treats the service as not responding and reconnects.

Test signals: `TestHealthMonitor`, `TestFailoverController`, and `HAAdmin -checkHealth` tests should assert unhealthy versus not-responding behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HealthCheckFailedException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HealthMonitor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HealthMonitor.java

Purpose: Runs a daemon loop that connects to an HA service, periodically checks service status and health, and notifies callbacks when health or service state changes.

Important APIs and types: `HealthMonitor` exposes `addCallback()`, `addServiceStateCallback()`, `shutdown()`, `getProxy()`, `start()`, `join()`, and test-visible health state. Enums include `State` values `INITIALIZING`, `SERVICE_NOT_RESPONDING`, `SERVICE_HEALTHY`, `SERVICE_UNHEALTHY`, and `HEALTH_MONITOR_FAILED`. Callback interfaces are `Callback` and `ServiceStateCallback`.

Control flow: `MonitorDaemon.work()` loops until shutdown, first `loopUntilConnected()` with retry sleep, then `doHealthChecks()`. Each health iteration calls `getServiceStatus()` and `monitorHealth()`. Domain health failures enter `SERVICE_UNHEALTHY`; transport failures stop the proxy, enter `SERVICE_NOT_RESPONDING`, sleep, and reconnect. Uncaught daemon errors enter `HEALTH_MONITOR_FAILED`.

State and persistence: Holds timing/retry config, volatile `shouldRun`, current proxy, current health state, last service status, and synchronized callback lists. No persisted state.

Dependencies and integration points: Used by `ZKFailoverController` to join or quit election based on local health and observed service state. Depends on `HAServiceTarget`, `HAServiceProtocol`, Hadoop IPC `RPC.stopProxy()`, `RemoteException`, and HA health configuration keys.

Risks: Callbacks run on the monitor thread, so slow or throwing callbacks delay checks or kill monitoring. Transport/health exception classification must unwrap remote health failures correctly. Aggressive intervals can overload services; slow intervals delay failover.

Test signals: `TestHealthMonitor` and `TestHealthMonitorWithDedicatedHealthAddress` cover connection retry, state transitions, unhealthy versus not responding, callback ordering, shutdown, and dedicated health RPC address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HealthMonitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/NodeFencer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/NodeFencer.java

Purpose: Parses configured fencing method specifications and tries each method in order until one fences the old active service successfully.

Important APIs and types: `NodeFencer.create(Configuration, String)`, constructor, `fence(HAServiceTarget)`, `fence(HAServiceTarget, HAServiceTarget)`, parser helpers, built-in method aliases `shell`, `sshfence`, and `powershell`, and private `FenceMethodWithArg`.

Control flow: Configuration text is split by newline, hash comments are stripped, each line is parsed as `Class(arg)` or `Class`, short aliases are resolved, classes are instantiated via reflection, and `checkArgs()` is called. During fencing, methods are attempted sequentially. If a destination target is supplied, the method is first tried on the destination before the source; source fencing is skipped if destination-side fencing fails.

State and persistence: Holds an ordered list of instantiated fencing methods and arguments. Fencing side effects are implementation-specific and external.

Dependencies and integration points: Used by `HAServiceTarget`, `FailoverController`, and `ZKFailoverController`. Depends on `FenceMethod`, `ReflectionUtils`, built-in fencers, and operator configuration.

Risks: Regex parsing is simple and arguments cannot include a closing parenthesis. Reflection allows custom code execution by configuration. Destination-first fencing semantics depend on `transitionTargetHAStatus` and script design. A false success can create split-brain.

Test signals: `TestNodeFencer` covers parsing, comments, aliases, custom classes, ordered fallback, misconfiguration, and success/failure aggregation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/NodeFencer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/PowerShellFencer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/PowerShellFencer.java

Purpose: Windows-oriented fencing method that generates and runs a temporary PowerShell script to terminate remote `java.exe` processes whose WMI `CommandLine` contains a configured process-name fragment.

Important APIs and types: `PowerShellFencer extends Configured implements FenceMethod`, with `checkArgs()`, `tryFence()`, and private `buildPSScript()`.

Control flow: `tryFence()` takes the configured process-name argument and target hostname, builds a `.ps1` script containing a `Get-WmiObject Win32_Process -Filter ... -Computer host |% { $_.Terminate() }` command, starts `powershell.exe` with the script path, pumps stdout/stderr with `StreamPumper`, waits for process exit, and returns success for exit code 0.

State and persistence: Creates a temporary script file marked `deleteOnExit()`. It persists no Java-side state, but can kill remote processes as its external side effect.

Dependencies and integration points: Invoked through `NodeFencer` alias `powershell`. Depends on Windows PowerShell, WMI permissions, target address metadata, and `StreamPumper`.

Risks: `checkArgs()` logs but does not validate null/empty process names. Process-name text is embedded into a WMI filter without escaping, so malformed input can break the script. `deleteOnExit()` is delayed until JVM exit. Success only reflects PowerShell exit status, not necessarily that the intended process died.

Test signals: Windows-specific or mocked process tests should verify script construction, process-name filtering, error output pumping, exit-code handling, and behavior for missing PowerShell or bad arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/PowerShellFencer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/ServiceFailedException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/ServiceFailedException.java

Purpose: Indicates failure while modifying an HA service or application state, especially active/standby/observer transitions.

Important APIs and types: Public `ServiceFailedException extends IOException` with message and message-plus-cause constructors.

Control flow: Thrown by `HAServiceProtocol.transition*()` implementations, unwrapped by protocol helpers and translators, and propagated through failover, admin, ZKFC, and elector callbacks.

State and persistence: Exception message and optional cause only, with `serialVersionUID = 1L`.

Dependencies and integration points: Used by `HAServiceProtocol`, `FailoverController`, `ZKFailoverController`, `ZKFCProtocol`, and admin paths.

Risks: This exception often decides whether election is retried, failback is attempted, or graceful failover reports failure. Losing the cause makes operator diagnosis difficult.

Test signals: Transition failure tests, failover failure tests, ZKFC active-attempt recording tests, and protobuf exception unwrap tests should assert it is preserved.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/ServiceFailedException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/ShellCommandFencer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/ShellCommandFencer.java

Purpose: Built-in fencer that executes an operator-provided shell command and treats exit code 0 as successful fencing.

Important APIs and types: `ShellCommandFencer extends Configured implements FenceMethod`. Key methods are `checkArgs()`, `tryFence()`, `parseArgs()`, `abbreviate()`, `setConfAsEnvVars()`, and `addTargetInfoAsEnvVars()`.

Control flow: `checkArgs()` rejects missing command text. `tryFence()` chooses a command based on the target's intended HA state when two comma-separated commands are supplied, starts `bash -e -c` or `cmd.exe /c`, injects Hadoop configuration and target/source variables into the environment, closes stdin, pumps stdout/stderr, waits for completion, and returns `rc == 0`.

State and persistence: No persistent state. It exports potentially large configuration state as environment variables and performs arbitrary external side effects through the configured command.

Dependencies and integration points: Used through `NodeFencer` alias `shell`. Relies on `HAServiceTarget.getFencingParameters()`, `Shell.WINDOWS`, `StreamPumper`, and operator scripts.

Risks: No built-in timeout; hung scripts can hang failover. Commands run via shell, so quoting and injection risks belong to configuration. Environment values can expose sensitive config in child process environments. Two-command parsing simply splits on comma, so commands containing commas are unsupported.

Test signals: `TestShellCommandFencer` covers missing arguments, exit code handling, command abbreviation, environment variable generation, output pumping, and source/target command selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/ShellCommandFencer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/SshFenceByTcpPort.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/SshFenceByTcpPort.java

Purpose: Built-in SSH fencer that connects to the target host and kills the process listening on the HA service TCP port using `fuser`; if killing is indeterminate, it verifies the port with `nc`.

Important APIs and types: `SshFenceByTcpPort extends Configured implements FenceMethod`, with `checkArgs()`, `tryFence()`, `createSession()`, `doFence()`, `execCommand()`, nested `Args`, and nested JSch `LogAdapter`. Config keys are `dfs.ha.fencing.ssh.connect-timeout` and `dfs.ha.fencing.ssh.private-key-files`.

Control flow: Arguments parse optional user and SSH port. `tryFence()` creates a JSch session with configured private keys and disabled strict host-key checking, connects with timeout, then executes `fuser -v -k -n tcp <port>`. Exit code 0 succeeds. Exit code 1 triggers `nc -z host port`; if the port is closed, fencing is considered successful.

State and persistence: No Java persistence. External side effects include SSH authentication and remote process termination. JSch logger is globally set.

Dependencies and integration points: Used via `NodeFencer` alias `sshfence`. Depends on JSch, remote `fuser`, remote `nc`, SSH keys, service address, and `StreamPumper`.

Risks: `StrictHostKeyChecking=no` trades security for operability. Lack of root permissions can make `fuser` indeterminate. Remote command availability and PATH are platform-specific. `nc` behavior varies by implementation. Hostname resolution and SSH user defaults matter.

Test signals: `TestSshFenceByTcpPort` covers argument parsing, configured host/port/key behavior, and command outcome paths; integration testing requires an SSH-capable environment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/SshFenceByTcpPort.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/StreamPumper.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/StreamPumper.java

Purpose: Asynchronously drains subprocess output streams and forwards lines into SLF4J logs, preventing fencer subprocesses from blocking on full stdout/stderr pipes.

Important APIs and types: Package-private `StreamPumper`, enum `StreamType` (`STDOUT`, `STDERR`), constructor, `start()`, `join()`, and protected `pump()`.

Control flow: Construction creates a daemon `SubjectInheritingThread`. `start()` begins the thread; `pump()` reads UTF-8 lines from the input stream and logs stdout at INFO or stderr at WARN with a prefix; `join()` waits for completion. Any pump exception is logged through `ShellCommandFencer.LOG`.

State and persistence: Holds logger, prefix, stream type, input stream, thread, and `started` flag. No persistence.

Dependencies and integration points: Used by `ShellCommandFencer`, `SshFenceByTcpPort`, and `PowerShellFencer`. Uses `SubjectInheritingThread` so security subject context is inherited by logging thread.

Risks: `join()` and `start()` rely on assertions for lifecycle misuse; assertions may be disabled. It never explicitly closes the stream. Very verbose commands can flood logs. Exceptions are logged to `ShellCommandFencer.LOG` even when used by other fencers.

Test signals: Fencer tests should verify stdout/stderr draining, log levels, daemon thread behavior, and no subprocess deadlock with large output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/StreamPumper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/ZKFCProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/ZKFCProtocol.java

Purpose: Defines the RPC protocol exposed by a ZooKeeper Failover Controller for graceful failover coordination.

Important APIs and types: Public-private `ZKFCProtocol` has `versionID = 1L` and idempotent methods `cedeActive(int millisToCede)` and `gracefulFailover()`, both secured with the Hadoop service Kerberos principal annotation.

Control flow: A remote controller or admin client calls `cedeActive()` to force a ZKFC to leave or delay joining the election, or `gracefulFailover()` to ask the target ZKFC to coordinate becoming active. `ZKFCRpcServer` implements this interface and delegates to `ZKFailoverController` after admin access checks.

State and persistence: Interface has no state. Implementations mutate ZKFC election participation, local service HA state, and ZooKeeper breadcrumb/lock behavior.

Dependencies and integration points: Used by `HAServiceTarget.getZKFCProxy()`, `HAAdmin.gracefulFailoverThroughZKFCs()`, `ZKFailoverController`, and protobuf ZKFC translators/server side files outside this work item.

Risks: Idempotent retry can repeat cede/failover commands. Access control must be enforced server-side. Incorrect cede durations can delay recovery or let old nodes rejoin too early.

Test signals: ZKFC graceful failover tests, access-control tests, and protocol translator tests should cover cede timing, rejoin behavior, already-active no-op behavior, and failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/ZKFCProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/ZKFCRpcServer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/ZKFCRpcServer.java

Purpose: Hosts the protobuf RPC server for `ZKFCProtocol`, exposing graceful failover and cede-active operations for a local `ZKFailoverController`.

Important APIs and types: `ZKFCRpcServer implements ZKFCProtocol`, constructor, `start()`, `getAddress()`, `stopAndJoin()`, `cedeActive()`, and `gracefulFailover()`. It creates an RPC server with three handlers.

Control flow: Constructor sets `ProtobufRpcEngine2` for `ZKFCProtocolPB`, wraps this server with `ZKFCProtocolServerSideTranslatorPB`, creates a reflective protobuf blocking service, builds an Hadoop RPC server bound to the requested address, and optionally refreshes service ACLs. RPC method implementations first call `zkfc.checkRpcAdminAccess()`, then delegate to `zkfc.cedeActive()` or `zkfc.gracefulFailoverToYou()`.

State and persistence: Holds a reference to the `ZKFailoverController` and an RPC `Server`. It persists no own state.

Dependencies and integration points: Used by `ZKFailoverController.initRPC()` and admin/peer ZKFC clients. Depends on protobuf generated `ZKFCProtocolService`, `ZKFCProtocolPB`, server-side translator, Hadoop RPC and service authorization.

Risks: Missing policy with service authorization enabled is fatal. Binding to the wrong address exposes or hides failover control. Handler count is fixed and small; long failover calls can occupy handlers.

Test signals: `TestZKFailoverController` and RPC server tests should cover bind address, ACL enforcement, admin access denial, cede delegation, graceful failover delegation, and clean stop/join.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/ZKFCRpcServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/ZKFailoverController.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/ZKFailoverController.java

Purpose: Abstract base for a service-specific ZooKeeper Failover Controller. It connects health monitoring, ZooKeeper election, local HA transitions, fencing, RPC admin control, and graceful failover orchestration.

Important APIs and types: Subclasses implement target serialization, login, RPC admin access, bind address, policy provider, peer target list, SSL flag, and ZK scope. Public API includes `run()`, `getLocalTarget()`, and test hooks. Internal major methods are `initZK()`, `initHM()`, `initRPC()`, `becomeActive()`, `becomeStandby()`, `fenceOldActive()`, `cedeActive()`, `doGracefulFailover()`, `recheckElectability()`, and `verifyChangedServiceState()`.

Control flow: `run()` verifies auto failover, logs in, initializes ZooKeeper, handles optional `-formatZK`, checks parent znode and fencing, starts RPC and health monitor, then waits until fatal error. Health callbacks join or quit election based on health. Elector callbacks transition the local service active/standby or fence an old active. Graceful failover asks non-target peers and the old active to cede, waits for a normal active attempt, then lets peers rejoin.

State and persistence: Tracks configuration, local target, health monitor, elector, RPC server, last health state, volatile service state, fatal error, cede delay, delayed recheck executor, and last active-attempt record. Persistent coordination state is stored in ZooKeeper by `ActiveStandbyElector`.

Dependencies and integration points: Central integration point for `HealthMonitor`, `ActiveStandbyElector`, `FailoverController`, `ZKFCRpcServer`, `ZKFCProtocol`, `HAServiceProtocol`, security login, ACL/auth parsing, credential-provider exclusion, and service-specific subclasses such as HDFS ZKFC.

Risks: Safety relies on correct lock ordering (`elector` then ZKFC), health-state accuracy, service-state mismatch detection, fencing configuration, and ZooKeeper session behavior. Graceful failover has timing windows around cede duration, active-attempt wait, and old-active rejoin. Fatal errors stop the controller.

Test signals: `TestZKFailoverController`, stress tests, real-ZK elector tests, mini-cluster HA failover tests, service-state mismatch tests, formatZK tests, and fencing failure tests cover most control paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/ZKFailoverController.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/HAServiceProtocolClientSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/HAServiceProtocolClientSideTranslatorPB.java

Purpose: Client-side protobuf RPC translator that implements `HAServiceProtocol` and forwards calls to an `HAServiceProtocolPB` proxy.

Important APIs and types: Constructors for address/config and address/config/socket-factory/timeout, `monitorHealth()`, `transitionToActive()`, `transitionToStandby()`, `transitionToObserver()`, `getServiceStatus()`, `close()`, `getUnderlyingProxyObject()`, and private conversion helpers for service state and request source.

Control flow: Constructors set the protocol engine to `ProtobufRpcEngine2` and create an RPC proxy. Calls build static or per-call protobuf request messages, invoke the PB proxy through `ShadedProtobufHelper.ipc()`, and convert protobuf status responses back into `HAServiceStatus`.

State and persistence: Holds only the RPC proxy. No persistent state; effects are remote service protocol operations.

Dependencies and integration points: Used by `HAServiceTarget` proxy factories. Depends on generated `HAServiceProtocolProtos`, Hadoop RPC, UGI, socket factories, shaded protobuf helpers, and `ProtocolTranslator`.

Risks: Conversion defaults unknown service-state protobufs to `INITIALIZING`, which may hide enum drift. Request source conversion throws on unknown Java enum values. Callers must `close()` or stop the underlying proxy to release resources.

Test signals: Protocol translator tests, admin/failover tests using PB proxies, observer transition tests, timeout/retry tests, and readiness reason round-trip tests validate this translator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/HAServiceProtocolClientSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/HAServiceProtocolPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/HAServiceProtocolPB.java

Purpose: Marker interface binding generated protobuf `HAServiceProtocolService.BlockingInterface` to Hadoop `VersionedProtocol` with the HA service protocol name and version.

Important APIs and types: `HAServiceProtocolPB extends HAServiceProtocolService.BlockingInterface, VersionedProtocol`, annotated with Kerberos server principal, `@ProtocolInfo(protocolName = "org.apache.hadoop.ha.HAServiceProtocol", protocolVersion = 1)`, and public/evolving audience metadata.

Control flow: No method bodies. Hadoop RPC uses this interface to identify protocol version and dispatch generated protobuf service methods through translators.

State and persistence: No state.

Dependencies and integration points: Used by client-side and server-side HA service protocol translators and by `HAServiceTarget` proxy construction. Depends on generated HA service protobufs and Hadoop IPC protocol metadata.

Risks: Protocol name/version changes are wire-compatibility changes. Because annotations drive Kerberos and RPC behavior, incorrect metadata breaks authentication or client/server negotiation.

Test signals: Compile coverage, protobuf RPC integration tests, secure-cluster tests, and protocol version negotiation tests cover this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/HAServiceProtocolPB.java -->
