# subset-b-008039 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMSecurityProtocolServer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMSecurityProtocolServer.java

Purpose: This class hosts SCM's security RPC endpoint. It implements `SCMSecurityProtocol` for certificate issuance and lookup, and `SecretKeyProtocolScm` for SCM-managed symmetric secret keys used by token services. It binds protobuf translators into a Hadoop RPC server and exposes the same secret-key service to datanode, OM, and SCM protocol interfaces.

Important APIs and types: The constructor wires `SCMSecurityProtocolServerSideTranslatorPB`, `SecretKeyProtocolServerSideTranslatorPB`, `ProtocolMessageMetrics`, `CertificateServer`, `CertificateClient`, `SequenceIdGenerator`, `SecretKeyManager`, and Hadoop `RPC.Server`. Public protocol methods include `getDataNodeCertificate`, `getCertificate(NodeDetailsProto, ...)`, `getOMCertificate`, `getSCMCertificate`, `getCertificate(String)`, `getCACertificate`, `getRootCACertificate`, `listCertificate`, `listCACertificate`, `removeExpiredCertificates`, `getCurrentSecretKey`, `getSecretKey`, `getAllSecretKeys`, and `checkAndRotate`.

Control flow: Construction resolves the SCM security bind address, installs the protobuf RPC engine, creates metrics, builds reflective blocking services, starts the RPC server through `StorageContainerManager.startRpcServer`, adds secret-key PB protocols, and refreshes service ACLs when Hadoop authorization is enabled. Certificate request methods log the caller role, validate root CA rotation state through `checkIfCertSignRequestAllowed`, parse the CSR, allocate a certificate serial with `SequenceIdGenerator`, choose the root CA for SCM node certs when present or the subordinate SCM CA otherwise, then wait on the certificate future and return PEM. Secret-key methods first validate that secret keys are enabled and initialized.

State and persistence behavior: The server itself persists no certificate or secret-key state directly. Certificate storage is delegated to the configured `CertificateServer` and `CertificateStore` behind it, certificate serials come from SCM's replicated sequence table, root CA sets are read from `SCMCertificateClient`, and secret keys are managed by `SecretKeyManager`. Runtime state includes the mutable root certificate server reference, RPC server lifecycle, protocol metrics, and security configuration.

Dependencies and integration points: It is created by `StorageContainerManager` only when security is enabled. It integrates with CA rotation, SCM HA sequence IDs, certificate stores, Hadoop IPC ACLs, Kerberos principal metadata, SCM admin access for expired certificate removal, and token services that call the secret-key protocol. It also exposes testing hooks for the remote RPC user and root CA server replacement.

Risks: Certificate issuance is synchronized and blocks on `Future.get`, so CA server latency directly delays RPC handlers. The secret-key protocol is registered even when no `SecretKeyManager` exists, relying on runtime exceptions for disabled or uninitialized key service. Root CA vs subordinate CA choice is role-sensitive; incorrect `NodeType` routing can issue from the wrong authority. `getSecurityProtocolRpcPort` in SCM assumes this server exists and would fail if called in unsecure mode. Expired-certificate removal depends on remote user context being present.

Test signals: Strong coverage should assert CSR role routing, cluster-ID rejection for SCM certs, CA rotation guard behavior, sequence ID allocation, PEM lookup/list behavior, secret-key disabled and uninitialized errors, admin-only expired certificate removal, RPC startup/stop metrics registration, and service ACL refresh under authorization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMSecurityProtocolServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMStarterInterface.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMStarterInterface.java

Purpose: This small interface abstracts the operations needed by the SCM command-line starter so production startup code can be replaced in tests. It is the injection seam between `StorageContainerManagerStarter` and the static creation, init, bootstrap, and cluster-ID generation methods on SCM.

Important APIs and types: The interface declares `start(OzoneConfiguration)`, `init(OzoneConfiguration, String)`, `bootStrap(OzoneConfiguration)`, and `generateClusterId()`. It depends only on `OzoneConfiguration`, `IOException`, and Hadoop `AuthenticationException`.

Control flow: `StorageContainerManagerStarter` calls one of these methods from the default command path or from the `--init`, `--bootstrap`, and `--genclusterid` picocli subcommands. The nested production helper implements them by delegating to `StorageContainerManager.createSCM`, `StorageContainerManager.scmInit`, `StorageContainerManager.scmBootstrap`, and `StorageInfo.newClusterID`.

State and persistence behavior: The interface owns no state. Its implementations decide whether SCM storage VERSION files are created, cluster IDs are generated, bootstrap metadata is written, or an SCM daemon is started.

Dependencies and integration points: It integrates the CLI layer with SCM initialization and start lifecycle while allowing unit tests to verify command behavior without launching an SCM or mutating real storage.

Risks: The method names are part of CLI testability rather than a general service API. `bootStrap` preserves a nonstandard capital S spelling, so callers and implementations must match it exactly. Implementations must preserve the boolean result contract used by the CLI to throw `IOException` on failed init/bootstrap.

Test signals: Tests should inject a fake receiver and assert the CLI passes the parsed `OzoneConfiguration` and optional cluster ID, propagates exceptions, and throws when `init` or `bootStrap` returns false.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMStarterInterface.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMStorageConfig.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMStorageConfig.java

Purpose: `SCMStorageConfig` specializes the common Ozone `Storage` abstraction for SCM. It locates SCM's storage directory, sets the initial HDDS layout version, and manages SCM-specific VERSION-file properties such as SCM ID, HA status, primary SCM node ID, and SCM certificate serial ID.

Important APIs and types: Constructors call `Storage(NodeType.SCM, ServerUtils.getScmDbDir(conf), STORAGE_DIR, initLayoutVersion)`. Public methods include `setScmId`, `getScmId`, `setSCMHAFlag`, `isSCMHAEnabled`, `setScmCertSerialId`, `getScmCertSerialId`, `setPrimaryScmNodeId`, `getPrimaryScmNodeId`, and `checkPrimarySCMIdInitialized`. `TESTING_INIT_LAYOUT_VERSION_KEY` lets tests force an initial layout version.

