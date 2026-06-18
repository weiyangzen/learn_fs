# subset-b-000469 research

This grouped report covers the requested Alluxio server-common RPC, formatting, extension shell, master lifecycle, backup, journal, checkpoint, noop journal, and journal option files. Each file section is wrapped with source-path markers for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/RpcUtils.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/RpcUtils.java

## Purpose
`RpcUtils` centralizes server-side gRPC call wrapping for Alluxio masters: timing, in-progress/failure metrics, debug logging, sensitive argument masking, exception translation to gRPC status, and observer completion.

## Important APIs, Types, And Functions
The main entry points are `call`, `callAndReturn`, `invoke`, and `streamingRPCAndLog`. `RpcCallableThrowsIOException` models unary RPC bodies that throw Alluxio/IO exceptions, while `StreamingRpcCallable` adds an `exceptionCaught` hook for stream failure handling. Metric names are decorated with authenticated user tags when present.

## Control Flow, State, Dependencies, Risks, And Tests
Unary calls enter timers, increment in-progress counters, execute the callable, translate `AlluxioRuntimeException`, `AlluxioException`, and `IOException`, and always decrement the counter. Async `invoke` attaches a `whenComplete` callback to a future. Streaming calls optionally send and complete observer responses. State is limited to metrics and logging; no persistence occurs. Dependencies include gRPC observers/statuses, `MetricsSystem`, authentication context, and `SensitiveConfigMask`. Risks include missed counter balance if observer callbacks throw, masking gaps in non-debug streaming error formatting, and broad `RuntimeException | LinkageError` conversion to internal errors. Tests should assert observer events, metric increments/decrements, exception mapping, failure-ok behavior, and sensitive argument masking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/RpcUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/cli/Format.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/cli/Format.java

## Purpose
`Format` is the command-line formatter for Alluxio master journals and worker data directories.

## Important APIs, Types, And Functions
`Mode` distinguishes `MASTER` and `WORKER`. `main` parses the mode, sets the process type to master for journal access, and calls `format`. `formatWorkerDataFolder` deletes/recreates worker folders, applies configured permissions, and sets the sticky bit. `format` builds a journal system for all enabled master services or formats all configured worker tier directories.

## Control Flow, State, Dependencies, Risks, And Tests
Master formatting resolves the journal URI, creates `NoopMaster` journals for every enabled master service, and invokes `JournalSystem.format`. Worker formatting iterates tiered-store levels and directory lists, deriving the worker data directory under each storage path. The command mutates persistent journal storage or local worker storage. Dependencies include `JournalUtils`, `ServiceUtils`, `FileUtils`, `CommonUtils`, and configuration keys. Risks are destructive deletion, POSIX permission assumptions, comma-split directory parsing, and formatting an unintended journal location. Tests should cover invalid modes, master service discovery, journal format calls, tier directory expansion, permission application, and failure exit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/cli/Format.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/cli/extensions/ExtensionsShell.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/cli/extensions/ExtensionsShell.java

## Purpose
`ExtensionsShell` is the top-level shell for managing Alluxio extension jars.

## Important APIs, Types, And Functions
The package-private constructor passes the global configuration to `AbstractShell`. `main` creates the shell and exits with the shell return code. `getShellName` returns `extensions`, and `loadCommands` discovers command implementations from the same package.

## Control Flow, State, Dependencies, Risks, And Tests
The shell delegates parsing, help, and command dispatch to `AbstractShell`; this class only wires discovery and naming. It has no persistence itself, but commands it loads mutate extension directories on local and remote hosts. Dependencies include `CommandUtils`, `Configuration`, and the CLI command package. Risks are classpath/service discovery failures and command packages being renamed without updating loader assumptions. Tests should verify command loading, shell name, dispatch to `install`, `ls`, and `uninstall`, and process exit propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/cli/extensions/ExtensionsShell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/cli/extensions/command/InstallCommand.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/cli/extensions/command/InstallCommand.java

## Purpose
`InstallCommand` installs an Alluxio extension jar to every configured master and worker host.

## Important APIs, Types, And Functions
It implements `Command` with name `install`, usage `install <URI>`, and `run`/`validateArgs`. `run` ensures the configured extension directory exists locally, then executes remote `rsync` over ssh for each host from `ConfigurationUtils.getServerHostnames`.

## Control Flow, State, Dependencies, Risks, And Tests
Argument validation requires exactly one non-null argument ending with `Constants.EXTENSION_JAR`. Runtime state is the local extension directory plus remote extension jar copies. Dependencies include configuration, `ShellUtils`, ssh/rsync, and host files. Risks include shell-string injection through URI or directory values, partial installation across hosts, local directory creation not guaranteeing remote parent existence, and reliance on external commands. Tests should mock host lists and command execution, check jar suffix validation, verify partial failure reporting, and cover directory creation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/cli/extensions/command/InstallCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/cli/extensions/command/LsCommand.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/cli/extensions/command/LsCommand.java

## Purpose
`LsCommand` lists installed extension jar names from the configured extension directory.

## Important APIs, Types, And Functions
It implements `Command` with name and usage `ls`. `validateArgs` requires zero arguments. `run` calls `ExtensionUtils.listExtensions` with `PropertyKey.EXTENSIONS_DIR` and prints each returned file name.

## Control Flow, State, Dependencies, Risks, And Tests
The command has read-only behavior against local extension directory state. Dependencies are `Configuration`, `PropertyKey`, and `ExtensionUtils`. The declared logger is unused. Risks are silent empty output when the directory is inaccessible or absent depending on `ExtensionUtils` behavior, and local-only visibility while install/uninstall operate across hosts. Tests should cover zero-argument validation, sorted or unsorted output contract from `ExtensionUtils`, absent directory behavior, and jar filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/cli/extensions/command/LsCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/cli/extensions/command/UninstallCommand.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/cli/extensions/command/UninstallCommand.java

## Purpose
`UninstallCommand` removes an extension jar from every configured master and worker host.

## Important APIs, Types, And Functions
It implements `Command` with name `uninstall`, usage `uninstall <JAR>`, and remote removal in `run`. `validateArgs` requires one non-null jar name ending in `Constants.EXTENSION_JAR`. `PathUtils.concatPath` combines the extension directory and jar argument for the remote `rm`.

## Control Flow, State, Dependencies, Risks, And Tests
For each server host, the command executes `ssh ... rm <extensionsDir>/<jar>`, records failed hosts, and returns `-1` on any failure. It mutates remote extension directory contents and does not alter service classloaders already running. Dependencies include ssh, shell command execution, configuration, and host discovery. Risks include shell injection via jar names, partial uninstall, no existence precheck, and removal of unintended paths if path joining or arguments are unsafe. Tests should mock command execution, validate jar suffix rules, verify failed-host reporting, and cover host-list iteration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/cli/extensions/command/UninstallCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/executor/ExecutorServiceBuilder.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/executor/ExecutorServiceBuilder.java

## Purpose
`ExecutorServiceBuilder` constructs configured RPC executor services for master, job master, and worker processes.

## Important APIs, Types, And Functions
`buildExecutorService` reads per-host configuration templates, validates keepalive and fork-join parameters, creates either Alluxio's JSR `ForkJoinPool` or a Java `ThreadPoolExecutor`, and wraps it in `AlluxioExecutorService`. `RpcExecutorHost` maps enum values to configuration prefixes.

## Control Flow, State, Dependencies, Risks, And Tests
The builder first resolves executor type, shared pool sizes, and thread naming. FJP mode reads parallelism, min-runnable, and async mode; TPE mode selects linked, bounded linked, array, or synchronous queues and applies core-thread timeout. State is runtime thread/queue state, not persistent. Dependencies include `Configuration`, `PropertyKey.Template`, `ThreadFactoryUtils`, `ForkJoinPool`, queue enums, and metrics counters. Risks include bad configuration causing startup failure, bounded queue sizing tied to max pool size, and an error message referencing master max pool for all hosts. Tests should cover every executor type/queue type, invalid values, thread naming, counter wrapping, and host prefix strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/executor/ExecutorServiceBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/AbstractMaster.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/AbstractMaster.java

## Purpose
`AbstractMaster` is the base implementation for Alluxio master services, providing common lifecycle, executor, journal creation, and state-lock-aware journal context handling.

## Important APIs, Types, And Functions
The constructor stores `MasterContext`, `Clock`, an `ExecutorServiceFactory`, and creates this master's journal from the journal system. `start` creates the maintenance executor and records primary/standby mode. `stop` interrupts and waits for executor shutdown. `createJournalContext` acquires the shared state lock and wraps the journal context in `StateChangeJournalContext`.

