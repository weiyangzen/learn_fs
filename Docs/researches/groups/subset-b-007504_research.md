# Research: subset-b-007504

Grouped research for Hadoop HDFS NameNode storage, startup, HTTP, resource, and management support classes.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NNStorage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NNStorage.java

## Purpose
`NNStorage` is the NameNode-specific `Storage` implementation responsible for local metadata storage directories. It maps configured image and edits URIs to `StorageDirectory` instances, names fsimage/edit/marker files, formats VERSION directories, reads storage properties, tracks checkpoint txids and times, handles failed directory removal/restoration, and exposes namespace identity (`namespaceID`, `clusterID`, `blockpoolID`) to the rest of NameNode startup and checkpoint code.

## Important APIs and Types
- `NameNodeFile` enumerates metadata file families: `IMAGE`, `IMAGE_NEW`, `IMAGE_ROLLBACK`, `IMAGE_LEGACY_OIV`, `EDITS`, `EDITS_INPROGRESS`, `EDITS_TMP`, `SEEN_TXID`, and legacy pre-HDFS-1073 names.
- `NameNodeDirType` distinguishes storage purposes: `IMAGE`, `EDITS`, and `IMAGE_AND_EDITS`; `IMAGE_AND_EDITS.isOfType()` intentionally matches either image or edits queries.
- Constructor `NNStorage(Configuration, Collection<URI> imageDirs, Collection<URI> editsDirs)` delegates to `setStorageDirectories` and initializes name-dir size metrics.
- Storage file name helpers (`getImageFileName`, `getCheckpointImageFileName`, `getFinalizedEditsFileName`, `getInProgressEditsFileName`, `getTemporaryEditsFileName`) centralize on-disk naming.
- Format and property APIs include `format(NamespaceInfo, boolean)`, `format()`, `readProperties(StorageDirectory, StartupOption)`, `setFieldsFromProperties`, `setPropertiesFromFields`, and `writeAll`.
- Failure APIs include `reportErrorOnFile`, private `reportErrorsOnDirectory`, `attemptRestoreRemovedStorage`, and `getRemovedStorageDirs`.

## Control Flow
Construction copies configured edits dirs, then `setStorageDirectories` clears current/removed lists, classifies shared/image/edit dirs, only adds `file://` dirs, and records shared edits dirs without locking. Startup inspection uses `readAndInspectDirs`: first read each VERSION file to establish a single layout version, reject missing all VERSION files or mixed layout versions, select transactional or pre-transactional inspectors based on `TXID_BASED_LAYOUT`, then inspect all storage dirs. Formatting clears each current dir, writes VERSION properties, writes `seen_txid=0`, and logs success.

Checkpoint lookup flows through image dir iterators and returns the first readable matching image. Edit-log lookup uses `findFinalizedEditsFile`, which fails loudly if the named segment is absent. `writeTransactionIdFileToStorage` writes marker files to all dirs of a requested type and removes dirs that fail, preventing partially writable storage from continuing unnoticed.

## State and Persistence Behavior
Persistent state is held in the storage VERSION files and metadata files under each `current` dir. `setFieldsFromProperties` loads common `Storage` fields and federation `blockpoolID`; `setPropertiesFromFields` writes `blockpoolID` when the layout supports federation. `readProperties` special-cases rolling-upgrade rollback by refusing newer storage versions and forcing the in-memory layout to the service layout. `mostRecentCheckpointTxId` is volatile, while `mostRecentCheckpointTime`, `removedStorageDirs`, `deprecatedProperties`, and `nameDirSizeMap` are in-memory. `SEEN_TXID` is written via `PersistentLongFile` to guard against rollback when edit logs are lost without a new checkpoint.

## Dependencies and Integration Points
`NNStorage` is created by `FSImage` and consumed by `FSImage`, `FSEditLog`, storage inspectors, retention management, upgrade utilities, and NameNode formatting commands. It depends on `Storage`, `StorageDirectory`, `NamespaceInfo`, `NameNodeLayoutVersion`, `LayoutVersion.Feature`, `FSImageStorageInspector`, `FileUtil`, `PersistentLongFile`, `DNS`, and Hadoop configuration keys. The static naming methods are reused directly by tests and other NameNode storage code.