Control flow: During SCM init or bootstrap, callers construct this object, set cluster and SCM-specific properties, then call `initialize` or `forceInitialize` inherited from `Storage`. During normal startup, SCM reads the storage state and these properties to decide whether startup, Ratis migration, HA bootstrap, or security initialization is allowed. `getNodeProperties` generates a random SCM ID only if one has not already been provided.

State and persistence behavior: The persistent state is the SCM VERSION file under the SCM DB storage directory. `SCM_ID`, `SCM_HA`, `SCM_CERT_SERIAL_ID`, and `PRIMARY_SCM_NODE_ID` are stored as properties. `setScmId` refuses to mutate an already initialized storage config, while the other setters update the in-memory property set for later force-initialization or persistence. `setSCMHAFlag` is one-way in practice because it does not overwrite an already true HA flag.

Dependencies and integration points: It is consumed heavily by `StorageContainerManager`, `SCMHANodeDetails`, HA/Ratis initialization, SCM security bootstrapping, certificate clients, upgrade finalization, and tests that need a formatted SCM directory. It depends on `HDDSLayoutVersionManager.maxLayoutVersion` and `ServerUtils.getScmDbDir`.

Risks: Accidentally using `forceInitialize` after changing properties can rewrite important VERSION values, so callers must preserve cluster ID and SCM ID carefully. `Boolean.valueOf(null)` makes missing `SCM_HA` read as false, which supports upgrade paths but can mask incomplete initialization. `setSCMHAFlag(false)` cannot clear a true flag. Random SCM ID generation in `getNodeProperties` means tests that need deterministic IDs must set them explicitly before initialize.

Test signals: Useful assertions cover uninitialized vs initialized `setScmId`, default random SCM ID creation, HA flag one-way behavior, certificate serial persistence, primary SCM ID checks, forced test layout version, and SCM DB directory fallback behavior in `ServerUtils`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMStorageConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/StorageContainerManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/StorageContainerManager.java

Purpose: `StorageContainerManager` is the main SCM daemon and composition root. It validates SCM storage, upgrades or initializes Ratis/HA metadata, logs in under Kerberos when needed, opens the SCM metadata store, constructs all core managers, registers event handlers, starts RPC/HTTP services, exposes MXBean state, and coordinates stop/join lifecycle.

Important APIs and types: The class implements `SCMMXBean` and `OzoneStorageContainerManager`. Major fields include `SCMDatanodeProtocolServer`, `SCMBlockProtocolServer`, `SCMClientProtocolServer`, optional `SCMSecurityProtocolServer`, `SCMMetadataStore`, `SCMHAManager`, `SCMContext`, `SequenceIdGenerator`, `NodeManager`, `PipelineManager`, `ContainerManager`, `BlockManager`, `ReplicationManager`, `SCMSafeModeManager`, `FinalizationManager`, `RootCARotationManager`, `SecretKeyManagerService`, `ContainerBalancer`, `MoveManager`, placement policies, metrics, and reconfiguration handler. Static lifecycle helpers include `createSCM`, `scmInit`, `scmBootstrap`, `initializeRatis`, `startRpcServer`, and `buildRpcServerStartMessage`.

Control flow: Construction first creates `SCMStorageConfig` and HA node details, registers metrics, requires initialized storage, initializes or repairs Ratis snapshot directories, logs in if security is enabled, creates the certificate client, opens the metadata store, configures reconfiguration callbacks, and builds system managers. System manager initialization sets up network topology, HA manager, lease manager, layout version manager, finalization manager, sequence IDs, SCM context, DNS mapping, node manager, placement policies, pipeline manager, pending replica ops, container manager, writable container factory, block manager, replication manager, safe mode manager, decommission manager, and stateful service manager. Security initialization creates certificate stores, subordinate/root CA servers, security protocol server, token secret manager, and root CA rotation manager. Event handler registration wires SCM event types to node, container, pipeline, replication, block-delete, and reconciliation handlers, including affinity executors for full and incremental container reports.

State and persistence behavior: Persistent state spans the SCM VERSION file, SCM RocksDB tables, Ratis log and snapshot directories, certificate store, sequence tables, layout version, finalization marks, and stateful service config. Startup may mutate persistent state by enabling Ratis on upgraded clusters, creating snapshot directories, initializing security, writing certificates, upgrading sequence ID tables, and writing layout-version/finalization metadata. Runtime state includes service metrics, event queues, admin sets, pipeline creation freeze state, safe mode status, root CA rotation, container token generator, and SCM HA leader metrics. Shutdown closes services in a careful order so event processing stops before the metadata store is closed.

Dependencies and integration points: This class integrates almost every SCM subsystem: HA/Ratis, metadata schema, node/pipeline/container/block management, replication, decommission, safe mode, CA security, secret keys, token generation, HTTP/JMX, admin authorization, tracing reconfiguration, DNS rack resolution, container balancer, and upgrade finalization. Public getters are used by protocol servers, tests, MXBean UI, and service managers.

Risks: Constructor ordering is critical; comments note security checks must happen before DB artifacts are created for secure-cluster tests. The startup path mutates HA/Ratis and security state, so partial failures can leave storage requiring careful recovery. `initializeRatis` uses `forceInitialize`, making VERSION-file integrity important. `start` treats HTTP startup as non-fatal but most RPC/security failures as fatal. `stop` must tolerate partially started services and is guarded by `isStopped`, but an early second stop still closes HA and replication. Admin checks are disabled unless security authorization is enabled. Upgrade finalization and root CA rotation intentionally block disruptive operations such as SCM removal and cert signing.

Test signals: Strong signals include SCM init/bootstrap idempotence, invalid cluster ID rejection, primordial vs non-primordial behavior, Ratis enablement on old storage, snapshot directory creation, security bootstrap and certificate persistence, RPC bind address selection, event handler registration, safe mode status exposure, admin/read-only admin reconfiguration, stop idempotence, HA role reporting, container state counts, peer removal validation, and finalization checkpoint propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/StorageContainerManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/StorageContainerManagerHttpServer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/StorageContainerManagerHttpServer.java

Purpose: This class is the SCM-specific `BaseHttpServer` wrapper. It configures the HTTP/HTTPS bind keys, SPNEGO settings, and SCM web context, and registers the SCM DB checkpoint servlet.

