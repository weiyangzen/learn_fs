# subset-b-008038 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/SafeModeExitRule.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/SafeModeExitRule.java

Purpose: This abstract base class defines the common event-driven lifecycle for SCM safe mode exit rules. A concrete rule subscribes itself to an `EventQueue`, receives events as an `EventHandler<T>`, updates rule-local state, and notifies `SCMSafeModeManager` when its condition is satisfied.

Important APIs and types: The constructor stores the owning `SCMSafeModeManager`, derives `ruleName` from the class name, and registers `this` against the concrete `TypedEvent<T>` returned by `getEventType()`. Subclasses implement `validate()`, `process(T report)`, `cleanup()`, `getStatusText()`, and `refresh(boolean forceRefresh)`. The base class exposes `getRuleName()`, `scmInSafeMode()`, `getSafeModeMetrics()`, and a feature flag `validateBasedOnReportProcessing`.

Control flow: `onMessage` is final. If SCM is still in safe mode, it first validates before processing, then processes the event only if still unsatisfied, and validates again. On either successful validation it calls `safeModeManager.validateSafeModeExitRules(ruleName)` and then `cleanup()`. This makes each concrete rule idempotent around repeated or late reports.

State and persistence behavior: The class keeps only in-memory rule metadata and the report-processing validation flag. Persistence is delegated to managers and event handlers outside this file. Cleanup is subclass-defined and usually clears sampled containers, pipelines, or report-tracking sets.

Dependencies and integration points: It integrates the safe mode manager with the HDDS event framework. Subclasses such as datanode, container, pipeline, and state-machine readiness rules use this template to bind SCM startup reports to safe mode exit.

Risks: Rule handlers remain registered because there is no handler removal path, so every message checks `getInSafeMode()` defensively. A subclass with non-idempotent `process` or `cleanup` can miscount reports if events are duplicated. The temporary `validateBasedOnReportProcessing` flag marks an active migration path and can hide behavior differences during HDDS-11958 work.

Test signals: Useful tests should send events before and after satisfaction, verify `process` is skipped when pre-validation succeeds, verify `cleanup` runs once per satisfied rule transition, and confirm late events after safe mode exit do not mutate rule state.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/SafeModeExitRule.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/SafeModeManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/SafeModeManager.java

Purpose: This is the minimal interface for components that expose safe mode status. It abstracts the common question "is this component in safe mode?" without tying callers to the concrete SCM safe mode manager implementation.

Important APIs and types: The single method `boolean getInSafeMode()` returns the current safe mode state. `SafeModeExitRule` consumes this method through `SCMSafeModeManager`, and external components can depend on the interface when only status is needed.

Control flow: There is no internal control flow. Implementations are responsible for providing a consistent view of safe mode state, usually backed by `SCMContext` or the concrete `SCMSafeModeManager`.

State and persistence behavior: The interface owns no state and has no persistence. State semantics are defined by implementers.

Dependencies and integration points: It is part of the `org.apache.hadoop.hdds.scm.safemode` package and acts as a small contract between safe mode-aware code and SCM services.

Risks: The interface does not distinguish manual forced exit, normal rule-based exit, pre-check failures, or startup not-yet-initialized states. Callers needing those details must use richer SCM APIs.

Test signals: Tests for implementers should verify the returned boolean changes on normal exit, force exit, and startup initialization paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/SafeModeManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/SafeModeMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/SafeModeMetrics.java

Purpose: `SafeModeMetrics` is the metrics source for observing SCM safe mode progress. It reports configured thresholds, current progress counters, safe mode state, refresh activity, and exit duration while SCM is starting and waiting for required datanode, container, and pipeline signals.

Important APIs and types: `create()` registers the source with `DefaultMetricsSystem` under `SafeModeMetrics`. Setters update gauges for container thresholds, pipeline thresholds, datanode thresholds, current healthy pipelines, current safe mode flag, safe mode exit duration, and last container-rule refresh durations by replication type. Increment methods update counters for reported RATIS containers, EC data replicas, pipeline reports, registered datanodes, and refresh calls.

Control flow: Safe mode rules and the manager call these methods as reports arrive or as state is refreshed. `setNumContainerReportedThreshold` and `setLastContainerSafeModeRuleRefreshDurationMs` branch on `HddsProtos.ReplicationType`, with RATIS and EC using separate gauges. Unsupported container threshold types fail fast with `IllegalArgumentException`.

State and persistence behavior: Metrics are in-memory Hadoop metrics objects. They are not persisted to RocksDB or local files. `unRegister()` removes the source from the default metrics system during shutdown.

Dependencies and integration points: The class depends on Hadoop metrics2 annotations and mutable metric primitives, and is consumed by `SCMSafeModeManager` plus concrete safe mode rules. It is externally visible through SCM metrics scraping and JMX-style metric endpoints.

Risks: Counters such as current reported container counts are monotonic unless callers explicitly reset by replacing the metrics instance, so tests and restarts must avoid reusing registered sources. Unsupported replication types in threshold setters will break callers if future replication modes are added without metric handling.

Test signals: Tests should assert metric registration/unregistration, threshold gauge values, safe mode flag 1/0 transitions, RATIS versus EC branch behavior, refresh counters, and exit duration publication.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/SafeModeMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/SafeModeRuleFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/SafeModeRuleFactory.java

Purpose: `SafeModeRuleFactory` is the singleton factory that wires SCM safe mode exit rules to configuration, managers, SCM context, and the event queue. It centralizes the current manual list of safe mode rules used during SCM startup.