## Risks and Edge Cases
- `setStorageDirectories` removes duplicate edit dirs while iterating a mutable copy; callers must not pass immutable edit collections except through the constructor's defensive copy.
- Only local `file://` URIs become `StorageDirectory` entries; non-file journals are handled elsewhere and are easy to miss when reasoning about storage coverage.
- `getDeprecatedProperty` is valid only during upgrades from old layouts; misuse is guarded only by an assertion.
- Directory removal is opportunistic: a failed write unlocks and removes the whole storage dir, so callers must tolerate reduced redundancy.
- `writeAll` returns without error on `ClosedByInterruptException`, which protects interrupt handling but can leave VERSION writes incomplete.
- Block pool ID consistency checks are strict and throw `InconsistentFSStateException` when VERSION files disagree.

## Test Signals
Relevant coverage appears in `TestStartup`, `TestNameEditsConfigs`, `TestStorageRestore`, `TestNNStorageRetentionManager`, `TestNNStorageRetentionFunctional`, `TestNNUpdateStorageVersionWhenInterrupt`, and `TestNameNodeRecovery`. These tests exercise file naming, format/restart behavior, storage restore after failures, retention interaction, interrupted VERSION writes, and recovery against corrupted edit/image storage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NNStorage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NNStorageRetentionManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NNStorageRetentionManager.java

## Purpose
`NNStorageRetentionManager` enforces configured NameNode metadata retention. It inspects fsimage files, decides which checkpoints to keep, calculates how many historical edit transactions and edit segments to retain, and delegates deletion or stale marking to a `StoragePurger`.

## Important APIs and Types
- Constructors read `dfs.namenode.num.checkpoints.retained`, `dfs.namenode.num.extra.edits.retained`, and `dfs.namenode.max.extra.edits.segments.retained`, validating non-negative/positive policy values.
- `purgeOldStorage(NameNodeFile nnf)` is the main policy method for normal fsimage families.
- `purgeCheckpoints` and `purgeCheckpoinsAfter` remove checkpoint images of a given type, optionally filtered by txid.
- `StoragePurger` abstracts `purgeLog`, `purgeImage`, and `markStale`; `DeletionStoragePurger` deletes image files plus `.md5` digest files and can move stale in-progress logs aside.
- `purgeOldLegacyOIVImages` handles OIV image directories that are not full `StorageDirectory` roots.

## Control Flow
`purgeOldStorage` creates a transactional storage inspector, asks `NNStorage` to inspect all storage dirs, chooses the oldest image txid that must be retained, purges older images, then skips edit purging for rollback images. For normal images it sets `minimumRequiredTxId` to `minImageTxId + 1`, chooses `purgeLogsFrom` with the configured extra-edit cushion, selects candidate logs from `LogsPurgeable`, sorts them by first and last txid, removes logs that are required for recovery, constrains retained extra segments by `maxExtraEditsSegmentsToRetain`, verifies it is not purging beyond the required txid, and finally calls `purgeLogsOlderThan`.

## State and Persistence Behavior
This class owns no durable state; it mutates durable metadata by deleting files or renaming stale in-progress edit logs through the purger. Its retention decisions are derived from current storage-directory listings and edit-log stream metadata. Image digest sidecars are deleted with image files.

## Dependencies and Integration Points
It integrates with `NNStorage`, `FSImageTransactionalStorageInspector`, `FSImageFile`, `LogsPurgeable`, `EditLogInputStream`, `FileJournalManager.EditLogFile`, `NNStorage.NameNodeFile`, `MD5FileUtils`, and DFS retention configuration. It is typically invoked by `FSImage` after checkpoint/save operations and when old storage needs cleanup.

## Risks and Edge Cases
- Retention is txid-based across all discovered image dirs; inconsistent listings or missing images can shift the edit-log retention boundary.
- `purgeLogsFrom` is adjusted to keep no more than the configured number of extra segments, so low segment limits may reduce the historical edit cushion.
- Delete failures are logged and retried on future retention passes, not fatal.
- `purgeCheckpoinsAfter` has a misspelled method name but is part of internal call sites.
- Legacy OIV cleanup parses file names manually after regex filtering; invalid names are logged and skipped.

## Test Signals
`TestNNStorageRetentionManager` covers policy calculations and purger behavior, while `TestNNStorageRetentionFunctional` exercises retention through a live `MiniDFSCluster`, saveNamespace, rollEditLog, and real file names from `NNStorage`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NNStorageRetentionManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NNUpgradeUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NNUpgradeUtil.java

## Purpose
`NNUpgradeUtil` is a static helper for NameNode storage directory upgrade lifecycle operations: pre-upgrade staging, upgrade completion, finalize, rollback capability checks, and rollback execution.