Important APIs and types: The constructor calls `super(conf, "scm")`, adds `SCMDBCheckpointServlet` at `OZONE_DB_CHECKPOINT_HTTP_ENDPOINT`, and stores the `StorageContainerManager` in the web app context under `OzoneConsts.SCM_CONTEXT_ATTRIBUTE`. Override methods return SCM-specific keys for HTTP address, HTTPS address, bind hosts, default ports, keytab, SPNEGO principal, enablement, HTTP auth type, and HTTP auth config prefix.

Control flow: `StorageContainerManager.start` constructs this server after RPC services, starts it, and treats failures as non-fatal. The base class uses the overridden keys to decide whether to bind HTTP/HTTPS listeners and how to configure authentication.

State and persistence behavior: This class owns no durable state. Runtime state is the servlet context and the inherited Jetty/HttpServer2 state. The DB checkpoint servlet may read SCM state through the context attribute.

Dependencies and integration points: It integrates SCM with the common Ozone web UI and checkpoint infrastructure. It depends on `ScmConfigKeys`, `SCMHTTPServerConfig`, and the web resources under `src/main/resources/webapps/scm`.

Risks: Misconfigured key overrides can silently bind the wrong address or disable expected auth. Since startup failure is logged but non-fatal, HTTP-only monitoring or DB checkpoint access may be unavailable while SCM itself appears healthy. The context attribute must remain in sync with servlet expectations.

Test signals: Tests should assert the endpoint registration, context attribute, SCM address/default key mapping, HTTP auth prefix, and that `StorageContainerManager` tolerates HTTP startup failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/StorageContainerManagerHttpServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/StorageContainerManagerStarter.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/StorageContainerManagerStarter.java

Purpose: This class is the picocli-based entry point for `ozone scm`. It handles normal daemon startup and subcommands for generating a cluster ID, initializing SCM storage, and bootstrapping an SCM into an HA ring.

Important APIs and types: The class extends `GenericCli` and implements `Callable<Void>`. It defines `main`, `call`, `generateClusterId`, `initScm`, `bootStrapScm`, `startScm`, and `commonInit`. The nested `SCMStarterHelper` implements `SCMStarterInterface` using production SCM methods and registers a shutdown hook with `ShutdownHookManager`.

Control flow: `main` disables JVM network address cache if configured, then runs the CLI with a production receiver. Each command calls `commonInit`, which loads `OzoneConfiguration`, extracts original arguments, and emits the startup/shutdown banner. The default `call` starts SCM through the receiver. `--init` passes the optional `--clusterid` and throws if the receiver returns false. `--bootstrap` similarly throws on false. `--genclusterid` prints a newly generated cluster ID.

State and persistence behavior: The starter itself persists no state. Its receiver can create VERSION files, bootstrap HA storage, start the SCM service, and add a shutdown hook. The production start path keeps the `StorageContainerManager` instance alive and shuts it down on JVM exit.

Dependencies and integration points: It connects CLI parsing, version reporting, server banner logging, network cache behavior, SCM init/bootstrap/start operations, and shutdown hooks. Tests can inject a fake receiver to isolate CLI behavior from SCM construction.

Risks: The subcommand names use flag-like command names (`--init`, `--bootstrap`, `--genclusterid`), so parser behavior is unusual and should be tested. The shutdown hook calls both `stop` and `join`; if `stop` hangs or partially fails, process shutdown can be delayed. Exceptions during `call` are logged and rethrown.

Test signals: `TestStorageContainerManagerStarter` should verify receiver invocation, cluster ID output, false-result failures, propagated exceptions, startup banner initialization, and shutdown hook registration for normal start.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/StorageContainerManagerStarter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/package-info.java

Purpose: This package descriptor declares that `org.apache.hadoop.hdds.scm.server` contains SCM server-related classes.

Important APIs and types: It contains no classes or functions beyond the package declaration and Javadoc.

Control flow: There is no runtime control flow.

State and persistence behavior: There is no state or persistence.

Dependencies and integration points: The descriptor provides package-level documentation for the SCM daemon, protocol server, storage, HTTP server, and starter classes in the same package.

Risks: The comment is broad and can become stale if the package grows beyond server classes.

Test signals: No direct tests are needed beyond compile/package documentation checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/FinalizationCheckpoint.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/FinalizationCheckpoint.java

Purpose: This enum models SCM upgrade finalization progress as checkpoints derived from disk state. It lets SCM resume finalization after leader changes or restarts by interpreting two facts: whether the DB contains the finalizing mark and whether metadata layout version is behind software layout version.

Important APIs and types: Checkpoints are `FINALIZATION_REQUIRED`, `FINALIZATION_STARTED`, `MLV_EQUALS_SLV`, and `FINALIZATION_COMPLETE`. Each stores the expected finalizing-mark state, expected MLV-behind-SLV state, and the `UpgradeFinalization.Status` reported to clients. Methods include `isCurrent`, `needsFinalizingMark`, `needsMlvBehindSlv`, `hasCrossed`, and `getStatus`.

Control flow: `FinalizationStateManagerImpl.getFinalizationCheckpoint` iterates the enum values and chooses the checkpoint whose expected booleans match current disk/in-memory state. Higher-level code uses `hasCrossed` to decide whether pipelines should be frozen, datanodes should be told to finalize, and finalization should resume on leader readiness.

State and persistence behavior: The enum itself is immutable. It encodes how persistent markers map to runtime upgrade status. The ordering of enum constants is semantically significant because `hasCrossed` uses `compareTo`.

Dependencies and integration points: It is used by `FinalizationManager`, `FinalizationStateManagerImpl`, `SCMContext`, and `StorageContainerManager` initialization. Client-facing upgrade status is coupled to the status stored in each enum value.

Risks: Reordering enum constants would change checkpoint progression. Adding a new checkpoint requires updating the boolean mapping and helper logic. If the two persistent facts ever cannot map to one of these states, SCM terminates through `ExitUtils` in the state manager.

Test signals: Tests should assert all four boolean combinations map to the expected checkpoint, status mapping is stable, `hasCrossed` ordering is correct, and helper methods in `FinalizationManager` react correctly at each checkpoint.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/FinalizationCheckpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/FinalizationManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/FinalizationManager.java