Important APIs and types: `initialize(...)` installs the singleton with `ConfigurationSource`, `SCMContext`, `EventQueue`, `PipelineManager`, `ContainerManager`, and `NodeManager`. `getInstance()` returns the initialized singleton or throws. `addSafeModeManager()` calls `loadRules()`. Accessors expose all safe mode rules, pre-check rules, and a typed `getSafeModeRule(Class<T>)`.

Control flow: `loadRules` always creates `RatisContainerSafeModeRule`, `ECContainerSafeModeRule`, and `DataNodeSafeModeRule`. The datanode rule is also added to `preCheckRules`. If `scmContext.getScm()` is a real `StorageContainerManager` with a Ratis server, it adds `StateMachineReadyRule`. If a `PipelineManager` exists, it adds healthy-pipeline and one-replica-pipeline rules.

State and persistence behavior: The factory stores rule instances in memory and does not persist rule configuration. Rule state is held by the individual rule objects. Re-initialization replaces the singleton and starts a fresh rule list.

Dependencies and integration points: It binds safe mode to container, EC container, datanode, pipeline, HA/Ratis state-machine readiness, and the event bus. The implementation notes a future annotation-based discovery replacement.

Risks: The singleton is process-global, which creates test isolation and reconfiguration risk. `loadRules` appends to existing lists, so repeated `addSafeModeManager` calls on the same instance can duplicate rules. The HA state-machine rule is only added for concrete `StorageContainerManager`, so Recon/passive SCM variants can intentionally differ.

Test signals: Tests should verify initialization guard behavior, rule ordering, pre-check contents, optional pipeline rules, optional HA state-machine rule, and no unintended duplicate registration in repeated initialization scenarios.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/SafeModeRuleFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/StateMachineReadyRule.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/StateMachineReadyRule.java

Purpose: `StateMachineReadyRule` blocks SCM safe mode exit until the HA Ratis state machine has applied transactions and reported readiness. In non-HA or missing-state-machine cases, it validates immediately.

Important APIs and types: It extends `SafeModeExitRule<Boolean>`, subscribes to `SCMEvents.STATEMACHINE_READY`, and reads readiness through `SCMStateMachine.getIsStateMachineReady()`. `getStatusText()` reports the latest ready state or `NA`.

Control flow: The base `SafeModeExitRule.onMessage` drives validation. `validate()` returns the state machine readiness flag when a state machine exists and `true` otherwise. `process`, `cleanup`, and `refresh` are no-ops because the rule state lives entirely in the state machine.

State and persistence behavior: The class stores only a reference to `SCMStateMachine`. It has no persistence and no internal counters. Persistent HA state is managed by Ratis and the SCM state machine.

Dependencies and integration points: The rule is added by `SafeModeRuleFactory` only when SCM is a `StorageContainerManager` with an HA manager and Ratis server. It connects the safe mode event model to the Ratis leader readiness event.

Risks: If the state machine reference is null, safe mode does not wait for HA replay. If readiness is set prematurely elsewhere, this rule cannot detect incomplete application; it trusts `SCMStateMachine`.

Test signals: Tests should simulate `STATEMACHINE_READY` events with ready false and true, verify non-HA/null behavior validates, and confirm status text changes with the underlying state-machine flag.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/StateMachineReadyRule.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/package-info.java

Purpose: This package descriptor documents the SCM safe mode package. The package groups the manager, rule factory, exit rules, and metrics used to delay SCM serving unsafe operations until startup conditions are satisfied.

Important APIs and types: The visible package members include the `SafeModeManager` status interface, `SafeModeExitRule` base class, `SafeModeRuleFactory`, `SafeModeMetrics`, and concrete rules for datanode, container, EC container, pipeline, and HA state-machine readiness.

Control flow: There is no executable control flow in this file. Package-level behavior is event-driven: datanode heartbeats and reports enter the SCM event queue, safe mode rules process those events, and the safe mode manager exits once required rules validate.

State and persistence behavior: No state is stored here. Package implementations keep runtime counters in memory and rely on SCM metadata managers, Ratis, and event handlers for durable state where applicable.

Dependencies and integration points: The package integrates SCM startup, datanode reports, container managers, pipeline managers, HA state-machine readiness, and metrics. It is part of the `server-scm` module and backs client-visible `inSafeMode` and rule-status APIs.

Risks: Package-info files can drift from real behavior because they are not executable. The concrete source files are the authoritative contract for safe mode rule ordering and semantics.

Test signals: Coverage should come from concrete safe mode manager/rule tests rather than this descriptor.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/RootCARotationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/RootCARotationHandler.java

Purpose: `RootCARotationHandler` defines the replicated command surface for root CA and sub-CA rotation across SCM HA peers. It is an `SCMHandler` whose operations are executed through the SCM Ratis path.

Important APIs and types: The replicated methods are `rotationPrepare(rootCertId)`, `rotationPrepareAck(rootCertId, scmCertId, scmId)`, `rotationCommit(rootCertId)`, and `rotationCommitted(rootCertId)`. Additional local helpers expose ack counting, ack reset, and new sub-CA certificate ID storage. `getType()` returns `SCMRatisProtocol.RequestType.CERT_ROTATE`.

Control flow: The leader sends prepare, followers prepare a new sub-CA and acknowledge through a client-style replicated call, the leader waits for enough acks, and then commit/committed commands make peers switch certificates and clean up. Annotation metadata controls whether invocations are ordinary replicated state-machine operations or client-originating replication.

State and persistence behavior: The interface itself owns no state. Implementations persist certificate IDs, move key/cert directories, reload certificate clients, and count prepare acknowledgements.