## Important APIs and Types
- `canRollBack(StorageDirectory, StorageInfo, StorageInfo, int)` validates whether a `previous` directory can roll back to a target layout version.
- `doPreUpgrade(Configuration, StorageDirectory)` renames `current` to `previous.tmp`, creates a new `current`, and hard-links existing edit log files into it.
- `renameCurToTmp(StorageDirectory)` performs the invariant-checked `current` to `previous.tmp` transition.
- `doUpgrade(StorageDirectory, Storage)` writes new VERSION properties and promotes `previous.tmp` to `previous`.
- `doFinalize(StorageDirectory)` removes the rollback snapshot by renaming `previous` to `finalized.tmp` and deleting it.
- `doRollBack(StorageDirectory)` removes current state and restores `previous` as `current`.

## Control Flow
Pre-upgrade requires `current` to exist and both `previous` and `previous.tmp` not to exist. It renames current to tmp, recreates current, and walks one directory level of tmp without following links; regular files whose names start with `edits` are hard-linked into the new current dir so edits survive the transition. Upgrade then writes VERSION metadata into current and renames previous.tmp to previous. Finalize checks for `previous`, renames it to a temporary finalized directory, and deletes it. Rollback renames current to removed.tmp, renames previous to current, then deletes removed.tmp.

## State and Persistence Behavior
All behavior is persistent filesystem mutation on `StorageDirectory` roots. The directory names `current`, `previous`, `previous.tmp`, `removed.tmp`, and `finalized.tmp` are the state machine. VERSION files are written during `doUpgrade`; `canRollBack` reads both current and previous VERSION properties and refuses incompatible target layout versions.

## Dependencies and Integration Points
The class uses `StorageDirectory`, `Storage`, `StorageInfo`, `NNStorage.rename/deleteDir`, `Preconditions`, and Java NIO file walking/link creation. It is called by `FSImage` upgrade, rollback, and finalize code, and its behavior must stay compatible with journal managers that implement similar stages.

## Risks and Edge Cases
- Hard-link creation in `doPreUpgrade` requires filesystem support and same-volume semantics; failures abort the upgrade.
- Preconditions intentionally fail if temp directories already exist, forcing restart/recovery rather than guessing.
- `canRollBack` returns false for dirs without `previous` after reading current properties, but throws for present `previous` with incompatible layout.
- Rollback deletes the current state after moving it aside; operator confirmation happens in higher-level `NameNode.doRollback`.

## Test Signals
Upgrade and rollback behavior is exercised indirectly by `TestStartup`, `TestSecondaryNameNodeUpgrade`, rolling-upgrade tests, and rollback/recovery tests under the NameNode test package. Focused validation should cover interrupted pre-upgrade temp directories, hard-link failures, and layout-version mismatch errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NNUpgradeUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameCache.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameCache.java

## Purpose
`NameCache<K>` interns frequently repeated NameNode names during namespace loading. It reduces heap duplication for values such as file-name byte arrays referenced by `INode` objects.

## Important APIs and Types
- `NameCache(int useThreshold)` configures the promotion threshold.
- `put(K name)` returns an existing cached/internal value when available, tracks use counts during initialization, promotes names that meet the threshold, and returns null for uncached names after initialization.
- `initialized()` marks the cache ready for steady-state lookup and discards the transient use-count map.
- `reset()` clears the cache and re-enters initialization mode.
- Inner `UseCount` stores the first internal value and its count.

## Control Flow
During initialization, `put` first checks the permanent cache. On a hit it increments `lookups` and returns the canonical value. On a transient hit it increments the count, promotes at or above threshold, and returns the first-seen value. On a new name it inserts a `UseCount`. After `initialized`, the transient map is null and new uncached names are not counted; only permanent cache hits return canonical objects.

## State and Persistence Behavior
All state is in-memory: `cache`, `transientMap`, `lookups`, and `initialized`. There is no disk persistence. The class explicitly requires external synchronization; callers must serialize all mutations and lookups.

## Dependencies and Integration Points
It is package-private to the NameNode namespace code and used by inode/fsimage loading paths. It depends only on Java collections and SLF4J.

## Risks and Edge Cases
- `initialized()` sets `transientMap` to null after clearing it; calling initialization-path code without respecting `initialized` would NPE, but `put` guards that path.
- `promote` increments lookup count by the threshold, so lookup metrics include estimated savings from promotion.
- A threshold of zero or negative is not validated here; callers must provide sane values or every repeated/new path may behave unexpectedly.
- Thread safety is entirely external.