Purpose: This interface defines the SCM service API for upgrade finalization. It starts finalization, reports progress, exposes checkpoint state, builds the upgrade context after managers are available, reinitializes state after snapshot install, and reacts when an SCM becomes leader.

Important APIs and types: Methods include `finalizeUpgrade`, `queryUpgradeFinalizationProgress`, `getUpgradeFinalizer`, `crossedCheckpoint`, `getCheckpoint`, `buildUpgradeContext`, `reinitialize`, and `onLeaderReady`. Static helpers `shouldCreateNewPipelines` and `shouldTellDatanodesToFinalize` encode checkpoint-dependent behavior.

Control flow: `StorageContainerManager` constructs the implementation during system manager initialization, builds the finalization context after node and pipeline managers are available, and places the current checkpoint into `SCMContext`. Protocol code can then call `finalizeUpgrade` or query progress. Leader readiness may trigger background resume if finalization was interrupted.

State and persistence behavior: The interface itself owns no state. Implementations persist finalization marks and layout versions through an SCM metadata table and the storage VERSION file. The static helpers are pure functions over checkpoints.

Dependencies and integration points: It links upgrade finalization to `NodeManager`, `PipelineManager`, `SCMContext`, `HDDSLayoutVersionManager`, `Table<String,String>`, and `BasicUpgradeFinalizer`. Other SCM components read the checkpoint to decide whether to create pipelines or tell datanodes to finalize.

Risks: Callers must invoke `buildUpgradeContext` before `finalizeUpgrade`; otherwise the implementation rejects finalization. The static helper semantics are subtle: pipeline creation is allowed before finalization starts or after MLV reaches SLV, but frozen in between.

Test signals: Tests should cover checkpoint helper truth tables, finalize/query delegation, reinitialize after snapshot install, context-build preconditions, and leader-ready resume behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/FinalizationManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/FinalizationManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/FinalizationManagerImpl.java

Purpose: `FinalizationManagerImpl` composes the SCM upgrade finalizer, persistent finalization state manager, and finalization context. It is the concrete bridge between client requests, leader-resume behavior, HA replication, and layout-version upgrade execution.

Important APIs and types: It owns an `SCMUpgradeFinalizer`, `SCMUpgradeFinalizationContext`, `SCMStorageConfig`, `OzoneConfiguration`, `HDDSLayoutVersionManager`, `FinalizationStateManager`, and a named `ThreadFactory`. Its builder requires configuration, layout version manager, storage config, HA manager, finalization store, and finalization executor. It uses `FinalizationStateManagerImpl.Builder` to wrap the state manager with an HA/Ratis proxy.

Control flow: Construction initializes common fields and creates the state manager. `buildUpgradeContext` assembles the objects finalization actions need, installs it into the state manager, and builds a thread name prefix from `SCMContext`. `finalizeUpgrade` validates that context exists and delegates to `SCMUpgradeFinalizer.finalize`. `queryUpgradeFinalizationProgress` returns readonly status without mutating client tracking when requested, otherwise delegates to `reportStatus`. `onLeaderReady` starts a background single-thread executor, checks the current checkpoint, and resumes finalization if it has started but not completed.

State and persistence behavior: Persistent state is delegated to `FinalizationStateManager`; this class holds runtime references and the finalizer. On leader resume failure it terminates the process to avoid an SCM leader remaining in an inconsistent upgrade state. The single-thread executor is created on each leader-ready call and not explicitly shut down.

Dependencies and integration points: It integrates the generic Ozone upgrade finalization framework with SCM HA (`SCMHAManager`), the SCM metadata finalization table, Ratis transaction buffer, storage VERSION files, node/pipeline managers, and SCM context. Tests can inject a custom state manager through the protected constructor.

Risks: `onLeaderReady` can create a new executor per invocation; repeated calls are expected to be rare but could leak idle threads. Resume failure terminates SCM, which is deliberate but high impact. Builder null checks catch configuration mistakes late at construction. Querying with `readonly=true` bypasses takeover behavior and returns empty messages.

Test signals: Important assertions include builder required fields, context-build propagation, `finalizeUpgrade` precondition, readonly query behavior, checkpoint delegation, reinitialize delegation, leader-ready resume only for started/incomplete checkpoints, and termination path on resume failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/FinalizationManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/FinalizationStateManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/FinalizationStateManager.java

Purpose: This interface owns the replicated state transitions for SCM upgrade finalization. It is the HA/Ratis handler that adds or removes the finalizing mark, finalizes a layout feature, and reports checkpoint progress.

Important APIs and types: Replicated methods are annotated with `@Replicate`: `addFinalizingMark`, `removeFinalizingMark`, and `finalizeLayoutFeature(Integer)`. Non-replicated methods include `crossedCheckpoint`, `getFinalizationCheckpoint`, `setUpgradeContext`, and `reinitialize`. As an `SCMHandler`, it returns Ratis request type `FINALIZE`.

Control flow: `SCMUpgradeFinalizer` calls the replicated methods on the leader-facing proxy. Ratis applies the operations across SCMs so followers update the finalizing mark, layout versions, and VERSION files consistently. Snapshot installation calls `reinitialize` with a new finalization table.

State and persistence behavior: The interface describes mutations to the finalization metadata table and local layout version. The actual implementation keeps an in-memory mark synchronized with the transaction buffer because DB flushes can be asynchronous.

Dependencies and integration points: It integrates upgrade finalization with SCM HA request routing, generated invokers, DB tables, and the SCM context used by other services.

Risks: The replicated annotation is a critical contract. Adding new finalization mutations without `@Replicate` would break HA consistency. The `FINALIZE` request type must match the Ratis state machine's dispatch rules.

Test signals: Tests should verify replicated methods are invoked through the generated proxy, request type is `FINALIZE`, and checkpoint queries reflect the persistent state after add/finalize/remove transitions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/FinalizationStateManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/FinalizationStateManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/FinalizationStateManagerImpl.java

Purpose: `FinalizationStateManagerImpl` implements the persistent and in-memory SCM finalization state machine. It derives checkpoints, publishes checkpoint side effects, writes finalization metadata through the SCM transaction buffer, and handles follower catch-up from Ratis snapshots.