## Control Flow, State, Dependencies, Risks, And Tests
Primary startup is expected to occur after journal replay and before RPC serving, while state mutations later journal through a shared lock so backups can pause them. Persistent state is owned by the journal; this class guards writes through `JournalContext`. Dependencies include `JournalSystem`, `StateLockManager`, `ExecutorServiceFactory`, and `LockResource`. Risks include non-thread-safe lifecycle, failure to release locks when journal context creation fails, and executor shutdown timeout leaving background work. Tests should cover start/stop idempotency expectations, lock acquisition failure mapping to `UnavailableException`, and `StateChangeJournalContext` close ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/AbstractMaster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/AbstractPrimarySelector.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/AbstractPrimarySelector.java

## Purpose
`AbstractPrimarySelector` supplies synchronization and listener mechanics for implementations that detect whether a master is primary or standby.

## Important APIs, Types, And Functions
Subclasses call protected `setState(NodeState)`. Public APIs implement `getState`, lock-free `getStateUnsafe`, `onStateChange`, and `waitForState`. Listeners are wrapped in unique `AtomicReference` instances and removed through a returned `Scoped`.

## Control Flow, State, Dependencies, Risks, And Tests
State starts as `STANDBY`. `setState` locks, updates state, signals waiters, invokes listeners synchronously, and logs. The state is in-memory coordination state only. Dependencies include `NodeState`, `LockResource`, Java locks/conditions, and `Scoped`. Risks include slow or throwing listeners running inside the state lock, listener set uniqueness based on wrapper identity rather than listener equality, and `getStateUnsafe` observing volatile state without coordinated waits. Tests should verify wait wakeups, listener registration/removal, state ordering, concurrent state transitions, and listener exception behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/AbstractPrimarySelector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/AlluxioExecutorService.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/AlluxioExecutorService.java

## Purpose
`AlluxioExecutorService` wraps an `ExecutorService` to expose RPC queue/active/pool metrics and optionally warn about active operations during shutdown.

## Important APIs, Types, And Functions
`getRpcQueueLength`, `getActiveCount`, and `getPoolSize` support `ThreadPoolExecutor` and Alluxio `ForkJoinPool`. All standard `ExecutorService` methods delegate, except `invokeAny` variants throw unsupported. Submission and execution methods briefly increment/decrement an optional `Counter`.

## Control Flow, State, Dependencies, Risks, And Tests
The wrapper does not own persistence; it exposes live executor state. Dependencies are Java executor APIs, Alluxio `ForkJoinPool`, Dropwizard `Counter`, and logging. A key risk is that the counter measures submission calls, not task lifetime, because it is decremented immediately after delegation; shutdown warnings may therefore not reflect active queued/running RPCs unless the counter has separate external tracking. Unsupported executor types throw for metric methods. Tests should cover metric delegation for both executor classes, shutdown warnings, counter behavior, and unsupported `invokeAny`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/AlluxioExecutorService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/AlwaysStandbyPrimarySelector.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/AlwaysStandbyPrimarySelector.java

## Purpose
`AlwaysStandbyPrimarySelector` is a trivial primary selector used where a master must never become primary, such as noop/test contexts.

## Important APIs, Types, And Functions
`start` and `stop` do nothing. `getState` and `getStateUnsafe` always return `NodeState.STANDBY`. `onStateChange` returns a no-op unregistration scope. `waitForState` returns immediately for standby and sleeps indefinitely for primary.

## Control Flow, State, Dependencies, Risks, And Tests
There is no mutable state or persistence. Dependencies are `NodeState`, `Scoped`, and `InetSocketAddress`. Risks include `Thread.sleep(Long.MAX_VALUE)` being the primary wait implementation, which relies on interruption for cancellation, and no listener notification ever occurring. Tests should verify standby immediacy, primary wait interruptibility, no-op lifecycle, and no-op listener behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/AlwaysStandbyPrimarySelector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/BackupManager.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/BackupManager.java

## Purpose
`BackupManager` creates gzip backups from all master journal entries and restores master state from such backups.

## Important APIs, Types, And Functions
`backup(OutputStream, AtomicLong)` streams journal entries from every registered master to a gzip output stream using reader/writer tasks and a bounded queue. `initFromBackup(InputStream)` reads gzip-delimited journal entries, maps each entry to its owning master via `JournalEntryAssociation`, and applies/journals batches through per-master `JournalContext`s. `safeWaitTasks` coordinates worker failures and cancellation.

## Control Flow, State, Dependencies, Risks, And Tests
Backup registers gauges for last backup/restore counts and durations. Backup writes a termination sentinel sequence number and finishes, not closes, the caller-owned stream. Restore schedules progress logging, drains batches, opens contexts for all masters, applies entries, then closes contexts to flush. Persistent behavior is serialized gzip journal entries and restored master journal/state. Dependencies include `MasterRegistry`, `JournalEntryStreamReader`, gzip streams, metrics, executor services, and `JournalUtils`. Risks include partial backups if a writer fails late, unbounded per-drain list size, sentinel collision assumptions, restore fatality on unrecognized entries, and context creation for all masters per batch. Tests should cover backup/restore round trips, failure cancellation, corrupted/truncated input, master association, metrics, and queue backpressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/BackupManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/Master.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/Master.java

## Purpose
`Master` defines the common contract for Alluxio master services.

## Important APIs, Types, And Functions
It extends `Journaled` and `Server<Boolean>`, requiring lifecycle, service, journaling, checkpoint, and journal-entry iteration behavior. It adds `createJournalContext`, `getMasterContext`, and default `getStandbyServices`.

## Control Flow, State, Dependencies, Risks, And Tests
Implementations use `createJournalContext` for persistent journal writes and `Journaled` methods for replay/checkpoint. Standby services default to none. Dependencies include gRPC service descriptors, `ServiceType`, journal contexts, and server lifecycle APIs. Risks are broad implementor responsibility: state changes must both mutate memory and journal consistently, and standby service exposure is optional. Tests should validate each master implementation's service maps, context creation behavior, journal replay support, and lifecycle interaction with primary/standby booleans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/Master.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/MasterContext.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/MasterContext.java

## Purpose
`MasterContext` groups shared dependencies required by master implementations.

## Important APIs, Types, And Functions
Constructors require `JournalSystem`, `PrimarySelector`, and a typed `UfsManager`; an optional `UserState` defaults to `ServerUserState.global`. Accessors expose journal system, primary selector, user state, state lock manager, and UFS manager.

## Control Flow, State, Dependencies, Risks, And Tests
The context is immutable except for the internally mutable `StateLockManager`. It carries no persisted state directly, but points masters to journal and UFS persistence. Dependencies include `JournalSystem`, `PrimarySelector`, `UfsManager`, and user-state classes. Risks include raw-type use in some callers, global user-state fallback complicating tests, and every context creating its own state lock manager. Tests should assert null rejection, default user-state selection, typed UFS manager access, and shared lock manager availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/MasterContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/MasterFactory.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/MasterFactory.java

## Purpose
`MasterFactory` is the service-provider contract for discovering and constructing master services.

## Important APIs, Types, And Functions
Implementations expose `isEnabled`, `getName`, and `create(MasterRegistry, T context)`. The generic type binds factories to their required `MasterContext` subtype.

## Control Flow, State, Dependencies, Risks, And Tests
Factories are loaded by `ServiceLoader` through `ServiceUtils`, then used to create masters and journal placeholders. There is no direct persistence. Dependencies are the master registry and context classes. Risks include service-loader metadata omissions, raw generic usage in `ServiceUtils`, and `getName` stability because journal/checkpoint naming depends on it. Tests should cover service loading, disabled factories being skipped, stable names, and create-time dependency registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/MasterFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/MasterRegistry.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/MasterRegistry.java

## Purpose
`MasterRegistry` is the typed registry for Alluxio master services.

## Important APIs, Types, And Functions
It extends `Registry<Master, Boolean>` and only provides a public constructor.

## Control Flow, State, Dependencies, Risks, And Tests
The inherited registry owns dependency ordering, startup, shutdown, and server lists; the Boolean option is passed to master `start` to indicate primary mode. It does not persist data. Dependencies are `Registry` and `Master`. Risks are all behavior being inherited, so changes in `Registry` affect master orchestration. Tests should focus on registry integration: dependency ordering, Boolean propagation, server enumeration for backups, and thread-safety inherited from `Registry`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/MasterRegistry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/NoopMaster.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/NoopMaster.java

## Purpose
`NoopMaster` is a placeholder master for tests and formatting paths that require a master identity without real services or state.

## Important APIs, Types, And Functions
Constructors accept default/custom names and optional `UfsManager`, building a `MasterContext` with `NoopJournalSystem` and `AlwaysStandbyPrimarySelector`. It implements `Master` and `NoopJournaled`, returns its name/context, no-ops lifecycle, and rejects `createJournalContext`.