Dependencies and integration points: It integrates root CA rotation manager scheduling with SCM HA Ratis invocation infrastructure via `SCMHandler` and `@Replicate`. It is invoked by `RootCARotationManager` and implemented by `RootCARotationHandlerImpl`.

Risks: Correctness depends on all implementations treating certificate IDs idempotently because Ratis log replay can reapply commands. Ack counting is leader-local and must not be confused with persisted rotation state.

Test signals: Tests should verify annotation-driven replication, idempotent skip behavior on already-rotated certs, ack counts, and request type routing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/RootCARotationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/RootCARotationHandlerImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/RootCARotationHandlerImpl.java

Purpose: This class implements the Ratis-applied root CA rotation commands for each SCM. It reacts to leader prepare/commit messages, coordinates local sub-CA certificate directory switching, tracks prepare acknowledgements, and reloads the SCM certificate client after commit.

Important APIs and types: It implements `RootCARotationHandler` and uses `StorageContainerManager`, `SCMCertificateClient`, `SecurityConfig`, `RootCARotationManager`, `SCMRatisServer`, and `RootCARotationHandlerInvoker`. Runtime state includes `newScmCertIdSet`, `newSubCACertId`, `newRootCACertId`, and the computed `newSubCAPath`.

Control flow: `rotationPrepare` skips already-applied root certs, resets ack state, records the new root ID, and schedules sub-CA preparation. `rotationPrepareAck` counts unique SCM certificate IDs only while the rotation manager is running and this root ID matches. `rotationCommit` atomically moves current sub-CA material to a backup directory, moves the new directory into the current path, and persists the new SCM certificate serial ID. `rotationCommitted` reloads keys/certs, deletes the backup directory, and clears the new sub-CA ID.

State and persistence behavior: Persistence is filesystem-heavy. It uses atomic directory moves for current, backup, and next certificate directories and persists the current SCM certificate serial ID through `SCMStorageConfig.persistCurrentState()`. Ack sets are in-memory and reset after rotation.

Dependencies and integration points: The builder wraps the implementation in a Ratis proxy handler, so calls participate in SCM HA replication. It depends on the rotation manager for skip decisions and task scheduling.

Risks: Directory moves are shutdown-triggering failure points. The class calls `scm.shutDown` on IO failures but continues through surrounding method structure, so callers must treat shutdown as terminal. `newScmCertIdSet` is a plain `HashSet`; method execution is expected to be serialized by Ratis/manager context rather than arbitrary concurrent callers.

Test signals: Tests should cover prepare reset, duplicate ack collapse, skip on already-current root cert, successful directory swap, persisted serial ID, certificate reload, backup cleanup, and builder proxy creation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/RootCARotationHandlerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/RootCARotationManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/RootCARotationManager.java

Purpose: `RootCARotationManager` is the SCM background service that decides when the root CA is close enough to expiry to rotate, generates a new root CA, coordinates sub-CA rotation across HA peers, persists post-processing state, and removes expired certificates.

Important APIs and types: It extends `StatefulService<CertInfoProto>` and implements SCM service callbacks. Key methods are `notifyStatusChanged`, `start`, `stop`, `isRunning`, `isRotationInProgress`, `isPostRotationInProgress`, `scheduleSubCaRotationPrepareTask`, `timeBefore2ExpiryGracePeriod`, and `shouldSkipRootCert`. Inner tasks are `MonitorTask`, `RotationTask`, `SubCARotationPrepareTask`, and `WaitSubCARotationPrepareAckTask`.

Control flow: The service runs only when SCM is leader and not in safe mode. `MonitorTask` checks the current root certificate and schedules `RotationTask` at configured time-of-day, or immediately if delay would exceed certificate expiry. `RotationTask` creates a new root CA server and certificate, installs it into the security protocol server, sends replicated prepare, and schedules ack polling plus an ack timeout. Followers run `SubCARotationPrepareTask`, create new sub-CA keys/certs under progress directories, atomically move them into the next directory, and send prepare ack. `WaitSubCARotationPrepareAckTask` waits until ack count matches current Ratis peers, then sends commit and committed, persists the new root certificate to the cert store if needed, saves a stateful `CertInfoProto`, and enters post-processing.

State and persistence behavior: Runtime booleans track running, processing, and post-processing. Durable state includes new root/sub-CA key directories, SCM storage config certificate serial IDs, valid certificate tables, and the `StatefulService` configuration used to preserve post-processing across restarts. `checkAndHandlePostProcessing` reads persisted `CertInfoProto` and either resumes the CSR-signing block window or deletes stale state.

Dependencies and integration points: The manager ties together `SCMContext`, SCM service manager, `SCMCertificateClient`, `SequenceIdGenerator`, `HASecurityUtils`, `CertificateStore`, `SecurityProtocolServer`, Ratis handler proxy, and `RootCARotationMetrics`.

Risks: The process has many shutdown-triggering IO and crypto steps. Leader changes cancel tasks and delete in-progress state, so interruption timing is important. Ack count uses current Ratis peers, which can differ from configured HA details during membership changes. Post-processing blocks CSR signing for the root cert polling interval and must be persisted correctly.

Test signals: Strong tests cover leader/safe-mode status transitions, scheduling delay calculation, immediate rotation near expiry, sequence ID match with new certificate serial, follower sub-CA directory creation and movement, ack timeout cleanup, successful commit metrics, persisted post-processing recovery, skip behavior on Ratis replay, and expired certificate cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/RootCARotationManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/RootCARotationMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/RootCARotationMetrics.java