Important APIs and types: Key fields are the finalization metadata table, `DBTransactionBuffer`, `SCMUpgradeFinalizer`, `HDDSLayoutVersionManager`, `ReadWriteLock`, volatile `hasFinalizingMark`, and `SCMUpgradeFinalizationContext`. Important methods are `initialize`, `publishCheckpoint`, `setUpgradeContext`, `addFinalizingMark`, `finalizeLayoutFeature`, `removeFinalizingMark`, `crossedCheckpoint`, `getFinalizationCheckpoint`, `reinitialize`, and `getDBLayoutVersion`. The builder wraps the implementation in `FinalizationStateManagerInvoker` through `SCMRatisServer.getProxyHandler`.

Control flow: On startup, `initialize` checks whether `OzoneConsts.FINALIZING_KEY` exists. Adding the finalizing mark updates the volatile flag under the write lock, buffers the DB put, and publishes `FINALIZATION_STARTED`. Finalizing a layout feature runs replicated finalization steps, updates the VERSION file through the finalizer, publishes `MLV_EQUALS_SLV` once no more features need finalization, and writes `LAYOUT_VERSION_KEY` into the DB. Removing the mark buffers its deletion, verifies the checkpoint is now complete, and publishes `FINALIZATION_COMPLETE`. Reinitialization swaps the table after snapshot install, reloads the finalizing mark, compares DB layout version to local VERSION-file layout version, and finalizes missing local versions without leader-only driving actions.

State and persistence behavior: Persistent state is the finalizing key and DB layout version key in the SCM metadata table plus the VERSION-file metadata layout version updated by finalization actions. Because the transaction buffer flushes asynchronously, the volatile mark is the freshest source for checkpoint reads. `publishCheckpoint` changes runtime state by setting upgrade status, forcing nodes to healthy-readonly when MLV reaches SLV, freezing or resuming pipeline creation, and updating `SCMContext`.

Dependencies and integration points: It integrates the layout version manager, SCM metadata table, transaction buffer, Ratis proxy generation, pipeline manager, node manager, SCM context, and upgrade finalizer. Snapshot-based follower finalization depends on DB layout version being written by the leader.

Risks: Unknown checkpoint combinations terminate SCM. `removeFinalizingMark` terminates if prior state is not complete, which protects consistency but makes bugs fatal. `publishCheckpoint` assumes an upgrade context has been set before checkpoint-changing methods are called. Snapshot reinitialization finalizes local VERSION files based on DB layout version; malformed DB values become IO failures. Pipeline freeze/resume and node state changes are side effects of state publication, so tests must account for them.

Test signals: Strong tests cover all checkpoint transitions, DB mark reload, asynchronous buffer behavior via volatile mark, pipeline freeze/resume calls, force-nodes-healthy-readonly at MLV_EQUALS_SLV, layout-version DB writes, malformed layout-version errors, follower catch-up from higher snapshot MLV, and termination guards for inconsistent states.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/FinalizationStateManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/SCMUpgradeFinalizationContext.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/SCMUpgradeFinalizationContext.java

Purpose: This immutable context object supplies SCM-specific dependencies to upgrade finalization code. It packages the managers and storage/configuration objects needed by `SCMUpgradeFinalizer` and layout-feature actions.

Important APIs and types: The context exposes getters for `NodeManager`, `PipelineManager`, `FinalizationStateManager`, `OzoneConfiguration`, `HDDSLayoutVersionManager`, `SCMContext`, and `SCMStorageConfig`. The nested builder has setters for each required field and validates all fields in `build`.

Control flow: `FinalizationManagerImpl.buildUpgradeContext` creates this context after SCM has constructed node and pipeline managers. `SCMUpgradeFinalizer` uses it to add finalizing marks, close pipelines, finalize layout features, wait for post-finalization pipelines, and read leader term. Upgrade actions receive the same object.

State and persistence behavior: The context is immutable and owns no persistent state. It gives finalization actions access to persistent surfaces such as SCM storage VERSION files and replicated finalization metadata through its dependencies.

Dependencies and integration points: It connects generic upgrade execution with SCM internals without requiring the finalizer to hold many separate references. It is also passed to `HDDSUpgradeAction<SCMUpgradeFinalizationContext>` implementations.

Risks: Every field is required; missing builder fields fail at build time. The context stores live manager references, so finalization behavior depends on those managers still being active and leader state being current.

Test signals: Tests should assert builder null validation, getter identity, and that finalizer code receives the exact node, pipeline, storage, layout, state manager, config, and SCM context instances supplied by `StorageContainerManager`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/SCMUpgradeFinalizationContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/SCMUpgradeFinalizer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/SCMUpgradeFinalizer.java

Purpose: `SCMUpgradeFinalizer` provides SCM-specific actions for the generic Ozone `BasicUpgradeFinalizer`. The leader drives disruptive upgrade finalization while followers apply replicated state manager operations.

Important APIs and types: It extends `BasicUpgradeFinalizer<SCMUpgradeFinalizationContext, HDDSLayoutVersionManager>`. Overridden methods are `preFinalizeUpgrade`, `finalizeLayoutFeature`, and `postFinalizeUpgrade`. Helper methods include `replicatedFinalizationSteps`, `closePipelinesBeforeFinalization`, and `createPipelinesAfterFinalization`.

Control flow: Pre-finalization ensures the finalizing mark exists, publishes `FINALIZATION_STARTED`, and closes existing non-closed pipelines if MLV has not yet reached SLV. Pipeline creation must already be frozen by checkpoint publication. Each layout feature is finalized by calling `FinalizationStateManager.finalizeLayoutFeature`, which runs replicated finalization steps and updates DB/VERSION state. Post-finalization logs that MLV equals SLV, waits for at least one open RATIS/THREE pipeline if finalization is not complete, and removes the finalizing mark.

State and persistence behavior: The finalizer does not write DB state directly; it delegates replicated mutations to the state manager. `replicatedFinalizationSteps` runs layout-feature upgrade actions and writes the VERSION-file layout version through the superclass. Pipeline close and post-finalization wait mutate runtime cluster state, not RocksDB directly.

Dependencies and integration points: It depends on `PipelineManager`, `ReplicationConfig`, SCM leader term checks in `SCMContext`, `HDDSLayoutFeature.scmAction`, and the generic upgrade executor. It is coordinated with `FinalizationStateManagerImpl.publishCheckpoint`, which freezes/resumes pipeline creation and changes node states.