## Control Flow, State, Dependencies, Risks, And Tests
There is no persisted state. The class is integrated by `Format` and journal setup to create named journals without real masters. Dependencies include noop journal and primary selector classes. Risks include returning `null` from `getDependencies` and `getServices`, which can surprise callers expecting empty collections, and illegal journal context creation. Tests should cover constructors, name propagation, context composition, no-op checkpoint behavior, and callers' tolerance of null service/dependency maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/NoopMaster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/NoopUfsManager.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/NoopUfsManager.java

## Purpose
`NoopUfsManager` is a UFS manager that suppresses under-storage connection work for tests and journal formatting.

## Important APIs, Types, And Functions
It extends `AbstractUfsManager` and overrides `connectUfs(UnderFileSystem fs)` with an empty implementation.

## Control Flow, State, Dependencies, Risks, And Tests
The inherited manager may still track mounts and UFS resources, but connection side effects are skipped. No persistence is performed by this override. Dependencies include `AbstractUfsManager` and `UnderFileSystem`. Risks are using it outside tests/formatting where actual UFS connectivity or authentication setup is required. Tests should verify operations that instantiate noop masters do not attempt UFS connects and that inherited manager behavior remains acceptable for formatting contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/NoopUfsManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/PrimarySelector.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/PrimarySelector.java

## Purpose
`PrimarySelector` defines how a master determines and observes primary/standby leadership.

## Important APIs, Types, And Functions
The nested `Factory` creates ZooKeeper-backed selectors for master and job master using configured addresses and election/leader paths. The interface defines `start`, `stop`, `getState`, `getStateUnsafe`, `onStateChange`, and `waitForState`.

## Control Flow, State, Dependencies, Risks, And Tests
Implementations coordinate in-memory leadership state and external election state. The factory returns `UfsJournalMultiMasterPrimarySelector`, linking leader election to UFS journal multi-master operation. No persistent state is defined here, but election paths in ZooKeeper are external coordination state. Risks include configuration mixups between master and job master paths, synchronous listener execution expectations, and unsafe state reads. Tests should cover factory property usage, lifecycle calls, listener cleanup, wait semantics, and integration with journal mode transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/PrimarySelector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/SafeModeManager.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/SafeModeManager.java

## Purpose
`SafeModeManager` defines the minimal contract for master safe-mode state.

## Important APIs, Types, And Functions
It declares notifications for primary master start and RPC server start, plus `isInSafeMode`.

## Control Flow, State, Dependencies, Risks, And Tests
Implementations typically transition out of safe mode only after leadership and RPC readiness conditions are satisfied. This interface has no direct persistence or dependencies beyond the master package. Risks are semantic ambiguity if implementations interpret the notifications differently, especially during failover or restart. Tests should target concrete implementations for transition order, repeated notifications, and RPC rejection while `isInSafeMode` is true.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/SafeModeManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/ServiceUtils.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/ServiceUtils.java

## Purpose
`ServiceUtils` centralizes discovery of enabled master service factories.

## Important APIs, Types, And Functions
`getMasterServiceLoader` returns a synchronized `ServiceLoader<MasterFactory>` using the `MasterFactory` class loader. `getMasterServiceNames` iterates factories and returns names for enabled services.

## Control Flow, State, Dependencies, Risks, And Tests
The utility is read-only but drives journal formatting and master startup composition. Dependencies include Java `ServiceLoader` and `MasterFactory`. Risks include raw type warnings, repeated service loading costs, disabled factory filtering differences between formatting and startup, and name stability across releases. Tests should use test service providers to verify loading, filtering, ordering assumptions, and failure behavior for misconfigured factories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/ServiceUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/StateLockManager.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/StateLockManager.java

## Purpose
`StateLockManager` coordinates shared state-changing RPCs with exclusive operations such as metadata backups.

## Important APIs, Types, And Functions
`lockShared` acquires an interruptible read lock and tracks waiters/holders by thread. `lockExclusive` performs a configurable grace cycle, optionally activates an interrupt cycle, then acquires the write lock or times out. `mastersStartedCallback` opens an exclusive-only maintenance window after state load. Accessors expose shared holders and interrupt-cycle state.

## Control Flow, State, Dependencies, Risks, And Tests
Shared callers are blocked during exclusive-only startup and can be interrupted while backup forces the write lock. Exclusive callers use `StateLockOptions`, optional `beforeAttempt`, configured forced duration, and a scheduler that interrupts registered shared threads. State is in-memory synchronization state; persistence is protected by ensuring journals and checkpoints see quiescent master state. Dependencies include `ReentrantReadWriteLock`, config keys, `ConcurrentHashSet`, `RetryUtils`, and `LockResource`. Risks include holder tracking cleanup bugs, interrupting active shared state operations, scheduler lifetime leaks, recursion warning noise, and fair-lock contention. Tests should cover grace timeout/forced modes, interrupt cycle ref-counting, exclusive-only window, shared lock cleanup, before-attempt failures, and high recursion logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/StateLockManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/StateLockOptions.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/StateLockOptions.java

## Purpose
`StateLockOptions` carries the timing and mode parameters for exclusive state-lock acquisition.

## Important APIs, Types, And Functions
It stores `GraceMode`, grace try duration, sleep duration, and total timeout. Factory methods provide defaults for shell backups, daily backups, and immediate forced locking by reading configuration keys.

## Control Flow, State, Dependencies, Risks, And Tests
The options are immutable after construction and have no persistence. `StateLockManager` consumes them to decide whether to timeout or force after the grace cycle. Dependencies are `Configuration`, `PropertyKey`, Java lock documentation, and the `GraceMode` enum. Risks include zero-duration defaults changing lock behavior dramatically, misconfigured durations causing long backup stalls, and no local validation of negative values. Tests should validate config-driven factories, forced default behavior, and manager integration for timeout versus forced modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/StateLockOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/audit/AsyncUserAccessAuditLogWriter.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/audit/AsyncUserAccessAuditLogWriter.java

## Purpose
`AsyncUserAccessAuditLogWriter` asynchronously writes user access audit events to a configured logger.

## Important APIs, Types, And Functions
The constructor creates a bounded `LinkedBlockingQueue` from `MASTER_AUDIT_LOGGING_QUEUE_CAPACITY`. `start` creates the worker thread, `stop` interrupts and joins it, `append` blocks to enqueue an `AuditContext`, and `getAuditLogEntriesSize` exposes queue depth.

## Control Flow, State, Dependencies, Risks, And Tests
The worker loops while not stopped, takes audit contexts, and logs `toString()` at info level. State is in-memory queue and worker thread; persistence is delegated to the logging backend. Dependencies include SLF4J, `Configuration`, and `AuditContext`. Risks include append blocking under full queues, stop dropping queued entries because interruption exits immediately, appends accepted while stopped, and logging failures not handled. Tests should cover start/stop idempotency, queue capacity blocking/interrupt behavior, drain behavior on stop, and logger output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/audit/AsyncUserAccessAuditLogWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/audit/AuditContext.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/audit/AuditContext.java

## Purpose
`AuditContext` is the lifecycle contract for audit-log event state.

## Important APIs, Types, And Functions
It extends `Closeable` and requires fluent `setAllowed`, `setSucceeded`, and `close`.

## Control Flow, State, Dependencies, Risks, And Tests
Implementations collect per-operation audit state, update authorization and success flags, then usually emit or enqueue on close. The interface has no direct persistence; log persistence depends on writer implementations and logging configuration. Dependencies are only Java `Closeable`. Risks include close being called before success/allowed flags are finalized, fluent setters hiding mutable state, and callers forgetting try-with-resources. Tests should target concrete contexts for string formatting, close idempotency, failure paths, and integration with async audit writer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/audit/AuditContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/AbstractCatchupThread.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/AbstractCatchupThread.java

## Purpose
`AbstractCatchupThread` standardizes journal catch-up thread execution, cancellation, and fatal failure handling.

## Important APIs, Types, And Functions
It extends `AutopsyThread`. `run` delegates to `runCatchup`, stores errors, and calls `ProcessUtils.fatalError` on failure. Subclasses implement `cancel` and `runCatchup`. `waitTermination` joins indefinitely and rethrows stored crash errors through fatal handling.

## Control Flow, State, Dependencies, Risks, And Tests
Catch-up state is thread-local runtime progress managed by subclasses; no persistence is defined here. Dependencies are `AutopsyThread` and `ProcessUtils`. Risks include process fatal exits from background failures, indefinite join waits, and cancellation semantics being entirely subclass-defined. Tests should use a concrete test subclass for normal completion, cancel propagation, failure recording, and `waitTermination` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/AbstractCatchupThread.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/AbstractJournalProgressLogger.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/AbstractJournalProgressLogger.java

## Purpose
`AbstractJournalProgressLogger` rate-limits progress logging during journal replay or catch-up.