Purpose: `RootCARotationMetrics` publishes counters and timing for SCM root CA rotation attempts. It lets operators distinguish total rotation attempts, successful rotations, and duration of the last successful rotation.

Important APIs and types: `create()` registers the source with `DefaultMetricsSystem` under `RootCARotationMetrics.NAME`. Public mutators are `incrTotalRotationNum`, `incrSuccessRotationNum`, and `setSuccessTimeInNs`. Public readers expose total and successful rotation counts. `unRegister()` removes the metrics source.

Control flow: `RootCARotationManager` increments total attempts when scheduling a rotation and increments success plus duration after all SCMs acknowledge and commit. There is no failure counter; failed attempts are inferred from total minus success.

State and persistence behavior: Metrics are in-memory Hadoop metrics primitives and are not persisted. A process restart resets them.

Dependencies and integration points: It uses Hadoop metrics2 annotations and mutable metric classes. The class is created in the rotation manager constructor and unregistered on manager stop.

Risks: The private `ms` field is stored but not used after construction. Re-registering without unregistering can collide in tests. The lack of explicit failure and timeout counters limits diagnosis of repeated rotation failures.

Test signals: Tests should verify registration name, counter increments, last success time gauge, unregister behavior, and total-minus-success interpretation on failed rotation scenarios.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/RootCARotationMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/ScmSecretKeyStateBuilder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/ScmSecretKeyStateBuilder.java

Purpose: This builder creates a `SecretKeyState` implementation wrapped in an SCM Ratis proxy so secret-key state mutations annotated for replication are applied through the HA state machine.

Important APIs and types: Setters accept a `SecretKeyStore` and `SCMRatisServer`. `build()` constructs `SecretKeyStateImpl(secretKeyStore)` and wraps it with `scmRatisServer.getProxyHandler(new SecretKeyStateInvoker(...))`.

Control flow: There is no branching. The builder defers all behavior to `SecretKeyStateImpl`, `SecretKeyStateInvoker`, and Ratis proxy infrastructure.

State and persistence behavior: This class owns no persistent state. The supplied `SecretKeyStore` controls local secret-key storage, while Ratis replication controls distributed state ordering.

Dependencies and integration points: It is used by `SecretKeyManagerService` to build the state object consumed by `SecretKeyManager`. It depends on SCM HA being present and usable.

Risks: There are no null checks. A missing store or Ratis server will fail at build time with a null-pointer style error. The class assumes all secret-key state mutations must go through the proxy; bypassing it would skip replication.

Test signals: Tests should verify that a built state object routes mutating calls through `SecretKeyStateInvoker` and that missing dependencies fail clearly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/ScmSecretKeyStateBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/SecretKeyManagerService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/SecretKeyManagerService.java

Purpose: `SecretKeyManagerService` is the SCM background service that initializes and rotates symmetric secret keys used by secure Ozone components. It runs only when this SCM is the ready leader.

Important APIs and types: The constructor builds `SecretKeyConfig`, `LocalSecretKeyStore`, a Ratis-proxied `SecretKeyState`, and `SecretKeyManager`, then schedules itself. It implements `SCMService` and `Runnable` with `notifyStatusChanged`, `shouldRun`, `run`, `start`, `stop`, `getSecretKeyManager`, and static `isSecretKeyEnable(SecurityConfig)`.

Control flow: `notifyStatusChanged` locks service state. If `SCMContext.isLeaderReady()` is true and the manager is uninitialized, it asynchronously calls `secretKeyManager.checkAndInitialize()`; then it marks service status running. Otherwise it pauses. The scheduled `run` exits unless running, and then calls `checkAndRotate(false)`.

State and persistence behavior: Runtime state is guarded by `serviceLock` and represented by `ServiceStatus`. Secret keys persist through `LocalSecretKeyStore` at the configured SCM CA cert storage directory, while mutations are replicated through the Ratis-backed `SecretKeyState`.

Dependencies and integration points: It integrates SCM leader readiness, SCM Ratis, local secret-key files, `SecretKeyManager`, and security configuration. It is enabled whenever security is enabled.

Risks: The constructor calls `start()`, so instantiation has scheduling side effects. Exceptions in the asynchronous initialization task are rethrown as runtime exceptions inside the executor. The service status is process-local and must be updated on leader transitions to avoid rotating keys on followers.

Test signals: Tests should cover leader-ready initialization, paused follower behavior, scheduled rotation only while running, persisted local key file interaction, Ratis replication of initialized state, and scheduler shutdown.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/SecretKeyManagerService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/package-info.java

Purpose: This descriptor identifies the SCM security package. The package contains code for SCM-issued certificates, root CA rotation, secret-key state, and related background services.

Important APIs and types: Important package members in this subset include `RootCARotationHandler`, `RootCARotationHandlerImpl`, `RootCARotationManager`, `RootCARotationMetrics`, `ScmSecretKeyStateBuilder`, and `SecretKeyManagerService`. Nearby package code also includes SCM security protocol implementations and certificate authority integration.

Control flow: The package participates in SCM startup and leader lifecycle. Certificate and key services generally run only on the leader or through Ratis proxies so that replicated state remains ordered.

State and persistence behavior: Package implementations persist security material to SCM certificate/key directories, SCM storage configuration, local secret-key stores, and SCM metadata tables. This file itself has no state.

Dependencies and integration points: The package integrates HDDS security configuration, X.509 certificate clients and servers, SCM HA/Ratis, SCM service management, and Hadoop metrics.