## Test Signals
`TestNameCache` is the direct unit test target. Useful assertions include promotion threshold behavior, canonical return values before and after initialization, lookup counts, and `reset()` rebuilding the transient map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNode.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeFormatException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeFormatException.java

## Purpose
`NameNodeFormatException` is a specific `IOException` used when NameNode formatting is rejected or fails for semantic reasons, such as reformat being disabled while metadata already exists.

## Important APIs and Types
- Public constructor `NameNodeFormatException(String message, Throwable cause)`.
- Public constructor `NameNodeFormatException(String message)`.
- `serialVersionUID` is defined for exception serialization compatibility.

## Control Flow
The class has no logic beyond exception construction. Higher-level format code throws it to distinguish format failures from generic I/O failures while preserving `IOException` compatibility.

## State and Persistence Behavior
No state beyond the exception message/cause. It does not perform persistence; it reports decisions made by `NameNode.format` and related format checks.

## Dependencies and Integration Points
It extends `java.io.IOException`, is annotated `@InterfaceAudience.Private`, and is used by `NameNode.format` when reformat is disabled by configuration and existing storage data is detected.

## Risks and Edge Cases
Because it is an `IOException`, callers that catch broad I/O failures may not distinguish operator-policy format aborts unless they check the concrete type or message. That is acceptable for current internal use but limits machine-readable failure handling.

## Test Signals
Format tests such as `TestStartup` and NameNode format/configuration tests are the expected integration coverage. A focused test should assert this exception type when `dfs.reformat.disabled` blocks formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeFormatException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeHttpServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeHttpServer.java

## Purpose
`NameNodeHttpServer` encapsulates the NameNode's Jetty/HttpServer2 web endpoint. It configures HTTP/HTTPS connectors, WebHDFS Jersey resources and filters, internal servlets, servlet-context attributes for NameNode services, and exposes bound addresses to the parent `NameNode`.

## Important APIs and Types
- Constructor `NameNodeHttpServer(Configuration, NameNode, InetSocketAddress)` stores the config, owning NameNode, and bind address.
- `start`, `stop`, and `join` manage the underlying `HttpServer2`.
- `initWebHdfs` configures WebHDFS path resources, parameter filters, user providers, ACL pattern validation, and optional REST CSRF prevention.
- Setters `setFSImage`, `setNameNodeAddress`, `setStartupProgress`, and `setAliasMap` publish objects into the servlet context.
- Static context getters retrieve `FSImage`, `NameNode`, `TokenVerifier`, `Configuration`, `InMemoryAliasMap`, NameNode address, startup progress, and HA state.
- `setupServlets` installs startup progress, fsck, image transfer, active-state, and network topology servlets.

## Control Flow
`start` reads the HTTP policy, derives HTTP and HTTPS bind addresses with bind-host overrides, builds the server from `DFSUtil.getHttpServerTemplate`, configures X-Frame-Options, stores the DataNode HTTPS port when HTTPS is enabled, initializes WebHDFS resources, sets base context attributes, installs internal servlets, starts the server, records connector addresses, and writes bound host:port values back to configuration.

## State and Persistence Behavior
Runtime state consists of the `HttpServer2` instance and bound `httpAddress`/`httpsAddress`. It does not persist metadata itself, but it exposes persistent metadata services through `ImageServlet` and WebHDFS endpoints and shares live `FSImage`/NameNode objects through servlet attributes.

## Dependencies and Integration Points
It depends on `HttpServer2`, `DFSUtil`, `HttpConfig.Policy`, Jersey `ResourceConfig`, WebHDFS parameter/resource classes, `RestCsrfPreventionFilter`, `ParamFilter`, `JspHelper`, `StartupProgressServlet`, `FsckServlet`, `ImageServlet`, `IsNameNodeActiveServlet`, `NetworkTopologyServlet`, and optional `InMemoryAliasMap`. `NameNode.initialize` starts it and fills attributes after loading the namesystem.

## Risks and Edge Cases
- Bind-host overrides can make advertised and bound addresses differ; tests must check both.
- WebHDFS CSRF protection is conditional and path-scoped to `/webhdfs/*`; misconfiguration changes REST write exposure.
- Servlet attribute population order matters: servlets needing `FSImage` or alias map must be used after `NameNode` sets them.
- HTTP/HTTPS connector index handling assumes the builder creates connectors in policy order.
- X-Frame options are passed through config and should reject/handle illegal values in lower HttpServer layers.