## Important APIs, Types, And Functions
Subclasses provide `getLastAppliedIndex` and `getJournalName`. `logProgress` uses exponential backoff capped by `MAX_LOG_INTERVAL_MS`, computes entries read since the last measurement, and optionally estimates remaining entries/time from an end commit index.

## Control Flow, State, Dependencies, Risks, And Tests
The logger stores last measurement time, last commit index, and log count in memory only. Dependencies are SLF4J and `OptionalLong`. Risks include initial `mLastCommitIdx` set to zero for journals with nonzero starting indices, division by zero avoidance relying on finite checks, and non-thread-safe mutable counters. Tests should control time or subclass behavior to verify rate limiting, estimate formatting, absent end index, and backoff cap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/AbstractJournalProgressLogger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/AbstractJournalSystem.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/AbstractJournalSystem.java

## Purpose
`AbstractJournalSystem` provides lifecycle and journal-sink management for concrete journal systems.

## Important APIs, Types, And Functions
`start`/`stop` guard running state and call `startInternal`/`stopInternal`. Sink APIs add, remove, and retrieve `JournalSink`s per master or globally under a read/write lock. `registerMetrics` registers per-master sequence-number gauges.

## Control Flow, State, Dependencies, Risks, And Tests
The class tracks runtime running state and sink associations; persistence is owned by concrete UFS or Raft systems. On stop, all sinks receive `beforeShutdown` before `stopInternal`. Dependencies include `JournalSystem`, `Master`, `JournalSink`, `MetricsSystem`, and concurrent collections. Risks include returning mutable sink sets, sink callbacks under lifecycle transitions, metrics lambdas repeatedly calling `getCurrentSequenceNumbers`, and `stop` requiring running state. Tests should cover lifecycle preconditions, sink add/remove sharing, global sink recomputation, and metric registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/AbstractJournalSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/AsyncJournalWriter.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/AsyncJournalWriter.java

## Purpose
`AsyncJournalWriter` decouples journal entry appends from durable flushes and batches writes on a dedicated thread.

## Important APIs, Types, And Functions
`appendEntry` enqueues an entry and returns a counter. `flush(targetCounter)` registers a `FlushTicket`, releases the flush thread semaphore, and blocks with ForkJoin managed blocking until the target counter is durable or failed. `close`/`stop` terminate the flush thread. `FlushTicket` wraps `SettableFuture` and error propagation.

## Control Flow, State, Dependencies, Risks, And Tests
The flush thread waits for queued entries or a timeout, writes entries through `JournalWriter`, appends to sinks, flushes the writer and sinks, updates counters, and completes tickets. State includes lock-free queue, counters, ticket set, semaphore, stop flag, and thread. Persistence is through the underlying `JournalWriter`. Dependencies include Alluxio `ForkJoinPoolHelper`, `JournalSink`, metrics, `JournalClosedException`, Ratis `NotLeaderException` pass-through via callers, and config batch timing. Risks include unbounded queue growth, constructor overload setting journal name after thread creation, stop not guaranteeing pending durability, ticket failure after IO errors, and sink side effects coupled to writer success. Tests should cover append/flush ordering, batching, IO failure ticket propagation, close semantics, concurrent flushes, sink append/flush calls, and interruption mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/AsyncJournalWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/CatchupFuture.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/CatchupFuture.java

## Purpose
`CatchupFuture` aggregates one or more journal catch-up threads for cancellation and termination waiting.

## Important APIs, Types, And Functions
`allOf` combines threads from multiple futures. `completed` creates an empty future. Constructors wrap one or more `AbstractCatchupThread`s. `cancel` forwards to each thread; `waitTermination` waits on each.

## Control Flow, State, Dependencies, Risks, And Tests
The state is a list of live or completed catch-up threads, with no persistence. Dependencies are `AbstractCatchupThread` and collection utilities. Risks include serial waiting where one hung thread blocks observation of later failures, duplicate threads if futures overlap, and cancellation ordering not waiting. Tests should cover empty futures, aggregation, cancel forwarding, wait forwarding, and duplicate/failed thread behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/CatchupFuture.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/DelegatingJournaled.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/DelegatingJournaled.java

## Purpose
`DelegatingJournaled` is a mixin for classes that expose `Journaled` behavior through another component.

## Important APIs, Types, And Functions
Default methods forward journal processing, reset, apply-and-journal, checkpoint naming, checkpoint write/restore, and journal-entry iteration to `getDelegate`.

## Control Flow, State, Dependencies, Risks, And Tests
The delegate owns all state and persistence. This interface removes boilerplate for wrappers but makes correctness depend on stable delegation. Dependencies include `Journaled`, checkpoint classes, `CloseableIterator`, and async checkpoint APIs. Risks include `getDelegate` returning null, changing delegates mid-operation, or losing wrapper-specific state from checkpoints. Tests should verify each default forwards exactly once and that wrappers document whether delegate identity is stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/DelegatingJournaled.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/FileSystemMergeJournalContext.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/FileSystemMergeJournalContext.java

## Purpose
`FileSystemMergeJournalContext` buffers and merges file-system journal entries before passing them to an underlying journal context.

## Important APIs, Types, And Functions
It wraps a `JournalContext` and `JournalEntryMerger`. `append` adds entries to the merger and force-appends merged journals if the buffered merged list reaches a configured warning threshold. `flush` appends merged journals and synchronously flushes the underlying context. `close` appends merged journals then closes the underlying context.

## Control Flow, State, Dependencies, Risks, And Tests
The context is synchronized to support metadata-sync workers sharing a context. Buffered entries are not persisted until `appendMergedJournals` runs; forced merging may expose intermediate standby state, as the comments note. Dependencies include `JournalEntryMerger`, configuration thresholds, and `JournalContext`. Risks include memory growth below threshold, merge correctness, forced flush weakening atomicity, and close/flush exception handling. Tests should cover merge append order, empty flush no-op, threshold behavior, close forwarding, thread safety, and merger clear semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/FileSystemMergeJournalContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/Journal.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/Journal.java

## Purpose
`Journal` is the per-master persistence handle for appending journal entries.

## Important APIs, Types, And Functions
It extends `Closeable`, exposes `getLocation`, and creates `JournalContext`s with `createJournalContext`.

## Control Flow, State, Dependencies, Risks, And Tests
Concrete implementations enforce whether writes are allowed based on journal system mode and whether the journal is closed. Persistent state is the backend log at the returned URI. Dependencies are `JournalContext`, `UnavailableException`, and `URI`. Risks include contexts outliving closed journals, unclear location semantics for embedded journals, and caller misuse outside primary mode. Tests should target concrete journal implementations for context creation, close behavior, location values, and unavailable error mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/Journal.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalContext.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalContext.java

## Purpose
`JournalContext` is the scoped API for appending and flushing journal entries during a state change.

## Important APIs, Types, And Functions
It extends `Closeable` and `Supplier<JournalContext>`, declares `append`, `flush`, and `close`, and returns itself from the default `get`.

## Control Flow, State, Dependencies, Risks, And Tests
Implementations may synchronously commit entries, buffer merged entries, or only enqueue to an async writer. Persistent behavior depends on the implementation, but callers should use try-with-resources so `close` can flush. Dependencies include `JournalEntry` and `UnavailableException`. Risks include append without close/flush, differing durability semantics across implementations, and supplier use hiding context reuse. Tests should check concrete contexts for close durability, exception propagation, multiple flush behavior, and supplier compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalEntryAssociation.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalEntryAssociation.java

## Purpose
`JournalEntryAssociation` maps a polymorphic journal entry protobuf to the master service responsible for applying it.

## Important APIs, Types, And Functions
`getMasterForEntry` checks `has*` fields on `JournalEntry` and returns file system, block, meta, or table master constants.

## Control Flow, State, Dependencies, Risks, And Tests
The method is a deterministic classifier with no state or persistence. It is used by backup restore and any replay path needing to route entries. Dependencies are `Constants` and generated journal protobuf accessors. Risks are new journal entry types not being added, ambiguous entries with multiple fields being classified by first matching group, and restore fatal failures on unknown entries. Tests should cover every journal entry variant, unknown/default entry rejection, and ordering if multi-field entries can be constructed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalEntryAssociation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalEntryIterable.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalEntryIterable.java

## Purpose
`JournalEntryIterable` exposes a closeable iterator over all journal entries representing a component's state.

## Important APIs, Types, And Functions
It declares `getJournalEntryIterator`, returning `CloseableIterator<Journal.JournalEntry>`.

## Control Flow, State, Dependencies, Risks, And Tests
Implementations stream in-memory state as journal entries for backups and checkpoint construction. There is no direct persistence, but the iterator feeds persisted journal-entry checkpoints and backups. Dependencies are generated journal protobufs and `CloseableIterator`. Risks include iterators not closing resources, snapshot consistency while state mutates, and ordering requirements for replay. Tests should verify full state coverage, iterator close behavior, deterministic ordering, and integration with `JournalUtils.writeJournalEntryCheckpoint`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalEntryIterable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalEntryMerger.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalEntryMerger.java