Risks: `closePipelinesBeforeFinalization` throws if pipeline creation was not frozen first, enforcing checkpoint ordering. `createPipelinesAfterFinalization` loops until an open RATIS/THREE pipeline exists and checks leader term to stop if leadership is lost; insufficient datanodes or disabled pipeline creation can delay completion. Interrupted sleep resets the interrupt flag but continues the loop. Any layout action failure is wrapped as `LAYOUT_FEATURE_FINALIZATION_FAILED`.

Test signals: Tests should cover finalizing mark creation idempotence, pipeline freeze precondition, closing all non-closed pipelines, layout feature delegation and exception wrapping, post-finalization wait behavior, leader-loss exit through `NotLeaderException`, and finalizing mark removal only after MLV reaches SLV and a pipeline is available.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/SCMUpgradeFinalizer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/ScmOnFinalizeActionForDatanodeSchemaV2.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/ScmOnFinalizeActionForDatanodeSchemaV2.java

Purpose: This class is the SCM-side finalization hook for the `DATANODE_SCHEMA_V2` HDDS layout feature. It currently records that the first SCM layout-feature action was executed.

Important APIs and types: It implements `HDDSUpgradeAction<SCMUpgradeFinalizationContext>` and is annotated with `@UpgradeActionHdds(feature = DATANODE_SCHEMA_V2, component = SCM)`. The only method is `execute`.

Control flow: During layout finalization, `SCMUpgradeFinalizer.replicatedFinalizationSteps` runs `HDDSLayoutFeature.scmAction`, which can invoke this action. The method logs the layout feature name and returns.

State and persistence behavior: There is no direct state mutation or persistence in this action. The surrounding finalizer still updates the VERSION file and finalization DB metadata for the layout feature.

Dependencies and integration points: The annotation registers this action with the HDDS upgrade framework for the SCM component. The action signature allows future use of node, pipeline, storage, or configuration state from `SCMUpgradeFinalizationContext`.

Risks: Because the action is currently a no-op aside from logging, correctness depends on any required schema-v2 SCM work being either unnecessary or handled elsewhere. Future changes must remain safe on every SCM because finalization actions are replicated to followers.

Test signals: Tests should verify annotation discovery for `DATANODE_SCHEMA_V2`, successful execution during finalization, and no unintended side effects on context managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/ScmOnFinalizeActionForDatanodeSchemaV2.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/package-info.java

Purpose: This package descriptor documents that `org.apache.hadoop.hdds.scm.server.upgrade` contains SCM upgrade-related classes.

Important APIs and types: It contains only Javadoc and the package declaration.

Control flow: There is no runtime control flow.

State and persistence behavior: There is no state or persistence.

Dependencies and integration points: The descriptor groups the SCM finalization manager, state manager, finalizer, context, checkpoint enum, and layout action in package-level documentation.

Risks: The documentation is intentionally broad and may not describe individual upgrade responsibilities as the package evolves.

Test signals: No direct tests are needed beyond compile/package documentation checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/ozone/audit/SCMAction.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/ozone/audit/SCMAction.java

Purpose: `SCMAction` enumerates SCM audit action names. Protocol servers and SCM admin/client handlers use these constants to record auditable operations with consistent action strings.

Important APIs and types: The enum implements `AuditAction` and defines action constants for datanode registration/heartbeat, SCM info, block/container allocation and deletion, pipeline operations, safe mode, replication manager, container balancer, SCM HA actions, upgrade finalization, datanode usage, token retrieval, metrics, node queries, reconciliation, deleted-block summaries, and container suppression. `getAction` returns `toString()`.

Control flow: There is no internal branching. Audit code selects an enum value at call sites and calls `getAction` when emitting audit records.

State and persistence behavior: The enum is static process state. Audit records generated elsewhere may persist or ship the returned names, so enum names are externally visible compatibility strings.

Dependencies and integration points: It integrates SCM protocol implementations with the common Ozone audit framework. Adding a new audited SCM operation generally requires adding a new constant and using it in the corresponding server method.

Risks: Renaming or removing enum constants changes audit log action strings and can break downstream parsing. `getAction` returning `toString` means there is no stable alias separate from the Java name. The enum has no grouping or metadata, so read/write/admin semantics must be encoded by call sites.

Test signals: Tests should verify new SCM operations use an appropriate action and that expected audit action strings remain stable for log consumers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/ozone/audit/SCMAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/ozone/audit/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/ozone/audit/package-info.java

Purpose: This package descriptor documents that the package defines `SCMAction`, the SCM implementation of `AuditAction`.

Important APIs and types: It contains only package-level Javadoc and the package declaration.

Control flow: There is no runtime control flow.

State and persistence behavior: There is no state or persistence.

Dependencies and integration points: It provides package documentation for SCM audit action definitions used by the wider audit framework.

Risks: The descriptor mentions only `SCMAction`, so it would need updating if more SCM audit classes are added.

Test signals: No direct tests are required.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/ozone/audit/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/ozone/protocol/commands/RetriableDatanodeEventWatcher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/ozone/protocol/commands/RetriableDatanodeEventWatcher.java

Purpose: This event watcher retries datanode commands that have a lease timeout before completion. It watches a command start event and a command-status completion event, and requeues timed-out commands onto SCM's retriable datanode command event.

Important APIs and types: The generic type parameter `T extends CommandStatusEvent`. The constructor takes `Event<CommandForDatanode>`, `Event<T>`, and `LeaseManager<Long>` and passes them to `EventWatcher`. It overrides `onTimeout` and `onFinished`.

Control flow: The inherited watcher starts a lease when a command is fired and completes it when a matching completion event arrives. If the lease times out, `onTimeout` logs command type and ID, then fires `SCMEvents.RETRIABLE_DATANODE_COMMAND` with the original `CommandForDatanode` payload. `onFinished` intentionally does nothing after normal completion.

State and persistence behavior: Durable state is not stored here. Runtime retry state is managed by the inherited `EventWatcher` and `LeaseManager`. Retried commands flow back through SCM event processing and node command queues.

Dependencies and integration points: It integrates command status reporting, SCM event publication, command leases, and retriable datanode command dispatch. It is relevant for commands where SCM expects eventual datanode acknowledgement and wants timeout-based retry.