Risks: Package-level documentation can become stale relative to concrete security workflows. Root CA rotation and secret-key rotation are high-impact paths because IO, crypto, and HA ordering failures can force SCM shutdown.

Test signals: Tests should focus on concrete security services, especially idempotence under Ratis replay, leader transitions, and persistence recovery.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/ContainerReportQueue.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/ContainerReportQueue.java

Purpose: `ContainerReportQueue` is a specialized `BlockingQueue` for SCM full and incremental container reports. It preserves fair per-datanode ordering while reducing redundant full container reports and optionally merging incremental reports in subclasses.

Important APIs and types: It implements `BlockingQueue<ContainerReport>` and `FixedThreadPoolWithAffinityExecutor.IQueueMetrics`. The queue stores datanode UUIDs in `orderingQueue` and per-datanode report lists in `dataMap`. Public queue methods include `add`, `offer`, `put`, `take`, `poll`, `peek`, `element`, `size`, `remainingCapacity`, `clear`, and `getAndResetDropCount`.

Control flow: Adding an FCR removes the latest queued FCR for the same datanode if present, decrements capacity, increments `droppedCount`, then enqueues the new report. Adding an ICR tries `mergeIcr`; if not merged, it appends and records ordering. Removal takes the next UUID from `orderingQueue` and removes the first report from that datanode's list.

State and persistence behavior: State is in-memory only: queue capacity, UUID ordering, report lists, and dropped FCR counter. There is no persistence.

Dependencies and integration points: It consumes `SCMDatanodeHeartbeatDispatcher.ContainerReport` types and is intended for SCM event executor queues that process full and incremental reports. Drop counts are exposed for queue metrics by event type name.

Risks: Several `BlockingQueue` operations are unsupported and throw. `isEmpty()` checks only `orderingQueue` without synchronizing on `dataMap`. `put` and timed `offer` sleep-loop rather than using condition variables. Capacity and ordering must stay balanced; bugs in report replacement can strand UUID entries or report lists.

Test signals: Tests should cover FCR replacement and drop counts, ICR append order, subclass ICR merge behavior, capacity limits, blocking/timed offer behavior, per-datanode fair order, clear, and unsupported operation exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/ContainerReportQueue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/OzoneStorageContainerManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/OzoneStorageContainerManager.java

Purpose: This interface is the facade contract for SCM-like services. It lets passive SCM variants such as Recon reuse server/protocol code while swapping selected manager implementations.

Important APIs and types: The interface exposes lifecycle methods `start`, `stop`, `join`, and `shutDown`, plus accessors for node, block, pipeline, container, replication, balancer, datanode RPC address, SCM node details, reconfiguration handler, metadata store, HA manager, and sequence ID generator.

Control flow: There is no implementation here. Protocol servers and dispatchers call this facade to reach managers without depending directly on the concrete `StorageContainerManager` in every path.

State and persistence behavior: The interface owns no state. Implementations provide access to persistent metadata stores, HA state, sequence IDs, and manager state.

Dependencies and integration points: It is consumed by `SCMDatanodeProtocolServer`, `SCMDatanodeHeartbeatDispatcher`, and other server-side classes that need SCM services but should remain overrideable for Recon.

Risks: The facade still exposes many concrete manager types, so alternate implementations must satisfy a broad surface. Methods do not encode nullability or readiness, so callers must know which managers are valid for passive modes.

Test signals: Tests for passive SCM variants should verify protocol servers can operate with custom implementations and that unsupported managers fail deliberately rather than by accidental null dereference.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/OzoneStorageContainerManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMBlockProtocolServer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMBlockProtocolServer.java

Purpose: `SCMBlockProtocolServer` hosts the protobuf RPC endpoint used by OM and block clients to allocate blocks, delete key blocks, query SCM identity, add SCM peers, sort datanodes, and retrieve network topology.

Important APIs and types: It implements `ScmBlockLocationProtocol` and `Auditor`. The constructor creates an RPC server for `ScmBlockLocationProtocolPB`, registers protocol metrics, applies service ACLs, and records the resolved bind address. Main RPCs are `allocateBlock`, `deleteKeyBlocks`, `getScmInfo`, `addSCM`, `sortDatanodes`, and `getNetworkTopology`; lifecycle methods are `start`, `stop`, `join`, and `close`.

Control flow: `allocateBlock` loops `num` times through `scm.getScmBlockManager().allocateBlock`, sorts pipeline nodes by client distance when possible, audits partial allocation as failure, and records latency metrics. `deleteKeyBlocks` calls the block manager delete log and maps `SCMException` result codes to per-block delete results. `addSCM` requires admin access and delegates to the HA manager. `sortDatanodes` resolves UUIDs to datanodes and sorts by topology distance.

State and persistence behavior: The server owns RPC server state and metrics only. Block allocation/deletion persistence is delegated to `BlockManager`; HA membership persistence is delegated to `SCMHAManager`. Audit logs and metrics record outcomes.

Dependencies and integration points: It integrates Hadoop RPC, protobuf translators, SCM block manager, node manager, network topology, HA manager, security authorization, audit logging, and performance metrics.

Risks: Partial block allocation is returned but audited as failure, so clients must handle fewer blocks than requested. Client machine topology resolution may fall back to synthetic nodes or null. `stop()` also cleans up the SCM node manager, which is shared state and must align with SCM lifecycle.

Test signals: Tests should verify RPC binding, service ACL refresh, allocation success/failure metrics, client-distance pipeline ordering, delete result-code mapping, admin checks for `addSCM`, datanode sorting with unknown nodes, and audit success/failure emission.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMBlockProtocolServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMCertStore.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMCertStore.java