## Purpose
`JournalEntryMerger` defines the strategy interface for merging related journal entries, especially inode updates.

## Important APIs, Types, And Functions
It declares `add`, `getMergedJournalEntries`, and `clear`.

## Control Flow, State, Dependencies, Risks, And Tests
Implementations hold mutable buffered entries and produce a semantically equivalent reduced list for persistence. Dependencies are generated `Journal.JournalEntry`. Risks include non-idempotent `getMergedJournalEntries`, lost updates, ordering changes, and thread safety when used from `FileSystemMergeJournalContext`. Tests should cover merge associativity for expected entry combinations, clear behavior, duplicate updates, unrelated entries, and concurrent access if shared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalEntryMerger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalEntryRepresentable.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalEntryRepresentable.java

## Purpose
`JournalEntryRepresentable` marks objects that can serialize themselves to a `JournalEntry`.

## Important APIs, Types, And Functions
It declares `toJournalEntry`.

## Control Flow, State, Dependencies, Risks, And Tests
The implementing object owns state; this interface defines conversion into the persisted journal protobuf representation. Dependency is `JournalEntry`. Risks include incomplete serialization, unstable field choices, and mismatch with `JournalEntryAssociation` or replay handlers. Tests should assert round-trip conversion for each implementation, compatibility with replay, and stable protobuf fields across upgrades.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalEntryRepresentable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalEntryStreamReader.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalEntryStreamReader.java

## Purpose
`JournalEntryStreamReader` reads delimited `JournalEntry` protobufs from an input stream.

## Important APIs, Types, And Functions
`readEntry` reads the first byte, decodes a protobuf varint size through `ProtoUtils.readRawVarint32`, expands an internal buffer when needed, reads the payload, and parses a `JournalEntry`. `close` closes the underlying stream.

## Control Flow, State, Dependencies, Risks, And Tests
EOF before a first byte returns null. Truncated size throws; truncated payload logs a warning and returns null because the final unacked entry can be ignored after a crash. State is the reusable byte buffer. Persistence is the delimited protobuf stream consumed by journals and backups. Dependencies include `ProtoUtils` and generated protobuf parser. Risks include large entry memory allocation, treating any truncated payload as benign, and close ownership. Tests should cover empty streams, valid multi-entry reads, buffer growth, truncated size/payload, malformed protobufs, and close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalEntryStreamReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalFileParser.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalFileParser.java

## Purpose
`JournalFileParser` is the closeable parser abstraction for journal log files.

## Important APIs, Types, And Functions
The nested `Factory.create(URI)` returns a `UfsJournalFileParser`. `next` reads the next journal entry or null when exhausted.

## Control Flow, State, Dependencies, Risks, And Tests
The parser is not thread-safe and delegates storage-specific parsing to UFS journal code. It is used by `JournalUpgrader` to inspect v0 completed logs and compute sequence ranges. Persistent state is the journal file at the URI. Dependencies include `UfsJournalFileParser`, URI handling, and journal protobufs. Risks include factory being hard-coded to UFS, parser close requirements, and sequence-range computation depending on valid entries. Tests should cover factory creation, next/EOF behavior in the UFS parser, close handling, and malformed file handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalFileParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalReader.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalReader.java

## Purpose
`JournalReader` defines sequential reading over checkpoint and log elements in a journal.

## Important APIs, Types, And Functions
It declares `advance`, `getEntry`, `getCheckpoint`, `getNextSequenceNumber`, and `close`. `State` distinguishes `CHECKPOINT`, `LOG`, and `DONE`.

## Control Flow, State, Dependencies, Risks, And Tests
Consumers call `advance`, then read either the current checkpoint stream or log entry; repeated getters return the same current item until the next advance. Persistence is the journal backend's checkpoint and log data. Dependencies are `CheckpointInputStream`, `JournalEntry`, and closeable resources. Risks include misuse of getters before or after the right state, checkpoint stream ownership, and next sequence semantics after close. Tests should cover state transitions, repeated getters, sequence tracking, checkpoint/log ordering, and close behavior in concrete readers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalSystem.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalSystem.java

## Purpose
`JournalSystem` is the top-level abstraction for creating, applying, formatting, checkpointing, and switching master journals between standby and primary modes.

## Important APIs, Types, And Functions
Core APIs include `createJournal`, `start`, `stop`, `gainPrimacy`, `losePrimacy`, `suspend`, `resume`, `catchup`, `getCurrentSequenceNumbers`, `format`, `isFormatted`, `isEmpty`, `checkpoint`, sink management, and optional journal gRPC services. `Builder` selects `NoopJournalSystem`, `UfsJournalSystem`, or `RaftJournalSystem` from configuration and process type.

## Control Flow, State, Dependencies, Risks, And Tests
The documented flow starts journals in standby, catches up/replays state, then gains primacy to accept writes; losing primacy resets and rebuilds state from the log. `suspend`/`resume` support backup and catch-up operations. Persistent state is journal logs and checkpoints in UFS or embedded Raft storage. Dependencies include configuration, master services, journal sinks, state lock manager, Raft/UFS systems, and network service types. Risks include mode-transition race conditions, creating journals after start, checkpointing without effective state lock, wrong process type selecting the wrong Raft service, and corruption tolerance behavior in implementations. Tests should cover builder selection, mode transitions, catch-up, suspend callbacks, formatting, checkpointing, sink propagation, and empty-state detection for each backend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalUpgrader.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalUpgrader.java

## Purpose
`JournalUpgrader` is a CLI tool for upgrading UFS journals from Alluxio v0 layout to v1 layout.

## Important APIs, Types, And Functions
`main` parses `-help` and `-journalDirectoryV0`, discovers master names, and runs an `Upgrader` per master. `Upgrader.prepare` recovers/completes v0 logs, formats v1 if needed, and creates checkpoint/log directories. `upgrade` renames the v0 checkpoint and completed logs into v1 sequence-range names after scanning each completed log with `JournalFileParser`.

## Control Flow, State, Dependencies, Risks, And Tests
The upgrade mutates persistent UFS paths: `checkpoint.data`, v0 `completed/log.N`, v1 `checkpoints/0x0-0x...`, and v1 `logs/0xstart-0xend`. Dependencies include v0 `MutableJournal`, v1 `UfsJournal`, `UnderFileSystem`, `ServiceUtils`, CLI parser, and URI utilities. Risks include destructive renames without rollback, assumptions about v0/v1 directories sharing storage, missing logs after checkpoint rename, scanning entire logs to compute ranges, and service-loader master names not matching old journal folders. Tests should use a fake UFS to cover no-checkpoint no-op, checkpoint-only upgrade, multi-log ranges, rename failure, argument parsing, and idempotent reruns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalUpgrader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalUtils.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalUtils.java

## Purpose
`JournalUtils` holds common journal URI, checkpoint, replay, and sink helper logic.

## Important APIs, Types, And Functions
`getJournalLocation` normalizes `MASTER_JOURNAL_FOLDER` to a trailing-slash URI. `writeJournalEntryCheckpoint` writes delimited entries under a `JOURNAL_ENTRY` checkpoint header. `restoreJournalEntryCheckpoint` resets state and replays entries. `writeToCheckpoint` writes compound Kryo chunked checkpoints. `restoreFromCheckpoint` dispatches compound entries by `CheckpointName`. `handleJournalReplayFailure`, `sinkAppend`, and `sinkFlush` centralize error and sink behavior.

## Control Flow, State, Dependencies, Risks, And Tests
Checkpoint helpers define persistent binary formats used by journal checkpoints. Restore tolerates or fatal-errors on replay failures based on `MASTER_JOURNAL_TOLERATE_CORRUPTION`. Dependencies include checkpoint streams/types, Kryo `OutputChunked`, `PatchedInputChunked` readers, protobuf entries, `Checkpointed`, and sinks. Risks include component name mismatches in compound checkpoints, unknown checkpoint entries aborting restore, interruption handling during writes, and corruption tolerance hiding bad state. Tests should cover journal-entry checkpoint round trips, compound checkpoint dispatch, unknown names, replay failure tolerance, sink calls, and URI normalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalWriter.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalWriter.java

## Purpose
`JournalWriter` is the low-level interface for writing and flushing journal entries.

## Important APIs, Types, And Functions
It extends `Closeable`, declares `write(JournalEntry)` and `flush`, both able to throw `IOException` or `JournalClosedException`.