Risks: Timeout retry can duplicate commands if completion races with lease expiration or if datanodes eventually execute an old command. The class assumes `CommandForDatanode.getId` matches completion event IDs managed by the base watcher. `onFinished` has no cleanup beyond inherited lease handling.

Test signals: Tests should assert timed-out commands are re-fired as `RETRIABLE_DATANODE_COMMAND`, completion suppresses retry, log fields are safe for null command details, and duplicate/race behavior is acceptable for idempotent datanode commands.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/ozone/protocol/commands/RetriableDatanodeEventWatcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/ozone/protocol/commands/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/ozone/protocol/commands/package-info.java

Purpose: This package descriptor documents protocol command-related classes.

Important APIs and types: It contains only Javadoc and the package declaration.

Control flow: There is no runtime control flow.

State and persistence behavior: There is no state or persistence.

Dependencies and integration points: It documents the package that includes `RetriableDatanodeEventWatcher` and related command classes.

Risks: The description is broad and may not help distinguish SCM-only command helpers from general Ozone protocol commands.

Test signals: No direct tests are needed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/ozone/protocol/commands/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/resources/webapps/scm/scm.js -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/resources/webapps/scm/scm.js

Purpose: This AngularJS module powers the SCM web UI pages for overview and Ratis events. It fetches JMX beans from SCM, transforms node, pipeline, container, and Ratis metrics into view-model state, and implements client-side search, pagination, and custom sorting for the node table.

Important APIs and types: The file defines module `scm` with dependencies `ozone` and `nvd3`, configures the `/ratis_events` route, registers `ratisEvents`, and registers `scmOverview`. The overview controller uses `$http`, `$scope`, and `$sce`, and reads JMX queries for `StorageContainerManager,name=SCMMetrics`, `SCMNodeManagerInfo`, `SCMPipelineManagerInfo`, and `ReplicationManagerMetrics`.

Control flow: `ratisEvents` fetches SCMMetrics, splits `tag.RatisEvents` by newline and pipe, and exposes timestamp/description objects. `scmOverview` initializes placeholder statistics, fetches Ratis role information, fetches node manager JMX data, maps `NodeStatusInfo` entries into table rows, derives per-node UI protocol and port from the browser scheme and JMX port entries, updates node usage/state/space statistics, fetches pipeline counts, fetches container lifecycle and health counts, and exposes UI functions for global search, records-per-page changes, page navigation, current item ranges, column sort toggling, and custom op-state/health-state sort order.

State and persistence behavior: All state is browser runtime state stored in controller fields and `$scope`. There is no persistence. `nodeStatusCopy` keeps the full fetched node list while `$scope.filteredNodes` and `$scope.nodeStatus` hold filtered and paginated views. The UI trusts selected JMX fields and uses `$sce.trustAsHtml` in `formatValue`.

Dependencies and integration points: It integrates the static SCM web app with the HTTP server, JMX JSON endpoint, SCM MXBeans and metrics naming, Ratis metrics, SCMNodeManager node-status schema, pipeline manager schema, and replication manager metrics. It depends on templates `scm-overview.html` and `ratis-events.html`.

Risks: Many mappings assume `result.data.beans[0]` exists and that `value.find(...)` returns an object; missing JMX fields can throw. `formatValue` uses `value.replace('/;/g', '<br>')`, which passes a string rather than a regex and likely does not replace semicolons globally. `$sce.trustAsHtml` should be limited to trusted JMX values. Pagination first-item display returns 1 even for empty results, while last index is clamped to at least 1. Ratis event parsing assumes `timestamp|description` format and ignores extra separators.

Test signals: UI tests should mock JMX responses for normal and missing-field cases, verify protocol/port fallback from HTTP/HTTPS, node statistics mapping, search across all row fields, pagination including empty results and "All", custom state ordering, container/pipeline count rendering, and Ratis event parsing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/resources/webapps/scm/scm.js -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/HddsTestUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/HddsTestUtils.java

Purpose: `HddsTestUtils` is a broad static helper library for SCM tests. It creates datanode details, storage reports, metadata storage reports, node reports, container reports, pipeline reports/actions, command status reports, containers, replicas, test SCM instances, and mocked RPC remote users.

Important APIs and types: Helpers include `getDatanodeDetails`, `createRandomDatanodeAndRegister`, `getListOfRegisteredDatanodeDetails`, `getRandomNodeReport`, `createNodeReport`, `createStorageReport`, `createMetadataStorageReport`, `getRandomContainerReports`, `getPipelineReportFromDatanode`, `openAllRatisPipelines`, `getPipelineActionFromDatanode`, `getContainerReports`, `getRandomContainerInfo`, `createContainerInfo`, `createCommandStatusReport`, `allocateContainer`, `closeContainer`, `quasiCloseContainer`, `getScmSimple`, `getScm`, `getContainer`, `getECContainer`, `getReplicas`, `getReplicaBuilder`, `getReplicasWithReplicaIndex`, `getRandomPipeline`, `createNodeRegistrationContainerReport`, `getContainerInfo`, `getECContainerInfo`, `createContainerReplica`, and `mockRemoteUser`.

Control flow: Most helpers build protobufs or SCM model objects from provided values or random defaults. SCM creation helpers configure loopback random ports, initialize `SCMStorageConfig` with random cluster and SCM IDs when needed, optionally inject `SCMHAManagerStub` and empty `SCMContext`, and delegate to `StorageContainerManager.createSCM`. Container state helpers drive container lifecycle events through `ContainerManager`. `mockRemoteUser` installs a spied Hadoop RPC `Server.Call` in thread-local state.

State and persistence behavior: The class is static and keeps a `ThreadLocalRandom` and one static random pipeline ID. `getScm` can create SCM VERSION files and start real SCM metadata state under configured directories. Report builders are in-memory. Randomized object IDs and usage values make many fixtures non-deterministic unless callers pass explicit values.

Dependencies and integration points: It supports tests across node manager, pipeline manager, container manager, replication manager, SCM protocol servers, and SCM startup. It depends on protobuf report types, SCM model classes, mock datanode details, Ratis and EC replication configs, `SCMConfigurator`, `SCMHAManagerStub`, Mockito, and Hadoop RPC internals.