Purpose: `SCMCertStore` persists certificates issued by SCM CA into SCM metadata tables. SCM certificates are stored in both the generic valid cert table and the SCM-specific valid cert table.

Important APIs and types: It implements `CertificateStore`. Methods include `storeValidCertificate`, `storeValidScmCertificate`, `checkValidCertID`, `removeAllExpiredCertificates`, `getCertificateByID`, `listCertificate`, and `reinitialize`. The builder wraps the store in a Ratis proxy using `CertificateStoreInvoker`.

Control flow: Store operations take a `ReentrantLock`. For SCM role certificates, `storeValidCertificate` delegates to `storeValidScmCertificate`, which writes both tables in a single batch operation. Non-SCM roles write only the generic valid cert table. Expired removal iterates valid and valid-SCM tables, queues deletes in one batch, and commits.

State and persistence behavior: Durable state lives in `SCMMetadataStore` tables keyed by certificate serial number. Batch operations ensure SCM certs are written consistently across both tables. `reinitialize` swaps the underlying metadata store during state-machine reload.

Dependencies and integration points: It integrates X.509 certificate authority code, SCM metadata tables, Ratis proxy invocation, and root CA rotation. `RootCARotationManager` uses it to persist new root certificates and remove expired certs.

Risks: The TODO notes that role-specific listing is only implemented for SCM versus generic roles. Expired certificates may appear in both valid and SCM tables, so removal returns both entries. Locking is local to this store instance; replicated invocation ordering is handled by Ratis proxy.

Test signals: Tests should verify duplicate serial rejection, SCM cert dual-table writes, non-SCM generic writes, batch atomicity, expired removal from both tables, list pagination with start ID zero handling, reinitialization, and proxy builder behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMCertStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMClientProtocolServer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMClientProtocolServer.java

Purpose: `SCMClientProtocolServer` hosts the main client/admin SCM RPC endpoint. It exposes container, pipeline, datanode, safe mode, replication manager, upgrade, balancer, metrics, HA, token, reconciliation, and container suppression operations through `StorageContainerLocationProtocol`.

Important APIs and types: The constructor creates a `StorageContainerLocationProtocolPB` RPC server, adds the reconfiguration protocol, registers protocol metrics, applies service ACLs, and records the resolved client RPC address. Major RPC groups include container allocation/list/read/delete, pipeline create/list/activate/deactivate/close, datanode query/decommission/maintenance/usage, safe mode status and force exit, replication manager controls, upgrade finalization, container balancer controls, SCM HA leadership/decommission, metrics fetch, container reconciliation, and suppression.

Control flow: Most write/admin operations call `checkAdminAccess(getRemoteUser(), false)`; read-sensitive operations usually use the read-only flag. Container reads route through `getContainerWithPipelineCommon`, which handles safe-mode open-container replica checks and reconstructs a read pipeline if the original open pipeline is gone. List operations build streams filtered by state, factor, replication type/config, and suppression flag. Balancer startup validates each optional override before mutating a configuration copy and starting the balancer. Reconciliation first calls `ReconciliationEligibilityHandler` and maps eligibility failures to protocol exceptions before firing an event.

State and persistence behavior: The server owns RPC and metric registration state only. Persistent effects are delegated to managers: container metadata updates, pipeline state changes, decommission manager state, finalization manager state, HA peer changes, and suppression flags persisted by `ContainerManager.updateContainerInfo`. Audit logs record each success/failure path.

Dependencies and integration points: It is the main integration point for `StorageContainerManager`, `ContainerManager`, `PipelineManager`, `NodeManager`, `ReplicationManager`, `ContainerBalancer`, `SCMRatisServer`, security configuration, token generation, event queue, finalization manager, and metrics fetcher.

Risks: The class has a very broad blast radius and mixes operator commands with client read paths. Some deprecated deleted-block APIs are no-ops. `getExistContainerWithPipelinesInBatch` suppresses per-container failures by excluding entries. Balancer start returns a failure response instead of throwing for selected validation/state exceptions. Safe-mode read behavior for open containers depends on reported replica count.

Test signals: Tests should cover admin authorization, audit status for every major RPC group, safe-mode allocation rejection and read allowance rules, list filtering including suppressed containers, datanode volume failure fields, pipeline lifecycle calls, leadership transfer with and without explicit target, balancer validation, upgrade finalization access control, reconciliation eligibility mapping, and suppression persistence.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMClientProtocolServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMConfigurator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMConfigurator.java

Purpose: `SCMConfigurator` is a test and extension builder object for injecting custom SCM manager implementations into `StorageContainerManager` construction. It lets tests replace selected managers without rewriting the full SCM startup path.

Important APIs and types: It has setters and getters for `NodeManager`, `PipelineManager`, `ContainerManager`, `BlockManager`, `ReplicationManager`, `SCMSafeModeManager`, `CertificateServer`, `SCMMetadataStore`, `NetworkTopology`, `SCMHAManager`, `SCMContext`, `WritableContainerFactory`, upgrade finalization executor, and `LeaseManager<Object>`.

Control flow: The class is a passive holder. SCM construction code reads configured values and uses defaults for null values. There is no validation, ordering, or lifecycle management here.

State and persistence behavior: State is only in-memory object references. It does not persist configuration and does not own injected managers.

Dependencies and integration points: It touches most major SCM subsystems and is important for unit/integration tests that need mocked managers, custom metadata stores, or specialized finalization behavior.

Risks: Because all fields are optional and unvalidated, inconsistent combinations can fail later in SCM startup. The class is mutable and not thread-safe; it should be treated as construction-time only.