## Control Flow, State, Dependencies, Risks, And Tests
`AsyncJournalWriter` calls `write` for each queued entry and `flush` to make entries durable. Persistent state is owned by concrete writer backends. Dependencies are generated journal protobufs and `JournalClosedException`. Risks include callers assuming `write` is durable without `flush`, close/flush races, and backend-specific error mapping. Tests should target concrete writers for sequence numbering, durability after flush, closed behavior, partial write recovery, and idempotent close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/Journaled.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/Journaled.java

## Purpose
`Journaled` defines the contract for components whose state can be replayed from journal entries and checkpointed.

## Important APIs, Types, And Functions
Implementations provide `processJournalEntry` and `resetState`. Default `applyAndJournal` mutates state then appends the entry. Default checkpoint methods write and restore journal-entry checkpoints via `JournalUtils`.

## Control Flow, State, Dependencies, Risks, And Tests
The intended mutation path is process in memory first, then append to the provided journal context. Persistent state is journal entries and checkpoints generated from `getJournalEntryIterator`. Dependencies include `Checkpointed`, `JournalEntryIterable`, and `JournalContext`. Risks include mutating memory before append failure, unsupported entries returning false but callers ignoring it, and checkpoint iterators not representing all state. Tests should cover replay idempotence, apply-and-journal ordering, append failure effects, reset behavior, and checkpoint round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/Journaled.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournaledGroup.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournaledGroup.java

## Purpose
`JournaledGroup` treats multiple `Journaled` components as one checkpointed/replayable component.

## Important APIs, Types, And Functions
It stores component list and group `CheckpointName`. `processJournalEntry` offers entries to components in order until one accepts. `resetState` resets components in reverse order. Checkpoint write/restore either runs component file checkpoint futures or uses compound checkpoint streams. Journal iterators are concatenated.

## Control Flow, State, Dependencies, Risks, And Tests
Persistence is a compound checkpoint or concatenated journal-entry stream representing all child components. Dependencies include `JournalUtils`, `CloseableIterator.concat`, Guava `Lists.reverse`, and checkpoint APIs. Risks include entries accepted by the wrong first component, component order being part of replay semantics, partial async checkpoint failures, and unknown compound checkpoint entries. Tests should cover ordering, reverse reset, checkpoint round trips, async future aggregation, iterator close behavior, and duplicate entry handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournaledGroup.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/MasterJournalContext.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/MasterJournalContext.java

## Purpose
`MasterJournalContext` is the standard durable journal context for master state changes.

## Important APIs, Types, And Functions
`append` enqueues entries through `AsyncJournalWriter` and records the returned flush counter. `flush` and `close` call `waitForJournalFlush`, which retries until the configured timeout, maps closed/not-leader conditions to `UnavailableException`, logs retryable failures, and fatal-errors on unexpected or exhausted failures.

## Control Flow, State, Dependencies, Risks, And Tests
State is the last flush counter for this context. Persistence occurs when the async writer flushes through its backend. Dependencies include `AsyncJournalWriter`, `TimeoutRetry`, `ProcessUtils`, Ratis `NotLeaderException`, and journal flush configuration. Risks include only tracking the last append counter, fatal process exits after timeout, memory mutation preceding journal durability, and cancellation being logged but not cancelling partial writes. Tests should cover no-op flush, append/close durability, retry loops, not-leader mapping, timeout fatal path, and concurrent append synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/MasterJournalContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/MergeJournalContext.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/MergeJournalContext.java

## Purpose
`MergeJournalContext` buffers journal entries for a specific file operation so partial inode updates can be merged before persistence.

## Important APIs, Types, And Functions
It wraps a `JournalContext`, target `AlluxioURI`, and merge operator. `append` buffers `InodeFile`, `UpdateInode`, and `UpdateInodeFile` entries for the target path/file id and passes all others through. `flush` applies the merge operator, appends merged entries, and clears the buffer; `close` flushes without closing the underlying context.

## Control Flow, State, Dependencies, Risks, And Tests
Buffered entries are not persisted until flush/close, while pass-through entries persist through the underlying context. Dependencies include `AlluxioURI`, generated journal entry fields, and merge operator behavior. Risks include non-thread-safe use, target file id only learned after the inode file entry, underlying context not being closed, >100 entries only debug-logged, and merge operator correctness. Tests should cover target matching, non-target pass-through, update after file-id capture, close semantics, empty merge behavior, and crash before flush.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/MergeJournalContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/MetadataSyncMergeJournalContext.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/MetadataSyncMergeJournalContext.java

## Purpose
`MetadataSyncMergeJournalContext` adapts filesystem merge journaling for metadata sync by avoiding synchronous flushes on normal flush/close.

## Important APIs, Types, And Functions
It extends `FileSystemMergeJournalContext`. `flush` and `close` only append merged entries to the underlying context and do not close or synchronously flush it. `hardFlush` appends and then flushes the underlying context. `getMerger` exposes the merger for tests.

## Control Flow, State, Dependencies, Risks, And Tests
Metadata sync worker threads use separate instances while an RPC thread owns the underlying context. Persistence is delayed until the underlying context is eventually flushed/closed or `hardFlush` is called. Dependencies are merge context base class and `JournalEntryMerger`. Risks include data loss if caller assumes close is durable, under-documented ownership of underlying context, and delayed standby visibility. Tests should cover async flush semantics, hardFlush durability, no underlying close on close, merger exposure, and metadata-sync multi-thread expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/MetadataSyncMergeJournalContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/NoopJournalContext.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/NoopJournalContext.java

## Purpose
`NoopJournalContext` is a singleton journal context that discards all entries.

## Important APIs, Types, And Functions
`INSTANCE` is the singleton. `append`, `flush`, and `close` are no-ops.

## Control Flow, State, Dependencies, Risks, And Tests
There is no state or persistence. It is used by noop journal implementations and test paths. Dependency is the `JournalContext` interface. Risks include accidentally using it in production paths and silently losing journal entries. Tests should assert singleton behavior, no exceptions on repeated close/flush, and that noop journal systems are only selected under explicit NOOP/test configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/NoopJournalContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/NoopJournaled.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/NoopJournaled.java

## Purpose
`NoopJournaled` supplies default no-op implementations for journaled components.

## Important APIs, Types, And Functions
It accepts all journal entries, resets nothing, reports checkpoint name `NOOP`, writes an empty `JOURNAL_ENTRY` checkpoint header, restores no state, and returns an empty closeable iterator.

## Control Flow, State, Dependencies, Risks, And Tests
No state is persisted beyond an empty checkpoint type marker. Dependencies include checkpoint streams/types and `CloseableIterator`. Risks include `processJournalEntry` returning true for every entry, which can mask routing errors if used in a group, and empty checkpoints being mistaken for valid state. Tests should cover empty checkpoint header, empty iterator, default restore, and interactions with `JournaledGroup` ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/NoopJournaled.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/PatchedInputChunked.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/PatchedInputChunked.java

## Purpose
`PatchedInputChunked` works around Kryo EOF handling for compound checkpoint reads.

## Important APIs, Types, And Functions
It extends Kryo `InputChunked` and overrides `fill` to translate a `KryoException` with message `Buffer underflow.` into `-1`, while rethrowing other exceptions.

## Control Flow, State, Dependencies, Risks, And Tests
The class has no additional state or persistence; it affects how Kryo chunked streams signal EOF while reading persisted compound checkpoints. Dependencies are Kryo `InputChunked` and `KryoException`. Risks include matching on exception message text, future Kryo behavior changes, and hiding real truncation as EOF if the same message is reused. Tests should read valid compound checkpoints to EOF, feed truncated chunks, and verify non-underflow Kryo exceptions still propagate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/PatchedInputChunked.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/SingleEntryJournaled.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/SingleEntryJournaled.java

## Purpose
`SingleEntryJournaled` is a base class for components represented by exactly one journal entry.

## Important APIs, Types, And Functions
It stores a single `JournalEntry`, returns it through a one-element closeable iterator, accepts any entry in `processJournalEntry` while warning if one was already processed, resets to the default entry, and exposes `getEntry` with a warning if unset.

## Control Flow, State, Dependencies, Risks, And Tests
The single entry is in-memory state and can be persisted through the default `Journaled` checkpoint path. Dependencies include journal protobufs, `CloseableIterator`, and `CommonUtils.singleElementIterator`. Risks include accepting wrong entry types unless subclasses override, warning-only duplicate detection, and returning a default entry when unset. Tests should cover reset, duplicate processing, iterator content, unset get warning behavior, and subclass checkpoint names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/SingleEntryJournaled.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/StateChangeJournalContext.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/StateChangeJournalContext.java

## Purpose
`StateChangeJournalContext` ties a journal context lifetime to a held shared state lock.

## Important APIs, Types, And Functions
It wraps `JournalContext` and `LockResource`. `append` and `flush` delegate. `close` closes the journal context, then releases the state lock in a finally block.