Risks: Random IDs can make failures harder to reproduce. `getScm` mutates the supplied configuration by setting several SCM addresses and may initialize storage on disk. The static `randomPipelineID` means default container helpers can share a pipeline ID across tests. `mockRemoteUser` modifies RPC thread-local state and must be isolated. Several helpers set simplified default values that may not satisfy all invariants for newer code.

Test signals: This file is itself test support. Downstream tests should rely on it for concise construction, but failures around storage initialization, random ports, replica index, lifecycle transitions, and mocked remote users often point back to helper behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/HddsTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/HddsWhiteboxTestUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/HddsWhiteboxTestUtils.java

Purpose: This test utility provides a small reflection-based replacement for Mockito/Hadoop Whitebox helpers whose availability changed across Hadoop versions. It lets tests read and write private fields portably.

Important APIs and types: Public methods are `getInternalState(Object, String)` and `setInternalState(Object, String, Object)`. Private helpers `getFieldFromHierarchy` and `getField` search the target class and superclasses for the named declared field.

Control flow: The utility starts from `target.getClass`, finds the requested field in the class hierarchy, calls `setAccessible(true)`, then gets or sets the value. Missing fields or reflection failures are wrapped in `RuntimeException` with diagnostic text.

State and persistence behavior: The utility owns no persistent state. It mutates arbitrary target object private fields when `setInternalState` is called.

Dependencies and integration points: It depends only on Java reflection and is used by tests that need to inspect or replace internal SCM state without relying on external Whitebox classes.

Risks: Reflection bypasses encapsulation and can make tests brittle across refactors. It does not handle static-field convenience explicitly, security-manager restrictions, module access restrictions, or primitive conversion beyond what `Field.set` supports. Error text says "set internal state" even for get failures.

Test signals: Tests using this helper should fail clearly when a field is renamed or moved outside the hierarchy. Direct tests could cover superclass lookup, get/set behavior, missing-field errors, and private field accessibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/HddsWhiteboxTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/TestHddsServerUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/TestHddsServerUtil.java

Purpose: This JUnit suite verifies server-side SCM address parsing and bind-address behavior in `HddsServerUtil` and `SCMNodeInfo`. It focuses on the configuration rules datanodes and SCM use to choose SCM endpoints, including HA service-id configuration.

Important APIs and types: Tests use `OzoneConfiguration`, `SCMNodeInfo.buildNodeInfo`, `HddsServerUtil.getScmClientBindAddress`, `HddsServerUtil.getScmDataNodeBindAddress`, `HddsServerUtil.getSCMAddressForDatanodes`, `NetUtils.createSocketAddr`, `ConfUtils.addKeySuffixes`, and SCM config keys for client, datanode, names, service IDs, node IDs, addresses, and ports.

Control flow: `testGetScmDataNodeAddress` checks datanode endpoint precedence and port handling: client address fallback uses datanode default port, datanode address overrides client address, and datanode address port is respected. `testScmClientBindHostDefault` and `testScmDataNodeBindHostDefault` verify bind hosts default to `0.0.0.0`, bind-host override keys are respected, and ports come from the relevant advertised address. `testGetSCMAddresses` validates single and multiple `OZONE_SCM_NAMES` values, whitespace trimming, default ports, explicit ports, and invalid empty/hostname/port cases. `testGetSCMAddressesWithHAConfig` builds an HA service with three nodes and verifies the datanode address list from suffixed keys.

State and persistence behavior: There is no filesystem persistence. State is per-test `OzoneConfiguration`. The suite asserts computed `InetSocketAddress` values and exception behavior.

Dependencies and integration points: The tests protect address contracts used by datanodes connecting to SCM, SCM RPC bind behavior, and HA configuration parsing. They complement `TestHddsServerUtils`, which covers fallback and directory utilities in adjacent helpers.

Risks: Address parsing tests can be sensitive to `InetSocketAddress.getHostName` vs `getHostString` behavior. Invalid hostname validation depends on utility semantics. HA tests assume order-insensitive address collection and remove expected host:port strings from a list.

Test signals: Exact host and port assertions, thrown `IllegalArgumentException` for malformed configuration, bind host defaults, datanode override precedence, and complete HA node address coverage are the main regression signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/TestHddsServerUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/TestHddsServerUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/TestHddsServerUtils.java

Purpose: This suite tests additional SCM server utility behavior: datanode address fallback rules, SCM DB directory selection, stale node interval clamping, and datanode ID file path resolution.

Important APIs and types: Tests use `SCMNodeInfo.buildNodeInfo`, `ServerUtils.getScmDbDir`, `HddsServerUtil.getStaleNodeInterval`, `HddsServerUtil.getDatanodeIdFilePath`, `PathUtils.getTestDir`, `FileUtils.deleteQuietly`, and config keys for SCM datanode/client/names addresses, SCM DB directories, metadata directories, stale node interval, heartbeat interval, and datanode ID directory.

Control flow: Address tests verify explicit datanode host:port, datanode host without port, fallback to client address without honoring client port, fallback to `OZONE_SCM_NAMES` without honoring names port, and default datanode port behavior. Directory tests verify `OZONE_SCM_DB_DIRS` wins over metadata dirs and is created, metadata dirs are used as fallback and created, and missing both settings throws. Timing tests set stale node interval outside allowed bounds relative to heartbeat processing interval and expect max/min clamped values. ID-path tests verify metadata-dir fallback, empty datanode ID dir fallback, and explicit datanode ID dir selection.

State and persistence behavior: The suite creates temporary directories for SCM DB, metadata, and datanode ID path tests, then deletes them quietly. Other state is in-memory configuration.

Dependencies and integration points: These tests protect low-level configuration interpretation used during SCM and datanode startup. They complement address parsing coverage in `TestHddsServerUtil`.

Risks: Temporary directories are under a class-specific test path and must be cleaned to avoid cross-test contamination. Stale-node interval assertions encode exact clamp values derived from heartbeat processing interval and may need updates if the policy changes.

Test signals: Strong signals include correct address host/port fallback, directory creation side effects, missing-directory exception, stale interval clamp values, and datanode ID file path fallback/override behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/TestHddsServerUtils.java -->