Test signals: Tests should verify default-manager fallback in SCM construction, successful use of each injected manager, and failures for incompatible injected combinations where appropriate.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMConfigurator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMContainerMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMContainerMetrics.java

Purpose: `SCMContainerMetrics` is a Hadoop metrics source that reports counts of containers by lifecycle state and total containers.

Important APIs and types: `create(SCMMXBean)` registers a metrics source named `SCMContainerMetrics`. `getMetrics` reads `scmmxBean.getContainerStateCount()` and emits gauges for open, closing, quasi-closed, closed, deleting, deleted, and total containers. `unRegister` removes the source.

Control flow: During metrics collection, it iterates over all `HddsProtos.LifeCycleState` values to compute total count, then emits selected state gauges using static lifecycle constants.

State and persistence behavior: It has no persistent state. Runtime state is the `SCMMXBean` reference and metrics system registration. Container counts originate from the SCM manager implementing the MXBean.

Dependencies and integration points: It depends on `SCMMXBean`, Hadoop metrics2, `Interns`, and Ozone constants. Operators see the output through SCM metrics sinks.

Risks: The code assumes `getContainerStateCount()` contains non-null entries for every lifecycle state. Adding new lifecycle states changes total calculation but not necessarily individual gauge publication. Re-registration without unregistering can affect tests.

Test signals: Tests should verify gauge names and values, total calculation across all states, behavior when state maps are complete, and unregister behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMContainerMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMDBCheckpointServlet.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMDBCheckpointServlet.java

Purpose: `SCMDBCheckpointServlet` exposes a tar.gz checkpoint snapshot of the SCM metadata database through the SCM HTTP server. It inherits checkpoint generation and authorization behavior from `DBCheckpointServlet`.

Important APIs and types: `init()` retrieves `StorageContainerManager` from the servlet context attribute `OzoneConsts.SCM_CONTEXT_ATTRIBUTE` and calls `initialize` with the SCM metadata store, DB checkpoint metrics, admin-authorization flag, empty allowed/denied user lists, and disabled SPNEGO proxy-user style handling.

Control flow: If the SCM context attribute is missing, it logs an error and returns without initializing the servlet. Otherwise the base servlet handles future checkpoint requests.

State and persistence behavior: The servlet itself persists nothing. It reads from the live SCM metadata store and the base servlet materializes checkpoint responses. Authorization is based on SCM admin settings.

Dependencies and integration points: It connects the HTTP server, servlet context, `StorageContainerManager`, SCM metadata store, and SCM metrics. It is used for backup, debugging, and HA/recovery workflows needing DB snapshots.

Risks: If the servlet is registered without the SCM context attribute, it silently remains uninitialized after logging. Checkpoint exposure is sensitive; admin authorization configuration must be correct when Ozone authorization is enabled.

Test signals: Tests should verify initialization with valid SCM, missing-context behavior, passing the correct DB store and metrics to the base servlet, and admin-only access when authorization is enabled.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMDBCheckpointServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMDatanodeHeartbeatDispatcher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMDatanodeHeartbeatDispatcher.java

Purpose: `SCMDatanodeHeartbeatDispatcher` translates a datanode heartbeat protobuf into SCM node-manager processing plus typed events for node, container, pipeline, action, and command-status reports.

Important APIs and types: The main method is `dispatch(SCMHeartbeatRequestProto)`. Nested payload wrappers include `ReportFromDatanode`, `NodeReportFromDatanode`, `CommandQueueReportFromDatanode`, `LayoutReportFromDatanode`, `ContainerReport`, `ContainerReportType`, `ContainerReportFromDatanode`, `IncrementalContainerReportFromDatanode`, `ContainerActionsFromDatanode`, `PipelineReportFromDatanode`, `PipelineActionsFromDatanode`, and `CommandStatusReportFromDatanode`.

Control flow: `dispatch` converts datanode details from protobuf. If the node is unregistered, it queues a `ReregisterCommand` and returns that node's command queue without processing reports. For registered nodes, it fills a backward-compatible initial layout version if missing, processes layout and heartbeat command-queue reports through `NodeManager`, then fires events for optional node report, full container report, each incremental container report, container actions, pipeline reports/actions, and command status reports.

State and persistence behavior: The dispatcher owns no durable state. Event payloads carry datanode identity and protobuf report data. `IncrementalContainerReportFromDatanode.mergeReport` can combine report lists in memory for queue coalescing.

Dependencies and integration points: It is used by `SCMDatanodeProtocolServer.sendHeartbeat` and integrates with `NodeManager`, `EventPublisher`, `SCMEvents`, layout upgrade handling, and Ozone command generation.

Risks: Unregistered nodes do not have their reports processed, so registration state accuracy is critical. Layout-version fallback preserves older datanode compatibility but can mask missing layout reports. Event ordering follows the method order and downstream handlers may depend on it.

Test signals: Tests should cover unregistered reregister behavior, registered command returns, layout fallback, event firing for every heartbeat sub-report, ICR multiple-event behavior, command-status events, and ICR merge semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMDatanodeHeartbeatDispatcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMDatanodeProtocolServer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMDatanodeProtocolServer.java

Purpose: `SCMDatanodeProtocolServer` hosts the protobuf RPC endpoint used by datanodes for version negotiation, registration, and heartbeats.