## Control Flow, State, Dependencies, Risks, And Tests
The wrapper ensures state-changing RPCs keep the shared lock until their journal context has closed and flushed. It has no persistence beyond delegated journal behavior. Dependencies are `LockResource`, `JournalContext`, and `Preconditions`. Risks include non-thread-safe use, caller failing to close, and underlying close hanging while holding shared lock. Tests should cover close ordering, lock release on close exception, delegate append/flush, and interaction with `AbstractMaster.createJournalContext`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/StateChangeJournalContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/CheckpointFormat.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/CheckpointFormat.java

## Purpose
`CheckpointFormat` defines the parsing and human-readable rendering contract for checkpoint binary formats.

## Important APIs, Types, And Functions
Implementations provide `createReader(CheckpointInputStream)` and `parseToHumanReadable`. The nested marker interface `CheckpointReader` identifies non-thread-safe reader types.

## Control Flow, State, Dependencies, Risks, And Tests
`CheckpointType` maps type ids to concrete format implementations. This interface has no state or persistence by itself, but defines how persisted checkpoint bytes are interpreted. Dependencies are `CheckpointInputStream`, `PrintStream`, and IO exceptions. Risks include format readers not validating input type, unavailable human-readable rendering for binary formats, and reader lifetime tied to input stream ownership. Tests should verify every `CheckpointType` format creates the correct reader and handles parse output/failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/CheckpointFormat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/CheckpointInputStream.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/CheckpointInputStream.java

## Purpose
`CheckpointInputStream` reads the checkpoint type header before exposing checkpoint payload bytes.

## Important APIs, Types, And Functions
The constructor extends `DataInputStream`, reads a leading long, converts it through `CheckpointType.fromLong`, and stores the type. `getType` returns the parsed checkpoint type.

## Control Flow, State, Dependencies, Risks, And Tests
Every checkpoint payload begins after the type id. EOF while reading the id is treated as an old/invalid checkpoint and throws an `IllegalStateException` with upgrade guidance. Dependencies include `RuntimeConstants`, `CheckpointType`, and Java data streams. Risks include consuming the header irreversibly, unknown ids failing hard, and old Alluxio 1.x checkpoints requiring explicit upgrade. Tests should cover valid types, EOF, unknown ids, and wrapping behavior with compressed/digest streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/CheckpointInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/CheckpointName.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/CheckpointName.java

## Purpose
`CheckpointName` enumerates stable names for checkpointed master components.

## Important APIs, Types, And Functions
The enum values cover file system, block, meta, table, inode stores, mount table, path properties, scheduler, snapshot id, and noop components.

## Control Flow, State, Dependencies, Risks, And Tests
Names are persisted in compound checkpoints as strings and in per-component checkpoint file names. The file comment states names should never change to preserve backward compatibility. There are no external dependencies. Risks include renaming/removing enum constants breaking old checkpoints, adding duplicate conceptual names, and `valueOf` failures in compound readers for unknown future names. Tests should cover old checkpoint compatibility, file-name usage, and new component additions requiring enum updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/CheckpointName.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/CheckpointOutputStream.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/CheckpointOutputStream.java

## Purpose
`CheckpointOutputStream` writes the checkpoint type header for a new checkpoint stream.

## Important APIs, Types, And Functions
The constructor extends `DataOutputStream` and writes `type.getId()` as the first long.

## Control Flow, State, Dependencies, Risks, And Tests
After construction, callers write format-specific payload bytes. Persistent state is the leading type id in every checkpoint. Dependencies are `CheckpointType` and Java data streams. Risks include callers wrapping streams in the wrong order, not flushing the header, or writing a payload that does not match the declared type. Tests should verify header round trips with `CheckpointInputStream`, all checkpoint types, and behavior on underlying IO failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/CheckpointOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/CheckpointType.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/CheckpointType.java

## Purpose
`CheckpointType` assigns stable numeric ids to supported checkpoint encodings and their parser formats.

## Important APIs, Types, And Functions
Types include `JOURNAL_ENTRY`, `COMPOUND`, `LONGS`, `ROCKS_SINGLE`, `INODE_PROTOS`, `LONG`, and `ROCKS_PARALLEL`. Each stores an id and `CheckpointFormat`. `fromLong` maps persisted ids back to enum values with upgrade guidance on failure.

## Control Flow, State, Dependencies, Risks, And Tests
The id is persisted as a leading long by `CheckpointOutputStream`; readers use it to select parser behavior. Dependencies include concrete format classes and `RuntimeConstants`. Risks include changing ids or meanings, unknown ids from future versions failing hard, and binary formats lacking human-readable parsing. Tests should assert stable ids, `fromLong` mapping, unknown-id errors, and format instance compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/CheckpointType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/Checkpointed.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/Checkpointed.java

## Purpose
`Checkpointed` is the base interface for master components that can write and restore metadata snapshots.

## Important APIs, Types, And Functions
Implementations provide `getCheckpointName`, stream `writeToCheckpoint`, and stream `restoreFromCheckpoint`. Default file-based methods run asynchronously, wrap output/input in optimized LZ4 plus MD5 streams, save or verify `.md5` files, and convert failures to `AlluxioRuntimeException`.

## Control Flow, State, Dependencies, Risks, And Tests
File checkpoint writes compute MD5 while writing compressed data, then persist the MD5 sidecar. Restore recomputes and verifies after loading. Persistent state is a file named by `CheckpointName` plus saved MD5. Dependencies include Ratis `MD5Hash`/`MD5FileUtil`, `OptimizedCheckpoint*Stream`, futures, and executor services. Risks include async exceptions hidden in futures, partial files on failure, MD5 sidecar mismatch, directory permissions, and interruption handling left to implementations. Tests should cover successful async write/restore, checksum mismatch, implementation exceptions, executor behavior, and file naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/Checkpointed.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/CompoundCheckpointFormat.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/CompoundCheckpointFormat.java

## Purpose
`CompoundCheckpointFormat` stores multiple named component checkpoints inside one checkpoint stream using Kryo chunked encoding.

## Important APIs, Types, And Functions
`createReader` returns `CompoundCheckpointReader`. `parseToHumanReadable` iterates entries and delegates each nested stream to its own `CheckpointFormat`. The reader uses `PatchedInputChunked`, reads a `CheckpointName` string, then wraps the same stream in a nested `CheckpointInputStream`.

## Control Flow, State, Dependencies, Risks, And Tests
The persisted format is `[componentName, checkpointTypeAndBytes]` per Kryo chunk. `nextCheckpoint` skips chunks after the first and returns entries valid only until the next call. Dependencies include Kryo chunked streams, `CheckpointName.valueOf`, nested checkpoint streams, and `PatchedInputChunked`. Risks include unknown names failing restore, callers closing nested streams, chunk boundary corruption, and future format compatibility. Tests should cover multi-component round trips, human-readable delegation, EOF handling, unknown names, truncated chunks, and entry validity across iterations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/CompoundCheckpointFormat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/InodeProtosCheckpointFormat.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/InodeProtosCheckpointFormat.java

## Purpose
`InodeProtosCheckpointFormat` reads and renders checkpoints made of delimited `InodeMeta.Inode` protobufs.

## Important APIs, Types, And Functions
`createReader` returns an `InodeProtosCheckpointReader` that validates type `INODE_PROTOS`. `read` returns an optional parsed delimited inode. `parseToHumanReadable` prints separators and each inode protobuf text.

## Control Flow, State, Dependencies, Risks, And Tests
The persisted format is a checkpoint type header followed by repeated delimited inode protos. Dependencies include generated `InodeMeta`, Guava `Preconditions`, and `Strings`. Risks include malformed or partially written protobufs, large text output, and type mismatches. Tests should cover empty checkpoints, multiple inode reads, human-readable output, wrong type rejection, and truncated proto handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/InodeProtosCheckpointFormat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/JournalCheckpointFormat.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/JournalCheckpointFormat.java

## Purpose
`JournalCheckpointFormat` reads and renders checkpoints made of delimited master `JournalEntry` protobufs.

## Important APIs, Types, And Functions
`createReader` returns a `JournalCheckpointReader` that validates type `JOURNAL_ENTRY`. `nextEntry` delegates to `JournalEntryStreamReader`. `parseToHumanReadable` prints separators and protobuf text for each entry.

## Control Flow, State, Dependencies, Risks, And Tests
The persisted format is a checkpoint type header followed by repeated delimited journal entries. Dependencies include `JournalEntryStreamReader`, generated journal protobufs, and Guava preconditions. Risks include `JournalEntryStreamReader` treating truncated final payload as EOF, wrong type rejection, and large human-readable output. Tests should cover round trips, empty checkpoints, wrong type, truncated entries, and parse output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/JournalCheckpointFormat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/LongCheckpointFormat.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/LongCheckpointFormat.java