## Test Signals
`TestNameNodeHttpServer`, `TestNameNodeHttpServerXFrame`, `TestNameNodeRespectsBindHostKeys`, WebHDFS tests, and image-transfer/fsck tests are the relevant coverage. Important cases include HTTP-only, HTTPS-enabled, X-Frame enabled/disabled/invalid, bind host overrides, CSRF filter installation, and context getter correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeHttpServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeLayoutVersion.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeLayoutVersion.java

## Purpose
`NameNodeLayoutVersion` defines NameNode metadata layout features and the version-to-feature map used to decide storage compatibility, rolling-upgrade downgrade compatibility, and feature support for fsimage/edit processing.

## Important APIs and Types
- `FEATURES` maps layout version integers to sorted sets of `LayoutFeature`.
- `CURRENT_LAYOUT_VERSION` and `MINIMUM_COMPATIBLE_LAYOUT_VERSION` are derived from the declared feature enum.
- `getFeatures(int lv)` returns features for a layout version.
- `supports(LayoutFeature f, int lv)` checks feature support against the NameNode feature map.
- `Feature` enum lists NameNode-specific layout changes from rolling upgrade through NVDIMM support, each carrying `FeatureInfo`.

## Control Flow
Static initialization merges common `LayoutVersion.Feature` values and NameNode-specific `Feature` values into `FEATURES`. Each enum constant declares its layout version, ancestor layout where needed, minimum compatible version, and description. Compatibility checks are delegated to `LayoutVersion.supports`.

## State and Persistence Behavior
There is no mutable runtime state after class initialization. The values directly control persistent metadata compatibility: VERSION layout numbers and feature-gated fsimage/edit behavior must match this table.

## Dependencies and Integration Points
`NNStorage`, fsimage loaders/savers, edit-log code, upgrade/rollback logic, and rolling-upgrade flows call `NameNodeLayoutVersion.supports` or use `CURRENT_LAYOUT_VERSION`. It depends on `LayoutVersion`, `LayoutVersion.FeatureInfo`, and `LayoutVersion.LayoutFeature`.

## Risks and Edge Cases
- Adding a feature with the wrong ancestor or minimum compatible version can break rolling downgrade guarantees.
- `getFeatures` may return null for unknown layout versions; callers need to handle invalid versions through higher-level storage checks.
- Feature descriptions are documentation, but the numeric version and compatibility values are operationally critical.

## Test Signals
Coverage is usually indirect through fsimage/edit-log compatibility, upgrade, rollback, and rolling-upgrade tests. `TestNameNodeRecovery`, `TestStartup`, and upgrade tests exercise current layout values when creating or reading metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeLayoutVersion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeMXBean.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeMXBean.java

## Purpose
`NameNodeMXBean` is the stable private JMX management contract for NameNode cluster state, capacity, health, storage, version, corrupt files, DataNode status, cache, upgrade, and topology validation information.

## Important APIs and Types
The interface exposes getters for software version, raw/DFS/provided capacity, safe mode, upgrade and rolling-upgrade status, block counts and missing/low-redundancy counts, snapshottable directory count, live/dead/decommissioning/maintenance nodes, cluster and block-pool IDs, name-dir and journal status, transaction info, compile info, corrupt files, DataNode version distribution, name-dir size, cache capacity/usage, and EC topology verification.

## Control Flow
There is no implementation logic in this file. Implementations, primarily `FSNamesystem`/NameNode management classes, populate these methods and register them with the Hadoop metrics/JMX subsystem. Callers access the values through JMX rather than implementing the interface themselves.

## State and Persistence Behavior
No state is stored here. Method results reflect live NameNode state and persisted metadata as exposed by the implementation. Several methods intentionally return JSON strings, making the serialized shape part of the management contract.

## Dependencies and Integration Points
The interface imports `RollingUpgradeInfo.Bean` and returns Java primitives, strings, and `Map<String,Integer>`. `TestNameNodeMXBean`, metrics tooling, dashboards, and operators depend on these names and return types.

## Risks and Edge Cases
- JSON-returning strings are weakly typed; schema changes can break external monitoring.
- Adding/removing methods affects JMX consumers even though the interface is marked private to Hadoop.
- Capacity metrics combine values from DataNodes, block manager, and provided storage; implementation consistency matters more than this contract file.

## Test Signals
`TestNameNodeMXBean` is the direct integration signal. Metrics tests and NameNode web/JMX assertions validate that values are registered and reflect live cluster changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeResourceChecker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeResourceChecker.java