Important APIs and types: It implements `StorageContainerDatanodeProtocol` and `Auditor`. The constructor creates an RPC server for `StorageContainerDatanodeProtocolPB`, configures metrics and ACLs, and creates a `SCMDatanodeHeartbeatDispatcher`. Main RPCs are `getVersion`, `register`, and `sendHeartbeat`. `getCommandResponse` converts in-memory `SCMCommand<?>` instances to protobuf command messages.

Control flow: `getVersion` delegates to `NodeManager`. `register` converts extended datanode details, delegates registration to `NodeManager`, and on success fires a registration full-container report, node-registration container report, and pipeline report before returning a protobuf registered response. `sendHeartbeat` dispatches reports, converts returned commands, optionally includes the current Ratis leader term, and audits the response. Command conversion switches over supported command types including reregister, delete blocks, close/delete/replicate/reconcile container, reconstruct EC, create/close pipeline, operational state, finalize layout, and refresh volume usage.

State and persistence behavior: The server owns RPC and metrics state only. Registration, heartbeat state, command queues, and layout version state are managed by `NodeManager` and downstream event handlers.

Dependencies and integration points: It integrates datanodes with SCM node manager, event queue, heartbeat dispatcher, HA leader term publication, protocol metrics, audit logging, service ACLs, and Recon-friendly override points for bind address, policy provider, protocol class, and metrics creation.

Risks: Adding a new `SCMCommand` type requires updating `getCommandResponse` or heartbeats will fail with `IllegalArgumentException`. Registration fires reports only after successful registration. `stop()` unregisters metrics after stopping RPC and cleans up the shared node manager.

Test signals: Tests should verify RPC binding, version delegation, registration event firing, heartbeat command protobuf conversion for every command type, leader term inclusion only on leaders, audit logs, unsupported command failure, and subclass override points.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMDatanodeProtocolServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMHTTPServerConfig.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMHTTPServerConfig.java

Purpose: `SCMHTTPServerConfig` is the Java-style configuration bean for SCM HTTP server SPNEGO/Kerberos authentication settings.

Important APIs and types: It is annotated with `@ConfigGroup(prefix = "hdds.scm.http.auth")`. Config fields are the HTTP Kerberos principal and keytab path. Getters and setters expose both values. Nested `ConfigStrings` publishes full legacy-compatible key names for code that needs string constants.

Control flow: There is no runtime control flow beyond simple getters and setters. The configuration framework populates annotated fields from `OzoneConfiguration`.

State and persistence behavior: The object holds configuration values in memory. Persistence comes from external configuration files.

Dependencies and integration points: It integrates with the HDDS configuration annotation system, Kerberos/SPNEGO HTTP server setup, and older code paths that reference raw config keys.

Risks: The annotation keys include the full property names while the config group also has a prefix; compatibility should be checked against the configuration framework's expected key composition. Defaults include placeholder realm and standard keytab path that must be overridden in secure deployments.

Test signals: Tests should verify configuration binding, default values, setter/getter behavior, and `ConfigStrings` key values used by HTTP security setup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMHTTPServerConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMMXBean.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMMXBean.java

Purpose: `SCMMXBean` is the JMX management interface for SCM runtime information. It extends `ServiceRuntimeInfo` with SCM-specific ports, IDs, safe mode state, container state, HA role, and storage directory information.

Important APIs and types: Methods expose datanode and client RPC ports, safe mode boolean and current container threshold, container state counts, safe mode rule statuses, SCM ID, cluster ID, Ratis roles, primordial node, Ratis log directory, RocksDB directory, and hostname.

Control flow: This is an interface with no implementation. `StorageContainerManager` or an adapter supplies the values for JMX and metrics sources such as `SCMContainerMetrics`.

State and persistence behavior: The interface owns no state. Implementations read from SCM context, storage config, managers, and runtime service metadata.

Dependencies and integration points: It is consumed by JMX tooling, metrics code, and operator diagnostics. It bridges internal SCM manager state to external observability.

Risks: Return types are loosely structured for some values, such as `Map<String, String[]>` for rule status and `List<List<String>>` for Ratis roles. Consumers must tolerate implementation-specific formatting.

Test signals: Implementation tests should assert stable values for ports, IDs, safe mode status, rule status formatting, container state counts, HA role lists, and directory paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMPolicyProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMPolicyProvider.java

Purpose: `SCMPolicyProvider` supplies Hadoop service authorization mappings for SCM RPC protocols. RPC servers use it when Hadoop security authorization is enabled.

Important APIs and types: It extends `PolicyProvider`. `getInstance()` returns a memoized singleton. `getServices()` returns ACL-key/protocol pairs for datanode protocol, container-location protocol, block-location protocol, SCM security protocol, secret-key protocols for OM/SCM/datanode, and reconfiguration protocol.

Control flow: There is no complex flow. RPC servers call `SCMPolicyProvider.getInstance()` and pass it to `refreshServiceAcl`; Hadoop authorization then evaluates configured ACLs per protocol.

State and persistence behavior: The provider owns an immutable static list of service mappings. ACL values are persisted in external Hadoop/Ozone configuration, not in this class.

Dependencies and integration points: It integrates `StorageContainerDatanodeProtocol`, `StorageContainerLocationProtocol`, `ScmBlockLocationProtocol`, `SCMSecurityProtocol`, secret-key protocols, and `ReconfigureProtocol` with Hadoop service authorization.

Risks: New SCM RPC protocols must be added here or service authorization may not protect them correctly. Misconfigured ACL keys can deny legitimate clients or allow unexpected access.

Test signals: Tests should verify singleton reuse, service list contents, ACL key/protocol pairing, and that each SCM RPC server refreshes ACLs with this provider when authorization is enabled.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMPolicyProvider.java -->