## Purpose
`LongCheckpointFormat` reads and renders checkpoints containing a single long.

## Important APIs, Types, And Functions
`createReader` returns `LongCheckpointReader`, which validates type `LONG`. `getLong` reads the long from the checkpoint stream. `parseToHumanReadable` prints the value.

## Control Flow, State, Dependencies, Risks, And Tests
The persisted format is a type header followed by one Java data-stream long. Dependencies are `CheckpointInputStream` and Guava `Preconditions`. Risks include EOF if the payload is missing, extra bytes not detected by `getLong`, and wrong-type failure. Tests should cover valid values, negative/large values, EOF, wrong type, and human-readable output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/LongCheckpointFormat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/LongsCheckpointFormat.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/LongsCheckpointFormat.java

## Purpose
`LongsCheckpointFormat` reads and renders checkpoints containing a sequence of longs.

## Important APIs, Types, And Functions
`createReader` returns `LongsCheckpointReader`, which validates type `LONGS`. `nextLong` reads longs until `EOFException`, returning `Optional.empty`. `parseToHumanReadable` prints one long per line.

## Control Flow, State, Dependencies, Risks, And Tests
The persisted format is a type header followed by zero or more Java data-stream longs. Dependencies are `CheckpointInputStream`, `Optional`, and Guava preconditions. Risks include partial trailing long being treated as EOF, no count/checksum at this layer, and wrong-type rejection. Tests should cover empty and multi-long checkpoints, partial trailing bytes, wrong type, and render output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/LongsCheckpointFormat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/OptimizedCheckpointInputStream.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/OptimizedCheckpointInputStream.java

## Purpose
`OptimizedCheckpointInputStream` reads compressed checkpoint files while updating a message digest.

## Important APIs, Types, And Functions
The constructor wraps `Files.newInputStream` in a 4MB `BufferedInputStream`, `LZ4FrameInputStream`, and `DigestInputStream`, then passes it to `CheckpointInputStream`.

## Control Flow, State, Dependencies, Risks, And Tests
Reading the stream decompresses LZ4 data and updates the provided digest over the compressed/decompressed stream as configured by wrapper order, then `CheckpointInputStream` consumes the type id. Persistent state is the checkpoint file plus MD5 sidecar verified by `Checkpointed`. Dependencies include LZ4, Java NIO files, `MessageDigest`, and `OptimizedCheckpointOutputStream.BUFFER_SIZE`. Risks include wrapper-order checksum expectations, decompression failures, open file handles, and type header errors. Tests should cover write/read compatibility, checksum verification integration, corrupt LZ4 frames, missing files, and all checkpoint types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/OptimizedCheckpointInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/OptimizedCheckpointOutputStream.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/OptimizedCheckpointOutputStream.java

## Purpose
`OptimizedCheckpointOutputStream` writes compressed checkpoint files while updating a message digest.

## Important APIs, Types, And Functions
`BUFFER_SIZE` is 4MB. Constructors wrap `Files.newOutputStream` in a buffered stream, LZ4 frame output stream, and `DigestOutputStream`. `write(int)` and `close` delegate to the wrapped stream.

## Control Flow, State, Dependencies, Risks, And Tests
Callers write checkpoint bytes to this stream; close finalizes the LZ4 frame and output file. The digest is later saved by `Checkpointed`. Dependencies include LZ4, `FormatUtils`, Java NIO files, and `MessageDigest`. Risks include only overriding single-byte `write` while relying on `OutputStream` default array writes, partial files on exceptions, close being required for valid LZ4 frames, and buffer-size benchmark constructor misuse. Tests should cover array writes, read-back compatibility, digest sidecar verification, close/failure behavior, and custom buffer sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/OptimizedCheckpointOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/TarballCheckpointFormat.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/TarballCheckpointFormat.java

## Purpose
`TarballCheckpointFormat` identifies RocksDB checkpoints stored as single-threaded tarball archives.

## Important APIs, Types, And Functions
`createReader` returns `TarballCheckpointReader`, which validates type `ROCKS_SINGLE`. `parseToHumanReadable` prints a message directing users to `bin/alluxio readJournal`.

## Control Flow, State, Dependencies, Risks, And Tests
The actual archive payload is opaque to this class; it only validates the checkpoint type and declines textual parsing. Persistent state is the tar.gz RocksDB backup data after the checkpoint header. Dependencies are `CheckpointInputStream` and Guava preconditions. Risks include no structural validation here, poor diagnostics for corrupt archives, and no human-readable output. Tests should cover correct/wrong type validation and readJournal integration elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/TarballCheckpointFormat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/ZipCheckpointFormat.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/ZipCheckpointFormat.java

## Purpose
`ZipCheckpointFormat` identifies RocksDB checkpoints stored as parallel-created zip archives.

## Important APIs, Types, And Functions
`createReader` returns `ZipCheckpointReader`, which validates type `ROCKS_PARALLEL`. `parseToHumanReadable` prints that no string representation is available.

## Control Flow, State, Dependencies, Risks, And Tests
Like the tarball format, this class treats archive bytes as opaque after validating the type header. Persistent state is a zip-format RocksDB checkpoint. Dependencies are `CheckpointInputStream` and preconditions. Risks include no archive validation, typo in the nested class comment saying tarball-based, and limited inspectability. Tests should cover type validation, parse message, corrupt archive handling in the actual restore layer, and readJournal integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/ZipCheckpointFormat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/noop/NoopJournal.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/noop/NoopJournal.java

## Purpose
`NoopJournal` is a `Journal` implementation that discards all writes.

## Important APIs, Types, And Functions
`getLocation` returns URI `/noop`, `createJournalContext` returns `NoopJournalContext.INSTANCE`, and `close` does nothing.

## Control Flow, State, Dependencies, Risks, And Tests
There is no mutable state or persistence. It integrates with `NoopJournalSystem` and test/formatting contexts. Dependencies include URI parsing and `NoopJournalContext`. Risks include accidental use in production configuration causing complete journal loss, and `/noop` being a synthetic location. Tests should verify returned context, no-op close, URI value, and explicit configuration gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/noop/NoopJournal.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/noop/NoopJournalSystem.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/noop/NoopJournalSystem.java

## Purpose
`NoopJournalSystem` is a complete journal-system implementation with no persistence or replay behavior.

## Important APIs, Types, And Functions
`createJournal` returns `NoopJournal`; lifecycle, primacy, suspend/resume, format, checkpoint, and sink operations are no-ops. `catchup` returns a completed future. `getCurrentSequenceNumbers` and sink lookups return empty collections. `isFormatted` and `isEmpty` return true.

## Control Flow, State, Dependencies, Risks, And Tests
There is no state and no persisted journal data. It is selected by `JournalSystem.Builder` for `JournalType.NOOP`. Dependencies include `JournalSystem`, `NoopJournal`, and `CatchupFuture`. Risks are severe data loss if selected accidentally, and lack of sink callbacks even if sinks are added. Tests should cover all interface methods, builder selection, completed catch-up, formatted/empty semantics, and ensuring production defaults do not select NOOP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/noop/NoopJournalSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/options/JournalReaderOptions.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/options/JournalReaderOptions.java

## Purpose
`JournalReaderOptions` carries options for constructing journal readers.

## Important APIs, Types, And Functions
`defaults` returns a new mutable options instance. Fields are next sequence number and primary-mode flag, with fluent setters, getters, `equals`, `hashCode`, and `toString`.

## Control Flow, State, Dependencies, Risks, And Tests
The options are in-memory construction parameters; they do not persist directly but control which persisted journal sequence is read and whether reader behavior is primary-aware. Dependencies are Guava `MoreObjects` and `Objects`. Risks include default `nextSequenceNumber` of zero if callers expect one, mutable options reuse, and equality relying on boxed `Objects.equal` for primitives. Tests should cover defaults, fluent setter chaining, equality/hash, toString, and concrete reader interpretation of primary mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/options/JournalReaderOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/options/JournalWriterOptions.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/options/JournalWriterOptions.java

## Purpose
`JournalWriterOptions` carries options for constructing journal writers.

## Important APIs, Types, And Functions
`defaults` returns a mutable options instance. Fields are next sequence number and primary flag, with fluent setters, getters, `equals`, `hashCode`, and `toString`.

## Control Flow, State, Dependencies, Risks, And Tests
The options guide concrete writer initialization, including first log sequence number and primary/standby behavior. They are not persisted themselves, but wrong values affect journal log persistence. Dependencies are Guava `MoreObjects` and `Objects`. Risks include default sequence zero mismatching journal conventions, mutable reuse across writers, and primary flag misconfiguration permitting or blocking writes incorrectly. Tests should cover defaults, fluent setters, equality/hash, toString, and writer behavior for sequence and primary settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/options/JournalWriterOptions.java -->