## Purpose
`NameNodeResourceChecker` builds the set of local volumes whose free disk space must be checked before the NameNode continues writing edits. It covers local edits dirs and configured extra checked volumes, classifies required versus redundant volumes, and delegates policy evaluation to `NameNodeResourcePolicy`.

## Important APIs and Types
- Constructor `NameNodeResourceChecker(Configuration)` reads reserved bytes, checked volume config, local edits dirs, required edits dirs, and minimum redundant volume count.
- Inner `CheckedVolume` implements `CheckableNameNodeResource` using Hadoop `DF` to check available bytes on a filesystem.
- `hasAvailableDiskSpace()` returns the resource policy result.
- Testing hooks include `getVolumesLowOnSpace`, `setVolumes`, and `setMinimumReduntdantVolumes`.

## Control Flow
Construction resolves extra checked volumes from `dfs.namenode.checked.volumes`, filters namespace edits dirs to local `file` URIs, adds each edits dir with required status based on `FSNamesystem.getRequiredNamespaceEditsDirs`, adds extra dirs as required, and stores the minimum redundant volume threshold. `addDirToCheck` requires the directory to exist, collapses multiple directories on the same filesystem to one `CheckedVolume`, and upgrades an existing redundant volume to required if necessary.

## State and Persistence Behavior
All state is runtime-only: `duReserved`, `volumes`, and `minimumRedundantVolumes`. It does not modify disk. `CheckedVolume.isResourceAvailable` reads current filesystem free space and compares it with reserved bytes, logging warnings for low space.

## Dependencies and Integration Points
It depends on `FSNamesystem` for namespace edits dir config, `NNStorage.LOCAL_URI_SCHEME`, `Util.stringCollectionAsURIs`, Hadoop `DF`, DFS config keys, and `NameNodeResourcePolicy`. `FSNamesystem` resource monitoring and `NameNode.monitorHealth` use this path to enter safe mode or fail HA health checks when resources are exhausted.

## Risks and Edge Cases
- Missing checked directories cause constructor failure.
- Only local edits dirs are checked here; remote/shared journal health is handled elsewhere.
- Multiple configured dirs on the same filesystem collapse to one resource, which is correct for disk-space accounting but can surprise config audits.
- `getVolumesLowOnSpace` currently returns all volume names after invoking debug logging; despite its name, it does not filter by availability in this implementation.
- The testing method name `setMinimumReduntdantVolumes` contains a typo.

## Test Signals
`TestNameNodeResourceChecker` covers constructor behavior, required/redundant volume policy, monitor integration with safe mode, and mock resource checkers. Metrics tests also exercise low-resource reporting through NameNode state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeResourceChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeResourcePolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeResourcePolicy.java

## Purpose
`NameNodeResourcePolicy` evaluates a collection of required and redundant NameNode resources and decides whether enough are available for the NameNode to continue safely logging edits.

## Important APIs and Types
- Static `areResourcesAvailable(Collection<? extends CheckableNameNodeResource>, int minimumRedundantResources)` is the single policy entry point.
- It consumes `CheckableNameNodeResource`, whose methods distinguish required resources and availability.

## Control Flow
An empty resource collection returns true as a startup workaround for configurations without local disk edits dirs. The method scans resources once. A required resource that is unavailable short-circuits to false. Redundant resources are counted, and unavailable redundant resources are counted separately. If there are no redundant resources, the policy succeeds when at least one required resource exists. Otherwise it succeeds only when available redundant resources are at least `minimumRedundantResources`; failures are logged with counts.

## State and Persistence Behavior
This is a stateless policy class with no persistence and no side effects except logging. Availability checks may have side effects in the resource implementations, such as disk-space logging.

## Dependencies and Integration Points
It is package-private and used by `NameNodeResourceChecker`. Its result feeds FSNamesystem resource monitoring and NameNode HA health checks.

## Risks and Edge Cases
- Empty resources returning true is intentional but can mask unexpected configuration bugs if upstream accidentally supplies no resources.
- Required resources dominate redundant policy: one required failure fails the whole check.
- `minimumRedundantResources` is not validated here; callers must ensure sane non-negative values.
- Availability is evaluated during iteration, so expensive resources can make health checks slow.

## Test Signals
`TestNameNodeResourcePolicy` directly covers combinations of required and redundant resources, empty resources, threshold failures, and log emission. `TestNameNodeResourceChecker` covers integration with real volume configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeResourcePolicy.java -->
