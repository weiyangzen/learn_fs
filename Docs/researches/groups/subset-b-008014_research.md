# subset-b-008014 research

Grouped research for `subset-b-008014`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/ReconfigurationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/ReconfigurationHandler.java

## Purpose

`ReconfigurationHandler` is the HDDS runtime reconfiguration coordinator. It extends Hadoop `ReconfigurableBase` and implements the public `ReconfigureProtocol`, exposing admin RPC methods that reload configuration, report task status, and list allowed properties. It also maps individual property names or whole prefixes to implementation callbacks.

## Important APIs, Types, and Functions

The key registration APIs are `register(String, UnaryOperator<String>)`, `register(ReconfigurableConfig)`, and `registerPrefix(String)`. Runtime RPC APIs are `startReconfigure()`, `getReconfigureStatus()`, `listReconfigureProperties()`, and `getServerName()`. Completion hooks are `registerCompleteCallback`, `setReconfigurationCompleteCallback`, and `defaultLoggingCallback`.

## Control Flow

Construction installs a Hadoop reconfiguration-complete callback. Starting reconfiguration first invokes `requireAdminPrivilege.accept("startReconfiguration")`, then starts the inherited background task. When the task completes, `getNewConf()` creates a fresh `OzoneConfiguration`, changed keys are converted to a `Map<String, Boolean>` where `false` means deletion, and registered callbacks/listeners are invoked.

## State and Persistence Behavior

The handler keeps concurrent maps/sets of explicit and prefix properties. It does not persist state itself; the persisted source is the normal configuration files loaded by `ReconfigurableBase`.

## Dependencies and Integration Points

It integrates with Hadoop `ReconfigurationTaskStatus`, HDDS `ReconfigurableConfig`, `ReconfigurationChangeCallback`, and the PB `ReconfigureProtocol` translators.

## Risks and Test Signals

`completeCallbacks` is an unsynchronized `ArrayList`, so callbacks should be registered during service setup, not while reconfiguration is completing. Prefix registrations use identity behavior unless a concrete property callback exists. Tests should cover admin checks, prefix matching, callback deletion flags, exception wrapping into `ReconfigurationException`, and sorted property listing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/ReconfigurationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/TracingReconfigurationCallback.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/TracingReconfigurationCallback.java

## Purpose

`TracingReconfigurationCallback` wires runtime configuration changes for `ozone.tracing.*` keys into HDDS tracing reinitialization. It is a narrow callback object intended to be registered with `ReconfigurationHandler`.

## Important APIs, Types, and Functions

`init(String, TracingConfig)` calls `TracingUtil.initTracing` once and returns the callback. `onPropertiesChanged(Map<String, Boolean>, Configuration)` scans changed keys for the `ozone.tracing.` prefix and calls `TracingUtil.reconfigureTracing`.

## Control Flow

Service startup calls `init`, then registers the returned object. After a reconfiguration completes, the handler supplies changed keys. This callback ignores non-tracing changes and only triggers tracing reconfigure when at least one changed property starts with the tracing prefix.

## State and Persistence Behavior

It keeps only `serviceName` and the mutable `TracingConfig` object reference. There is no direct persistence; the new configuration is supplied by the broader reconfiguration framework.

## Dependencies and Integration Points

It depends on `TracingUtil`, `TracingConfig`, and `ReconfigurationChangeCallback`. It expects tracing configuration binding to read refreshed values from the existing config object or backing configuration machinery.

## Risks and Test Signals

The `newConf` argument is not directly used, so correctness depends on how `TracingConfig` is backed. Prefix-only matching may reconfigure for any tracing key addition, update, or deletion. Tests should verify init is called once, non-tracing keys are ignored, and a tracing key deletion still triggers reconfiguration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/TracingReconfigurationCallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.hdds.conf` as the HDDS configuration package. It groups configuration beans, dynamic reconfiguration support, and configuration-facing servlet/helper classes.

## Important APIs, Types, and Functions

The file contains package-level Javadoc only. The substantive APIs in this package include `OzoneConfiguration`, `ReconfigurableBase`, `ReconfigurationHandler`, config annotations, and reconfiguration callbacks.

## Control Flow

There is no executable control flow. It contributes package documentation to generated Javadocs.

## State and Persistence Behavior

There is no state or persistence behavior.

## Dependencies and Integration Points

The descriptor integrates only through Java package metadata. It helps readers identify the package as configuration-related.

## Risks and Test Signals

There are no behavioral risks. Documentation checks or Javadoc generation are the only relevant signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/freon/FakeClusterTopology.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/freon/FakeClusterTopology.java

## Purpose

`FakeClusterTopology` pre-generates deterministic-shape but random-identity datanodes and RATIS pipelines for Freon load tests. It gives fake SCM protocol clients enough topology to allocate blocks and query nodes without contacting a real SCM.

## Important APIs, Types, and Functions

`INSTANCE` is a static singleton with nine datanodes and three pipelines. `getRandomPipeline()` returns one pipeline selected by `Random`; `getAllDatanodes()` returns the unmodifiable datanode list. `createDatanode()` builds localhost protobuf datanodes with a RATIS port.

## Control Flow

Static initialization loops over nine nodes, creates a datanode each iteration, and after every third node builds a RATIS/THREE pipeline containing the last three nodes. Exceptions are logged and the topology is still wrapped.

## State and Persistence Behavior

State is in-memory only: unmodifiable lists of `DatanodeDetailsProto` and `Pipeline`, plus a non-secure `Random`.

## Dependencies and Integration Points

It depends on HDDS protobuf types and `PipelineID.randomId()`. `FakeScmBlockLocationProtocolClient` and `FakeScmContainerLocationProtocolClient` use the singleton.

## Risks and Test Signals

The fake topology assumes exactly three-node RATIS pipelines and localhost endpoints, so it is not suitable for production-like network behavior. If initialization failed before pipeline creation, `getRandomPipeline()` could fail on an empty list. Tests should validate nine datanodes, three pipelines, immutable lists, and stable protobuf shape.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/freon/FakeClusterTopology.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/freon/FakeScmBlockLocationProtocolClient.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/freon/FakeScmBlockLocationProtocolClient.java

## Purpose

This utility returns fake `SCMBlockLocationResponse` protobufs for Freon block-allocation load tests. It avoids real SCM calls while producing plausible SCM info and container block IDs.

## Important APIs, Types, and Functions

`submitRequest(SCMBlockLocationRequest)` handles `Type.GetScmInfo` and `Type.AllocateScmBlock`. `BLOCK_PER_CONTAINER` controls container ID derivation, and a static `AtomicLong counter` provides monotonically increasing local IDs.

## Control Flow

For `GetScmInfo`, the method returns fixed `scm-id` and `cluster-id`. For `AllocateScmBlock`, it loops over `numBlocks`, increments the counter, assigns `containerID = seq / BLOCK_PER_CONTAINER`, sets `localID = seq`, and attaches a random fake pipeline. Unsupported commands throw inside the try block, are logged, and return `null`.

## State and Persistence Behavior

The only mutable state is the process-wide atomic block counter. There is no persistence.

## Dependencies and Integration Points

It depends on SCM block-location protobufs and `FakeClusterTopology`. Freon clients can use it as a static protocol shim.

## Risks and Test Signals

Returning `null` after errors pushes failure handling to callers and differs from normal RPC exception semantics. Container IDs start at zero until the counter reaches 1000. Tests should cover `GetScmInfo`, multi-block allocation, monotonic IDs under concurrency, and unsupported command behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/freon/FakeScmBlockLocationProtocolClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/freon/FakeScmContainerLocationProtocolClient.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/freon/FakeScmContainerLocationProtocolClient.java

## Purpose

This fake client returns SCM container-location protocol responses for Freon node queries. It is a lightweight stand-in for SCM when tests need healthy datanode metadata.

## Important APIs, Types, and Functions

`submitRequest(ScmContainerLocationRequest)` handles only `Type.QueryNode`. It builds a `NodeQueryResponseProto` from every fake datanode in `FakeClusterTopology.INSTANCE`.

## Control Flow

For `QueryNode`, it iterates over all fake datanodes, wraps each as an `HddsProtos.Node` with `NodeState.HEALTHY`, and returns a response with `Status.OK`. Unsupported commands throw, are caught, logged, and produce `null`.

## State and Persistence Behavior

There is no local mutable state or persistence; all topology comes from `FakeClusterTopology`.

## Dependencies and Integration Points

It depends on storage-container-location protobufs and the Freon fake topology singleton.

## Risks and Test Signals

All fake nodes are always healthy and localhost, so load tests cannot simulate stale/dead/maintenance states. `null` on unsupported requests can hide protocol misuse. Tests should verify every fake datanode appears once, the status is OK, and unsupported command handling is visible to callers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/freon/FakeScmContainerLocationProtocolClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/freon/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/freon/package-info.java

## Purpose

This package descriptor identifies `org.apache.hadoop.hdds.freon` as containing Freon helper classes for load testing.

## Important APIs, Types, and Functions

The file has package-level Javadoc only. In this subset, the package contains fake SCM block/container clients and fake topology data.

## Control Flow

There is no executable logic.

## State and Persistence Behavior

There is no state or persistence behavior.

## Dependencies and Integration Points

It contributes package documentation to Javadocs for the Freon helper namespace.

## Risks and Test Signals

No runtime risks. Javadoc generation is the only relevant check.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/freon/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/AbstractSpaceUsageSource.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/AbstractSpaceUsageSource.java

## Purpose

`AbstractSpaceUsageSource` is a convenience base for `SpaceUsageSource` implementations that measure usage for a filesystem path. It centralizes canonical-path handling, capacity/available reporting, and timing logs.

## Important APIs, Types, and Functions

The constructor stores the `File` and canonical path. `getAvailable()` delegates to `File.getUsableSpace()`, `getCapacity()` delegates to `File.getTotalSpace()`, and `time(LongSupplier, Logger)` measures and logs source-specific usage checks.

## Control Flow

Subclasses call `super(path)`, then implement `getUsedSpace()`, often by wrapping their calculation with `time`. Canonical-path resolution failures are converted to `UncheckedIOException`.

## State and Persistence Behavior

State is immutable: the original `File` and canonical path string. The class does not persist usage.

## Dependencies and Integration Points

It underpins `DU` and `DedicatedDiskSpaceUsage`, and implements common `SpaceUsageSource` behavior.

## Risks and Test Signals

Capacity and available values reflect Java filesystem APIs and can change between calls. Canonical path resolution can fail at construction. Tests should verify canonical path behavior, capacity/available delegation, and timing wrapper returning the supplier value.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/AbstractSpaceUsageSource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/CachingSpaceUsageSource.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/CachingSpaceUsageSource.java

## Purpose

`CachingSpaceUsageSource` wraps another `SpaceUsageSource`, caches capacity/available/used values, and refreshes them periodically. It reduces expensive `du` calls and allows datanode volume code to adjust used space immediately after writes/deletes.

## Important APIs, Types, and Functions

Public methods include `start()`, `shutdown()`, `refreshNow()`, `incrementUsedSpace(long)`, `decrementUsedSpace(long)`, and `snapshot()`. Read/write synchronization uses Ratis `AutoCloseableReadWriteLock`. Refresh scheduling uses a daemon `ScheduledExecutorService`.

## Control Flow

Construction loads a persisted used value if present and always refreshes capacity/available from the source. `start()` schedules full used-space refreshes after a delay and available/capacity updates at up to one-minute intervals, or refreshes immediately when refresh is zero. `refresh()` is guarded by an `AtomicBoolean` so concurrent refreshes do not overlap.

## State and Persistence Behavior

Cached values are in memory. `shutdown()` calls `persistence.save(this)` before canceling scheduled tasks and shutting down the executor. `snapshot()` memoizes an immutable `Fixed` object until values change.

## Dependencies and Integration Points

It consumes `SpaceUsageCheckParams`, `SpaceUsageSource`, and `SpaceUsagePersistence`. Factories build it for datanode volumes.

## Risks and Test Signals

`refreshNow()` assumes an executor exists, so it is unsafe when refresh is zero. Increment/decrement clamp at zero/available but can diverge until the next source refresh. Tests should cover persistence load/save, scheduled startup, clamping warnings, snapshot invalidation, and refresh exception handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/CachingSpaceUsageSource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/DU.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/DU.java

## Purpose

`DU` implements `SpaceUsageSource` using the Unix `du -sk` command. It provides accurate directory usage for datanode volumes, optionally excluding paths.

## Important APIs, Types, and Functions

Constructors accept a `File`, an optional exclude pattern, or a `Supplier<File>` exclusion provider. `getUsedSpace()` delegates to the inner `DUShell`. `constructCommand` handles Linux `--exclude` versus macOS `-I`.

## Control Flow

`DUShell.getUsed()` runs the shell command and parses the first output line. `parseExecResult` splits by tab, parses kilobytes, and converts to bytes using `OzoneConsts.KB`. Dynamic exclusion providers are evaluated each command execution.

## State and Persistence Behavior

The object stores command templates and an atomic last parsed value. It does not persist; persistence is supplied by `SaveSpaceUsageToFile`.

## Dependencies and Integration Points

It extends `AbstractSpaceUsageSource`, uses Hadoop `Shell`, and feeds `DUFactory`/`DUOptimized`.

## Risks and Test Signals

It requires a compatible platform `du`; malformed output or nonzero exits become `UncheckedIOException`. Exclude behavior differs by OS. Tests should mock shell output, verify byte conversion, exercise static and dynamic exclusions, and cover command failure paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/DU.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/DUFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/DUFactory.java

## Purpose

`DUFactory` creates `SpaceUsageCheckParams` backed by the shell-based `DU` implementation and a cache file. It is the classic accurate disk-usage factory for datanode volumes.

## Important APIs, Types, and Functions

`setConfiguration(ConfigurationSource)` loads `DUFactory.Conf`. `paramsFor(File)` creates a `DU`, reads the refresh period, and uses `SaveSpaceUsageToFile(new File(dir, "scmUsed"), refreshPeriod)`. `Conf` binds `hdds.datanode.du.refresh.period`, defaulting to one hour.

## Control Flow

Factory creation is configuration-driven. Each requested directory receives an independent source, refresh period, and persistence object.

## State and Persistence Behavior

The factory stores loaded configuration. Resulting params persist used-space cache in `scmUsed` under the volume directory.

## Dependencies and Integration Points

It implements `SpaceUsageCheckFactory` and is available through factory class-name configuration, although the current default factory is `DUOptimizedFactory`.

## Risks and Test Signals

If `setConfiguration` is not called, `conf` is null. Cache file creation depends on a positive refresh period because `SaveSpaceUsageToFile` rejects zero. Tests should verify config binding, cache path, and params construction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/DUFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/DUOptimized.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/DUOptimized.java

## Purpose

`DUOptimized` combines shell `du` of metadata paths with in-memory container data usage. It avoids scanning large container data trees when datanode container accounting already knows their sizes.

## Important APIs, Types, and Functions

The constructor creates a `DU` with an exclusion provider. `setContainerUsedSpaceProvider(Supplier<Supplier<Long>>)` links to params-held container usage. `getUsedSpace()` returns metadata `du` plus supplied container usage when configured.

## Control Flow

Every used-space check runs `metaPathDU.getUsedSpace()`. If no provider exists, it returns metadata size only. Otherwise it calls the outer supplier to obtain a current inner supplier, reads container usage, logs both components, and sums them.

## State and Persistence Behavior

State is in-memory: the underlying metadata `DU` and optional provider. Persistence is external through factory-created params.

## Dependencies and Integration Points

It implements `SpaceUsageSource` and delegates capacity/available to `DU`. `DUOptimizedFactory` wires the provider from `SpaceUsageCheckParams`.

## Risks and Test Signals

The nested supplier shape is easy to misuse and may throw at runtime if the container provider is absent or not thread-safe. Tests should verify metadata-only behavior, summed usage after provider injection, and exception propagation from either component.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/DUOptimized.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/DUOptimizedFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/DUOptimizedFactory.java

## Purpose

`DUOptimizedFactory` creates optimized disk-usage params for volumes where metadata can be scanned separately and container data usage is supplied from memory.

## Important APIs, Types, and Functions

`setConfiguration` loads `DUFactory.Conf`. `paramsFor(File, Supplier<File>)` creates a `DUOptimized`, a `SaveSpaceUsageToFile` cache at `scmUsed`, and injects `params::getContainerUsedSpace` into the source.

## Control Flow

Callers must use the overload that supplies an exclusion provider. The plain `paramsFor(File)` currently returns `null`.

## State and Persistence Behavior

The factory stores only config. Generated params persist used-space cache in the volume directory.

## Dependencies and Integration Points

This is returned by `SpaceUsageCheckFactory.defaultImplementation()`, so datanode code must call the overload when using the default optimized factory.

## Risks and Test Signals

The `paramsFor(File)` null return is a sharp edge for generic callers and should be covered. Tests should verify default factory behavior, provider wiring, cache path, and container usage propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/DUOptimizedFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/DedicatedDiskSpaceUsage.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/DedicatedDiskSpaceUsage.java

## Purpose

`DedicatedDiskSpaceUsage` is a fast `SpaceUsageSource` for volumes assumed to own their entire filesystem. It estimates used space as total capacity minus usable space.

## Important APIs, Types, and Functions

`getUsedSpace()` times `calculateUsedSpace()`. `calculateUsedSpace()` returns `getCapacity() - getFile().getUsableSpace()`.

## Control Flow

There is no traversal. Each usage query reads filesystem-level capacity and usable space from Java `File` APIs.

## State and Persistence Behavior

State is inherited immutable path data. No persistence is needed because checks are cheap.

## Dependencies and Integration Points

It extends `AbstractSpaceUsageSource` and is produced by `DedicatedDiskSpaceUsageFactory`.

## Risks and Test Signals

It is inaccurate when other data shares the filesystem, and usable space excludes some system-reserved space. Tests should verify arithmetic and construction behavior with temporary filesystems or mocked `File` behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/DedicatedDiskSpaceUsage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/DedicatedDiskSpaceUsageFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/DedicatedDiskSpaceUsageFactory.java

## Purpose

This factory builds fast df-style usage checks for dedicated datanode disks. It avoids cache persistence because filesystem capacity queries are cheap.

## Important APIs, Types, and Functions

`setConfiguration` loads `DedicatedDiskSpaceUsageFactory.Conf`. `paramsFor(File)` returns a `SpaceUsageCheckParams` with `DedicatedDiskSpaceUsage`, configured refresh period, and `SpaceUsagePersistence.None.INSTANCE`. Config key `hdds.datanode.df.refresh.period` defaults to five minutes.

## Control Flow

The factory reads refresh configuration once and produces independent params per volume.

## State and Persistence Behavior

No persistence is used for generated params. The factory stores the loaded config object.

## Dependencies and Integration Points

It implements `SpaceUsageCheckFactory` and can be selected by `hdds.datanode.du.factory.classname`.

## Risks and Test Signals

The factory assumes dedicated disks; using it on shared disks misattributes space. Tests should verify config binding, no-op persistence, and refresh period defaults.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/DedicatedDiskSpaceUsageFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/SaveSpaceUsageToFile.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/SaveSpaceUsageToFile.java

## Purpose

`SaveSpaceUsageToFile` persists a cached used-space value and timestamp so startup can avoid expensive `du` scans when a recent value is available.

## Important APIs, Types, and Functions

`load()` returns `OptionalLong` when the file contains a non-expired value and timestamp. `save(SpaceUsageSource)` deletes the old file, reads `source.getUsedSpace()`, and writes `used epochMillis` if used is positive. The constructor requires a non-null file and positive expiry.

## Control Flow

Loading uses a UTF-8 `Scanner`, reading value first and time second. Expired, missing, or malformed-incomplete cache data returns empty. Saving writes the timestamp last, so truncated files are rejected on the next load.

## State and Persistence Behavior

The cache file is the durable state. It is advisory; write failures are logged and ignored.

## Dependencies and Integration Points

It implements `SpaceUsagePersistence` and is used by `DUFactory` and `DUOptimizedFactory`.

## Risks and Test Signals

Malformed numeric data other than missing tokens can still throw scanner/parse exceptions outside the explicit `FileNotFoundException` path. Tests should cover absent files, expired files, truncated files, positive save/load, zero usage skip, and write failure logging.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/SaveSpaceUsageToFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/SpaceUsageCheckFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/SpaceUsageCheckFactory.java

## Purpose

`SpaceUsageCheckFactory` is the pluggable factory interface for datanode disk-usage sources. It allows deployments to choose accurate `du`, optimized `du`, or dedicated-disk accounting via configuration.

## Important APIs, Types, and Functions

`paramsFor(File)` is the core factory method; the overload accepting `Supplier<File>` supports exclusion paths. `create(ConfigurationSource)` loads `hdds.datanode.du.factory.classname`, reflects a no-arg factory, falls back to `defaultImplementation()`, and calls `setConfiguration`.

## Control Flow

Creation attempts class loading, constructor lookup, instantiation, and config injection. Any load/instantiate failure is logged and falls back to `DUOptimizedFactory`.

## State and Persistence Behavior

The interface itself has no state. Implementations define cache and refresh persistence behavior.

## Dependencies and Integration Points

It depends on HDDS config annotations and is a key integration point between datanode volume code and specific usage implementations.

## Risks and Test Signals

Because the default is `DUOptimizedFactory`, generic callers using only `paramsFor(File)` may receive `null`. Reflection failures are non-fatal and can silently select a different implementation except for logs. Tests should cover default fallback, invalid class names, custom class loading, and overload behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/SpaceUsageCheckFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/SpaceUsageCheckParams.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/SpaceUsageCheckParams.java

## Purpose

`SpaceUsageCheckParams` bundles all parameters needed by `CachingSpaceUsageSource`: directory, underlying source, refresh period, persistence, and optional container usage supplier.

## Important APIs, Types, and Functions

The constructor validates non-null parameters and non-negative refresh. Accessors expose `dir`, canonical `path`, `source`, `refresh`, and `persistence`. `setContainerUsedSpace` and `getContainerUsedSpace` support optimized DU composition.

## Control Flow

Construction resolves the directory canonical path and throws `UncheckedIOException` on failure. Container usage defaults to a supplier returning zero until explicitly set.

## State and Persistence Behavior

State is in-memory configuration. Persistence behavior is delegated to the supplied `SpaceUsagePersistence`.

## Dependencies and Integration Points

Factories create params; `CachingSpaceUsageSource` consumes them; `DUOptimizedFactory` uses the container supplier bridge.

## Risks and Test Signals

The container supplier is mutable and not explicitly synchronized. Zero refresh is allowed here but incompatible with `SaveSpaceUsageToFile` expiry rules if paired incorrectly. Tests should cover validation, canonical path failures, default container usage, and setter behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/SpaceUsageCheckParams.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/SpaceUsagePersistence.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/SpaceUsagePersistence.java

## Purpose

`SpaceUsagePersistence` abstracts saving and loading cached disk usage values.

## Important APIs, Types, and Functions

`load()` returns an `OptionalLong`, and `save(SpaceUsageSource)` persists the current source usage. The nested `None` implementation is a singleton no-op used for cheap sources and tests.

## Control Flow

Implementations choose their own persistence mechanism. `None.load()` always returns empty and `None.save()` does nothing.

## State and Persistence Behavior

The interface has no state. `None` has no persistent state.

## Dependencies and Integration Points

`CachingSpaceUsageSource` invokes it on construction and shutdown. `SaveSpaceUsageToFile` is the primary file-backed implementation.

## Risks and Test Signals

Persistence implementations must avoid making shutdown fragile, because cache writes are advisory. Tests should cover `None` no-op behavior and integration load/save sequencing in `CachingSpaceUsageSource`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/SpaceUsagePersistence.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.hdds.fs` as filesystem-related HDDS utilities.

## Important APIs, Types, and Functions

It contains only package-level Javadoc. The package includes disk-usage sources, factories, cache params, and persistence helpers.

## Control Flow

No executable flow.

## State and Persistence Behavior

No state or persistence behavior.

## Dependencies and Integration Points

It contributes package metadata to Javadocs.

## Risks and Test Signals

No runtime risks; documentation generation is the relevant signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/package-info.java

## Purpose

This top-level HDDS package descriptor labels `org.apache.hadoop.hdds` as generic HDDS utilities and helper classes.

## Important APIs, Types, and Functions

The file contains package-level Javadoc only. In the broader tree, this package hosts shared config keys, utilities, server helpers, protocol-adjacent classes, and filesystem abstractions.

## Control Flow

There is no executable code.

## State and Persistence Behavior

There is no state or persistence behavior.

## Dependencies and Integration Points

It integrates through Java package documentation.

## Risks and Test Signals

No runtime risks. Javadoc/package-info checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/DiskBalancerProtocol.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/DiskBalancerProtocol.java

## Purpose

`DiskBalancerProtocol` defines the client-to-datanode administrative RPC contract for DiskBalancer operations.

## Important APIs, Types, and Functions

It exposes `getDiskBalancerInfo(GetDiskBalancerInfoRequestProto)`, a default no-arg `getDiskBalancerInfo()`, `startDiskBalancer(@Nullable DiskBalancerConfigurationProto)`, `stopDiskBalancer()`, and `updateDiskBalancerConfiguration(DiskBalancerConfigurationProto)`. Methods are annotated `@Idempotent`.

## Control Flow

The interface defines no implementation. The default info method constructs a current-client-version request and delegates to the request-taking method.

## State and Persistence Behavior

No local state. Implementations may persist DiskBalancer configuration or use the last persisted config when start receives null.

## Dependencies and Integration Points

PB client/server translators implement the wire layer, and datanode services implement the actual operations.

## Risks and Test Signals

The null config semantics for start must be preserved across translators. Tests should cover default request versioning, null start config, non-null update validation, and idempotent retry behavior at the RPC layer.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/DiskBalancerProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/ReconfigureProtocol.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/ReconfigureProtocol.java

## Purpose

`ReconfigureProtocol` is the admin RPC interface used by Ozone tools to trigger and observe runtime configuration reloads.

## Important APIs, Types, and Functions

It defines `getServerName()`, `startReconfigure()`, `getReconfigureStatus()`, and `listReconfigureProperties()`, all marked idempotent and throwing `IOException`.

## Control Flow

The interface is implemented by `ReconfigurationHandler`; PB translators adapt the methods to protobuf RPC calls. Reconfiguration itself is asynchronous.

## State and Persistence Behavior

No protocol state. Implementations report task status and apply updates from configuration files.

## Dependencies and Integration Points

It depends on Hadoop `ReconfigurationTaskStatus` and is exposed for SCM, OM, and datanode through role-specific PB interfaces.

## Risks and Test Signals

Callers must handle an in-progress or never-started status. Tests should verify translator round-trips for start/end times, property changes, errors, and allowed property lists.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/ReconfigureProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/SCMSecurityProtocol.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/SCMSecurityProtocol.java

## Purpose

`SCMSecurityProtocol` defines SCM CA and certificate-management RPCs used by datanodes, OMs, SCM peers, and administrative clients.

## Important APIs, Types, and Functions

It includes certificate issuance for datanodes, OMs, SCM nodes, and generic nodes; lookup by serial; CA/root CA retrieval; certificate listing; all-root-CA retrieval; and expired-certificate removal. Kerberos server principal is SCM.

## Control Flow

The interface has no implementation. Clients submit requests through `SCMSecurityProtocolClientSideTranslatorPB`; SCM-side services validate CSRs, issue certificates, and query metadata.

## State and Persistence Behavior

Persistent behavior is in SCM certificate metadata stores, not this interface. Returned values are PEM strings or lists of PEM strings.

## Dependencies and Integration Points

It uses HDDS protobuf node identity types, `HddsProtos.NodeType`, and SCM security exceptions via translators.

## Risks and Test Signals

Certificate issuance is security-sensitive: role-specific identity validation, renewal, and CA list ordering must be tested. Translator tests should verify status-to-exception mapping and correct request type selection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/SCMSecurityProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/SecretKeyProtocol.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/SecretKeyProtocol.java

## Purpose

`SecretKeyProtocol` exposes SCM-managed symmetric secret keys used for signing and verifying short-lived tokens.

## Important APIs, Types, and Functions

The interface defines `getCurrentSecretKey()`, `getSecretKey(UUID)`, and `getAllSecretKeys()`, returning `ManagedSecretKey` objects.

## Control Flow

It is a read-oriented RPC contract. Role-specific subinterfaces add Kerberos principal constraints; SCM-specific access adds rotation.

## State and Persistence Behavior

No local state. Implementations read from SCM secret-key state and stores.

## Dependencies and Integration Points

It integrates with HDDS symmetric key clients, token secret managers, and PB secret-key translators.

## Risks and Test Signals

Returning keys is security-sensitive; role-based Kerberos access and expired-key filtering must be enforced server-side. Tests should cover missing UUID behavior, current-key availability, and all-key list conversion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/SecretKeyProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/SecretKeyProtocolDatanode.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/SecretKeyProtocolDatanode.java

## Purpose

`SecretKeyProtocolDatanode` specializes secret-key access for datanode clients.

## Important APIs, Types, and Functions

It adds no methods beyond `SecretKeyProtocol`; its primary function is `@KerberosInfo` binding with SCM as server principal and datanode as client principal.

## Control Flow

All method behavior comes from `SecretKeyProtocol`.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

It is paired with `SecretKeyProtocolDatanodePB` and datanode-side secret-key clients.

## Risks and Test Signals

The role distinction is security policy. Tests should verify the PB protocol name/principals and that datanode clients use this interface rather than OM/SCM variants.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/SecretKeyProtocolDatanode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/SecretKeyProtocolOm.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/SecretKeyProtocolOm.java

## Purpose

`SecretKeyProtocolOm` specializes secret-key access for Ozone Manager clients.

## Important APIs, Types, and Functions

It adds no methods beyond `SecretKeyProtocol`. Its role is Kerberos metadata, with SCM as server and `ozone.om.kerberos.principal` as client.

## Control Flow

Behavior is inherited from `SecretKeyProtocol`.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

It maps to `SecretKeyProtocolOmPB` and OM token verification/signing components.

## Risks and Test Signals

The hard-coded OM principal key is marked TODO to move to hdds-common. Tests should guard protocol/principal metadata and OM client wiring.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/SecretKeyProtocolOm.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/SecretKeyProtocolScm.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/SecretKeyProtocolScm.java

## Purpose

`SecretKeyProtocolScm` specializes secret-key access for SCM-to-SCM or SCM admin operations and adds explicit key rotation.

## Important APIs, Types, and Functions

It inherits key retrieval methods and adds `checkAndRotate(boolean force)`, returning whether rotation occurred or succeeded.

## Control Flow

The rotation call is implemented server-side by SCM secret-key management and exposed by the PB translator as `Type.CheckAndRotate`.

## State and Persistence Behavior

Rotation mutates SCM secret-key state and likely persistent key stores, but this interface holds no state itself.

## Dependencies and Integration Points

It pairs with `SecretKeyProtocolScmPB`, SCM HA clients, and admin paths such as `ScmClient.rotateSecretKeys`.

## Risks and Test Signals

Forced rotation can affect all token issuers/verifiers. Tests should cover forced and non-forced rotation, authorization, and propagation to clients retrieving all non-expired keys.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/SecretKeyProtocolScm.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.hdds.protocol` as HDDS protocol-related classes.

## Important APIs, Types, and Functions

The file has package-level Javadoc only. In this subset, the package includes DiskBalancer, reconfiguration, SCM security, and secret-key protocol interfaces.

## Control Flow

No executable logic.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

It contributes package documentation for protocol contracts.

## Risks and Test Signals

No runtime risks; Javadoc generation is enough.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/DiskBalancerProtocolClientSideTranslatorPB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/DiskBalancerProtocolClientSideTranslatorPB.java

## Purpose

This client translator adapts `DiskBalancerProtocol` Java calls to protobuf Hadoop RPCs against a datanode.

## Important APIs, Types, and Functions

The constructor builds `DiskBalancerProtocolPB` via `createDiskBalancerProtocolProxy`. Methods translate `getDiskBalancerInfo`, `startDiskBalancer`, `stopDiskBalancer`, and `updateDiskBalancerConfiguration`. `getUnderlyingProxyObject()` and `close()` expose/stop the proxy.

## Control Flow

Proxy creation sets `ProtobufRpcEngine`, converts `OzoneConfiguration` to Hadoop `Configuration`, and obtains a protocol proxy. Each method builds the appropriate request proto, invokes `rpcProxy`, and converts `ServiceException` to remote `IOException` via `ProtobufHelper`.

## State and Persistence Behavior

State is only the RPC proxy. Persistence is server-side.

## Dependencies and Integration Points

It depends on Hadoop RPC, UGI, NetUtils, disk-balancer protobufs, and the datanode PB interface.

## Risks and Test Signals

`updateDiskBalancerConfiguration` enforces non-null locally; `startDiskBalancer` allows null. Tests should mock the PB proxy for request construction, exception conversion, close behavior, and protocol-engine setup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/DiskBalancerProtocolClientSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/DiskBalancerProtocolPB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/DiskBalancerProtocolPB.java

## Purpose

`DiskBalancerProtocolPB` is the Hadoop RPC protobuf binding for datanode DiskBalancer operations.

## Important APIs, Types, and Functions

It extends `DiskBalancerProtocolService.BlockingInterface` and declares `@ProtocolInfo` with protocol name `org.apache.hadoop.hdds.protocol.DiskBalancerProtocol` and version 1. Kerberos server principal is the datanode principal.

## Control Flow

No implementation. Hadoop RPC uses the annotations and blocking interface to bind server and client translators.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

It integrates generated protobuf service code with Hadoop IPC.

## Risks and Test Signals

Protocol name/version and Kerberos principal must match clients and servers. Tests should verify translator proxy creation uses this interface and service methods are compatible with generated protobuf definitions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/DiskBalancerProtocolPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/DiskBalancerProtocolServerSideTranslatorPB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/DiskBalancerProtocolServerSideTranslatorPB.java

## Purpose

This server translator adapts protobuf DiskBalancer RPCs to a local `DiskBalancerProtocol` implementation.

## Important APIs, Types, and Functions

It implements `DiskBalancerProtocolPB`, stores `impl`, and implements protobuf service methods for info, start, stop, and update configuration.

## Control Flow

Each RPC unwraps request fields, calls `impl`, builds an empty or data-bearing response, and wraps `IOException` in `ServiceException`. `startDiskBalancer` maps absent config to `null`.

## State and Persistence Behavior

Only the delegate reference is stored. Mutations and persistence happen in the datanode implementation.

## Dependencies and Integration Points

It is registered on datanode RPC servers and pairs with the client translator.

## Risks and Test Signals

`updateDiskBalancerConfiguration` calls `request.getConfig()` without checking presence, relying on proto defaults. Tests should cover absent/present config behavior, exception wrapping, and response info preservation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/DiskBalancerProtocolServerSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/ReconfigureProtocolClientSideTranslatorPB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/ReconfigureProtocolClientSideTranslatorPB.java

## Purpose

This client translator adapts `ReconfigureProtocol` calls to SCM, OM, or datanode protobuf RPC interfaces.

## Important APIs, Types, and Functions

`createReconfigureProtocolProxy(NodeType, InetSocketAddress, UGI, OzoneConfiguration)` selects `ReconfigureProtocolOmPB`, `ReconfigureProtocolDatanodePB`, or SCM `ReconfigureProtocolPB`. Public methods implement server name, start, status, property listing, close, and underlying proxy access.

## Control Flow

Void request protos are reused as constants. `getReconfigureStatus()` invokes RPC then reconstructs Hadoop `ReconfigurationTaskStatus` from start/end times and `GetConfigurationChangeProto` entries, mapping optional error messages to `Optional<String>`.

## State and Persistence Behavior

State is only the RPC proxy. Reconfiguration state is remote.

## Dependencies and Integration Points

It depends on Hadoop RPC, role-specific PB interfaces, `ReconfigurationTaskStatus`, and generated reconfigure protobufs.

## Risks and Test Signals

Server-side null old values are serialized as empty strings, so old null versus empty can be lost on round trip. Tests should verify role selection, in-progress status with no end time/status map, error message mapping, and exception conversion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/ReconfigureProtocolClientSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/ReconfigureProtocolDatanodePB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/ReconfigureProtocolDatanodePB.java

## Purpose

`ReconfigureProtocolDatanodePB` is the datanode-specific protobuf RPC interface for runtime reconfiguration.

## Important APIs, Types, and Functions

It extends `ReconfigureProtocolPB`, declares the common protocol name/version, and uses the datanode Kerberos server principal.

## Control Flow

No implementation; Hadoop RPC dispatches generated service methods through the server translator.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

Used by the client translator when `NodeType.DATANODE` is requested and by datanode RPC server registration.

## Risks and Test Signals

Incorrect principal metadata would break secure admin reconfiguration. Tests should verify role-based proxy selection and protocol annotations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/ReconfigureProtocolDatanodePB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/ReconfigureProtocolOmPB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/ReconfigureProtocolOmPB.java

## Purpose

`ReconfigureProtocolOmPB` is the OM-specific protobuf RPC interface for runtime reconfiguration.

## Important APIs, Types, and Functions

It extends `ReconfigureProtocolPB` with common protocol name/version and a Kerberos server principal key of `ozone.om.kerberos.principal`.

## Control Flow

No implementation in this file.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

Selected by `ReconfigureProtocolClientSideTranslatorPB` for `NodeType.OM` and implemented by `ReconfigureProtocolServerSideTranslatorPB`.

## Risks and Test Signals

The OM principal key is hard-coded due to dependency layering. Tests should protect role selection and secure RPC metadata.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/ReconfigureProtocolOmPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/ReconfigureProtocolPB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/ReconfigureProtocolPB.java

## Purpose

`ReconfigureProtocolPB` is the SCM/default protobuf RPC binding for runtime reconfiguration.

## Important APIs, Types, and Functions

It extends generated `ReconfigureProtocolService.BlockingInterface` and declares protocol name `org.apache.hadoop.hdds.protocol.ReconfigureProtocol`, version 1, and SCM Kerberos server principal.

## Control Flow

No implementation; it is the base PB interface for SCM and role-specific subinterfaces.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

Used by client/server translators and SCM RPC registration.

## Risks and Test Signals

Protocol name/version compatibility is critical for Hadoop IPC. Tests should verify generated service compatibility and SCM role proxy creation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/ReconfigureProtocolPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/ReconfigureProtocolServerSideTranslatorPB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/ReconfigureProtocolServerSideTranslatorPB.java

## Purpose

This server translator exposes a `ReconfigureProtocol` implementation over SCM, OM, and datanode protobuf RPC interfaces.

## Important APIs, Types, and Functions

It implements all three PB interfaces and delegates to `impl`. Helpers convert property lists and `ReconfigurationTaskStatus` into protobuf responses.

## Control Flow

Each RPC calls the local implementation and wraps `IOException` in `ServiceException`. Status conversion writes start time always, end time only when stopped, and each property change with old/new values and optional full error message.

## State and Persistence Behavior

Only the delegate reference is stored. Reconfiguration state remains in `ReconfigurationHandler`/Hadoop base class.

## Dependencies and Integration Points

Paired with `ReconfigureProtocolClientSideTranslatorPB` and role-specific PB interfaces.

## Risks and Test Signals

Null old values are serialized as empty strings, potentially losing distinction from a real empty old value. Assertions on status map require stopped status to have non-null map. Tests should cover in-progress status, completed success/failure, deleted properties, and IOException wrapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/ReconfigureProtocolServerSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/SCMSecurityProtocolClientSideTranslatorPB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/SCMSecurityProtocolClientSideTranslatorPB.java

## Purpose

This client translator adapts `SCMSecurityProtocol` to the wrapper-based `SCMSecurityProtocolPB` RPC service with failover/retry support.

## Important APIs, Types, and Functions

The constructor wraps a `SCMSecurityProtocolFailoverProxyProvider` in a `RetryProxy`. `submitRequest(Type, Consumer<Builder>)` builds a traced wrapper request. Public methods implement datanode/OM/SCM/generic certificate issuance, certificate lookup/listing, CA/root CA retrieval, all-root-CA retrieval, and expired-certificate removal.

## Control Flow

Each protocol method builds the specific nested request, sets the wrapper command type and trace ID, invokes `rpcProxy.submitRequest`, calls `handleError`, and extracts the response field. Non-OK status maps by ordinal to `SCMSecurityException.ErrorCode`; protobuf service errors become remote IOExceptions.

## State and Persistence Behavior

State is the retrying PB proxy. Certificate persistence is server-side in SCM metadata.

## Dependencies and Integration Points

It integrates SCM security failover providers, tracing, generated security protobufs, and `SCMSecurityException`.

## Risks and Test Signals

Ordinal status-to-error mapping requires enum order compatibility. Some methods return only leaf certificate strings while chain helpers expose full response protos. Tests should cover every `Type`, trace ID propagation, non-OK status mapping, failover proxy close, and certificate-chain fields.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/SCMSecurityProtocolClientSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/SCMSecurityProtocolPB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/SCMSecurityProtocolPB.java

## Purpose

`SCMSecurityProtocolPB` is the Hadoop IPC protobuf binding for SCM security operations.

## Important APIs, Types, and Functions

It extends generated `SCMSecurityProtocolService.BlockingInterface` and declares protocol name `org.apache.hadoop.hdds.protocol.SCMSecurityProtocol`, version 1, and SCM Kerberos server principal.

## Control Flow

No implementation in this interface.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

Used by SCM security clients, failover proxy providers, and SCM RPC servers.

## Risks and Test Signals

Protocol annotation drift would break secure clients. Tests should verify generated service compatibility and principal metadata.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/SCMSecurityProtocolPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/SecretKeyProtocolClientSideTranslatorPB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/SecretKeyProtocolClientSideTranslatorPB.java

## Purpose

This translator adapts `SecretKeyProtocol` and `SecretKeyProtocolScm` calls to the generated SCM secret-key protobuf service with failover/retry support.

## Important APIs, Types, and Functions

The constructor creates a retrying `BlockingInterface` proxy from `SecretKeyProtocolFailoverProxyProvider`. `submitRequest(Type, Consumer<Builder>)` adds command type and trace ID. Methods include `getCurrentSecretKey`, `getSecretKey(UUID)`, `getAllSecretKeys`, and `checkAndRotate(boolean)`.

## Control Flow

Methods build nested request protos where needed, submit a wrapper RPC, validate status via `handleError`, and convert protobuf keys with `ManagedSecretKey.fromProtobuf`. Missing `getSecretKey` response returns `null`.

## State and Persistence Behavior

Only the PB proxy is stored. Key state and persistence live in SCM.

## Dependencies and Integration Points

It integrates secret-key failover proxy providers, tracing, generated `SCMSecretKeyProtocolProtos`, and `SCMSecretKeyException`.

## Risks and Test Signals

The class implements SCM rotation even when used through non-SCM roles, relying on proxy/interface selection and server authorization. Tests should cover UUID bit conversion, missing key null return, all-key list conversion, status error mapping, trace propagation, and close behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/SecretKeyProtocolClientSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/SecretKeyProtocolDatanodePB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/SecretKeyProtocolDatanodePB.java

## Purpose

`SecretKeyProtocolDatanodePB` binds datanode-role secret-key protobuf RPCs.

## Important APIs, Types, and Functions

It extends generated `SCMSecretKeyProtocolService.BlockingInterface`, sets protocol name `org.apache.hadoop.hdds.protocol.SecretKeyProtocolDatanode`, version 1, SCM server principal, and datanode client principal.

## Control Flow

No implementation.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

Used by datanode secret-key clients and failover providers.

## Risks and Test Signals

Principal metadata enforces the role contract. Tests should verify protocol annotations and proxy provider selection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/SecretKeyProtocolDatanodePB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/SecretKeyProtocolOmPB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/SecretKeyProtocolOmPB.java

## Purpose

`SecretKeyProtocolOmPB` binds OM-role secret-key protobuf RPCs.

## Important APIs, Types, and Functions

It extends generated `SCMSecretKeyProtocolService.BlockingInterface` and declares the OM protocol name/version, SCM server principal, and `ozone.om.kerberos.principal` client principal.

## Control Flow

No implementation.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

Used by OM secret-key clients and the shared client translator.

## Risks and Test Signals

Hard-coded principal key is a dependency-layering risk. Tests should verify role-specific protocol metadata and secure client wiring.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/SecretKeyProtocolOmPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/SecretKeyProtocolScmPB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/SecretKeyProtocolScmPB.java

## Purpose

`SecretKeyProtocolScmPB` binds SCM-role secret-key protobuf RPCs, including rotation access.

## Important APIs, Types, and Functions

It extends generated `SCMSecretKeyProtocolService.BlockingInterface`, sets protocol name `org.apache.hadoop.hdds.protocol.SecretKeyProtocolScm`, version 1, and SCM as both server and client Kerberos principal.

## Control Flow

No implementation.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

Used by SCM clients/admin paths that need key retrieval and rotation.

## Risks and Test Signals

Protocol/principal mismatches would block SCM HA/admin secret-key operations. Tests should verify metadata and rotation route selection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/SecretKeyProtocolScmPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/package-info.java

## Purpose

This package descriptor documents the protobuf-to-RPC wiring package for HDDS protocols.

## Important APIs, Types, and Functions

The file has package-level Javadoc only. The package contains PB interfaces and client/server translators for reconfiguration, DiskBalancer, security, and secret-key protocols.

## Control Flow

No executable code.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

It provides package documentation for Hadoop IPC binding classes.

## Risks and Test Signals

No runtime risks; Javadoc generation is the relevant check.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/client/ScmClient.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/client/ScmClient.java

## Purpose

`ScmClient` is the broad administrative/client facade for SCM container, pipeline, datanode, balancer, safe-mode, HA, secret-key, upgrade, metrics, and maintenance operations.

## Important APIs, Types, and Functions

It declares container creation/read/list/delete/close APIs, replica queries, node queries and admin state changes, pipeline lifecycle, safe-mode controls, replication manager controls/reporting, container balancer start/stop/status, SCM roles and leadership transfer, secret-key rotation, deleted-block summary, datanode usage, SCM upgrade finalization, SCM decommission, metrics, reconcile, and container suppression.

## Control Flow

The interface has no implementation. Concrete clients translate these calls to SCM protocols and compose lower-level SCM block/container/security RPCs.

## State and Persistence Behavior

No interface state. Implementations mutate SCM metadata: containers, pipelines, datanode admin state, balancer config/status, secret keys, and upgrade metadata.

## Dependencies and Integration Points

It ties command-line/admin consumers to SCM subsystems: container manager, pipeline manager, replication manager, container balancer, HA/Ratis, upgrade finalization, and metrics.

## Risks and Test Signals

The interface is wide and mixes read, write, admin, and long-running operations, so compatibility and authorization are critical. Tests should cover method-to-RPC mapping, optional balancer parameters, failure reporting lists, pagination/count limits, and close/resource behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/client/ScmClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/client/ScmTopologyClient.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/client/ScmTopologyClient.java

## Purpose

`ScmTopologyClient` keeps an OM-side cached network topology refreshed from SCM in a background thread.

## Important APIs, Types, and Functions

`start(ConfigurationSource)` fetches initial topology and schedules polling. `getClusterMap()` returns the cached `NetworkTopology`. `stop()` shuts down the executor. `parseRefreshDuration` reads `ozone.om.network.topology.refresh.duration`.

## Control Flow

Startup fetches `InnerNode` from `ScmBlockLocationProtocol`, wraps it in `NetworkTopologyImpl` using the configured schema file, stores it in an `AtomicReference`, and schedules fixed-rate `checkAndRefresh`. Refresh compares the root `InnerNode`; if changed, it rebuilds and swaps the topology.

## State and Persistence Behavior

State is an in-memory atomic cache and scheduled executor. There is no persistence.

## Dependencies and Integration Points

It depends on SCM block-location protocol, `NetworkTopologyImpl`, `InnerNode`, and OM/SCM network topology config keys.

## Risks and Test Signals

`checkAndRefresh` throws `UncheckedIOException` inside a scheduled task, which can stop future executions depending on executor behavior. `getClusterMap()` fails before `start()`. Tests should cover initial load, unchanged/changed refresh, stop behavior, parse duration, and fetch failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/client/ScmTopologyClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/client/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/client/package-info.java

## Purpose

This package descriptor documents SCM client-related classes.

## Important APIs, Types, and Functions

The file contains package-level Javadoc only. In this subset, the package contains `ScmClient` and `ScmTopologyClient`.

## Control Flow

No executable code.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

It contributes package documentation for SCM client APIs.

## Risks and Test Signals

No runtime risks; Javadoc generation is sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/client/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/DeleteBlockResult.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/DeleteBlockResult.java

## Purpose

`DeleteBlockResult` is a simple holder for SCM block deletion outcomes.

## Important APIs, Types, and Functions

The constructor stores a `BlockID` and `DeleteScmBlockResult.Result`. Accessors are `getBlockID()` and `getResult()`.

## Control Flow

No behavior beyond construction and getters.

## State and Persistence Behavior

State is in-memory mutable fields set by constructor. There is no persistence or protobuf conversion here.

## Dependencies and Integration Points

It depends on HDDS `BlockID` and SCM block-location deletion result protobuf enum. It is consumed by deletion/reporting code that needs to correlate blocks with result statuses.

## Risks and Test Signals

Fields are not final, though there are no setters. Tests should verify constructor/getter mapping and null handling expectations in consumers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/DeleteBlockResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/DeletedBlocksTransactionInfoWrapper.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/DeletedBlocksTransactionInfoWrapper.java

## Purpose

This wrapper provides JSON-friendly and conversion-friendly representation of deleted-block transaction info.

## Important APIs, Types, and Functions

It stores `txID`, `containerID`, `localIdList`, and `count`, exposes Jackson `@JsonCreator` constructor and getters, and converts among `DeletedBlocksTransactionInfo`, wrapper, and datanode `DeletedBlocksTransaction`.

## Control Flow

`fromProtobuf` returns a wrapper only if txID, containerID, and count are present; otherwise it returns null. `toProtobuf`, `fromTxn`, and `toTxn` rebuild the corresponding protobufs with local IDs and count.

## State and Persistence Behavior

The wrapper is immutable in field references, but `localIdList` is not defensively copied. Persistence is external through JSON/protobuf consumers.

## Dependencies and Integration Points

It bridges SCM `HddsProtos.DeletedBlocksTransactionInfo`, datanode protocol `DeletedBlocksTransaction`, and Jackson serialization.

## Risks and Test Signals

Returning null for incomplete protobufs can surprise callers. Mutable list aliasing can change wrapper contents after construction. Tests should cover all conversions, incomplete input, JSON round trip, and list immutability expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/DeletedBlocksTransactionInfoWrapper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/MoveDataNodePair.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/MoveDataNodePair.java

## Purpose

`MoveDataNodePair` represents a source and target datanode for container movement decisions.

## Important APIs, Types, and Functions

It stores final `DatanodeDetails src` and `tgt`, provides getters, `getProtobufMessage(int)`, `getFromProtobuf`, and a static RocksDB `Codec<MoveDataNodePair>` built with `DelegatedCodec` and `Proto2Codec`.

## Control Flow

Serialization converts both datanodes to protobuf at the requested client version. Deserialization requires a non-null proto and converts both endpoints back to `DatanodeDetails`.

## State and Persistence Behavior

Object state is immutable references. The codec persists move pairs in SCM metadata, specifically the move table keyed by container ID.

## Dependencies and Integration Points

It integrates datanode identity, `MoveDataNodePairProto`, client-version-aware protobuf conversion, and SCM metadata tables.

## Risks and Test Signals

There is no explicit null validation for constructor arguments, so serialization can fail later. Tests should cover codec round trips, client version compatibility, null proto rejection, and equality expectations in table consumers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/MoveDataNodePair.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/package-info.java

## Purpose

This package descriptor documents SCM container helper classes and protocol-buffer utilities.

## Important APIs, Types, and Functions

The file has package-level Javadoc only. This subset includes delete-block results, deleted-block transaction wrappers, and move datanode pairs.

## Control Flow

No executable code.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

It contributes package documentation for SCM container helper classes.

## Risks and Test Signals

No runtime risks; documentation generation is the relevant signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHAUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHAUtils.java

## Purpose

`SCMHAUtils` centralizes utility logic for SCM high availability: primordial-node detection, Ratis directory selection, node-list manipulation, exception unwrapping/classification, and retry/failover decisions.

## Important APIs, Types, and Functions

Key methods include `getPrimordialSCM`, `isPrimordialSCM`, `getSCMRatisDirectory`, `getSCMRatisSnapshotDirectory`, `removeSelfId`, `unwrapException`, exception classifiers, and `getRetryAction`.

## Control Flow

Directory methods use explicit config values or fall back to component defaults. `removeSelfId` clones configuration, removes the local SCM ID from service-specific node lists, and returns the clone. Retry action first fails for access-control and no-failover RPC exceptions, retries without failover for specific retriable classes, fails for known non-retriable SCM exceptions, and otherwise failovers until max count.

## State and Persistence Behavior

The class is stateless. Returned configurations/directories affect external HA/Ratis persistence.

## Dependencies and Integration Points

It depends on SCM config keys, `HddsUtils`, Ratis exceptions, Hadoop retry policies, remote exceptions, and SCM-specific exception classes.

## Risks and Test Signals

Exception classification depends on wrapping shapes and class lists. `removeSelfId` does not trim node IDs. Tests should cover direct/wrapped exceptions, access-control failure, retry count boundaries, directory fallbacks, and node-list removal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHAUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHandler.java

## Purpose

`SCMHandler` is a base interface for SCM handlers participating in Ratis-backed HA request processing.

## Important APIs, Types, and Functions

It defines one method, `getType()`, returning an `SCMRatisProtocol.RequestType`.

## Control Flow

No implementation. Dispatcher code can use `getType()` to route or register handlers by Ratis request type.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

It depends on generated `SCMRatisProtocol.RequestType` and integrates with SCM HA/Ratis command handlers.

## Risks and Test Signals

Handler type uniqueness is enforced outside this interface. Tests should verify registrations do not collide and handlers report the expected request type.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/ha/SequenceIdType.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/ha/SequenceIdType.java

## Purpose

`SequenceIdType` enumerates persisted sequence counters managed by SCM HA sequence ID generation. Enum names are intentionally persisted RocksDB keys.

## Important APIs, Types, and Functions

Constants include `localId`, `delTxnId`, `containerId`, `CertificateId`, and deprecated `rootCertificateId`. `getCodec()` returns a custom `Codec<SequenceIdType>` supporting byte arrays and `CodecBuffer`.

## Control Flow

Each enum constant encodes its name with `StringCodec`. Decoding uses the first byte as a fast lookup, then verifies full byte equality. Static initialization ensures first-byte uniqueness across constants.

## State and Persistence Behavior

Persisted state is the enum name bytes stored as RocksDB keys in the sequence ID table. Byte arrays are cloned and byte buffers duplicated for safety.

## Dependencies and Integration Points

Used by `SCMMetadataStore.getSequenceIdTable()` and sequence ID generation. Depends on HDDS DB codec abstractions.

## Risks and Test Signals

Renaming enum constants or adding one with duplicate first byte can break persisted compatibility or class initialization. Tests should cover codec byte and buffer round trips, unknown bytes, deprecated key compatibility, and static uniqueness.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/ha/SequenceIdType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/ha/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/ha/package-info.java

## Purpose

This package descriptor documents SCM HA utility classes.

## Important APIs, Types, and Functions

The file has package-level Javadoc only. The package includes HA utilities, Ratis handler markers, and sequence ID types.

## Control Flow

No executable code.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

It contributes package documentation for SCM HA.

## Risks and Test Signals

No runtime risks; Javadoc generation is sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/ha/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/metadata/DBTransactionBuffer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/metadata/DBTransactionBuffer.java

## Purpose

`DBTransactionBuffer` abstracts SCM metadata writes so callers can add/remove table mutations without depending on whether updates are immediately applied or buffered for HA replication.

## Important APIs, Types, and Functions

It declares generic `addToBuffer(Table<KEY, VALUE>, KEY, VALUE)`, `removeFromBuffer(Table<KEY, VALUE>, KEY)`, and `close()`.

## Control Flow

Implementations decide whether calls write directly to tables or stage into a batch/Ratis transaction.

## State and Persistence Behavior

The interface has no state. Implementations may buffer persistent RocksDB mutations.

## Dependencies and Integration Points

It depends on HDDS DB `Table`, `CodecException`, and `RocksDatabaseException`. `SCMDBTransactionBufferImpl` is the non-Ratis direct implementation.

## Risks and Test Signals

Callers must close buffers when implementations require flushing/releasing resources. Tests should verify add/remove semantics through direct and HA implementations and exception propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/metadata/DBTransactionBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/metadata/Replicate.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/metadata/Replicate.java

## Purpose

`@Replicate` marks SCM metadata methods that should be invoked through Ratis rather than directly mutating local state.

## Important APIs, Types, and Functions

The annotation targets methods, is inherited, retained at runtime, and has `invocationType()` with enum values `DIRECT` and `CLIENT`, defaulting to `DIRECT`.

## Control Flow

Interceptors/proxies inspect the annotation at runtime. `DIRECT` submits to the local Ratis server and requires leadership; `CLIENT` submits through a Ratis client and need not run on the leader.

## State and Persistence Behavior

No state. It controls whether method effects are replicated and persisted through Ratis.

## Dependencies and Integration Points

Used by SCM HA metadata services/proxies that route annotated calls.

## Risks and Test Signals

Missing annotation on mutating methods can bypass replication; wrong invocation type can fail on followers or add unnecessary client hops. Tests should verify annotation discovery and routing for direct and client modes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/metadata/Replicate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/metadata/SCMDBTransactionBufferImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/metadata/SCMDBTransactionBufferImpl.java

## Purpose

`SCMDBTransactionBufferImpl` is the simple non-Ratis `DBTransactionBuffer` implementation for SCM metadata.

## Important APIs, Types, and Functions

`addToBuffer` calls `table.put`; `removeFromBuffer` calls `table.delete`; `close` is a no-op.

## Control Flow

Mutations are applied immediately to the supplied table rather than staged.

## State and Persistence Behavior

The object has no internal state. Persistence behavior is whatever the table implementation provides for `put` and `delete`.

## Dependencies and Integration Points

Used when SCM is not buffering mutations for Ratis. Depends on HDDS DB `Table`.

## Risks and Test Signals

The name says buffer, but this implementation writes immediately, so callers relying on atomic multi-table batching need a different implementation. Tests should verify immediate writes/deletes and no-op close.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/metadata/SCMDBTransactionBufferImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/metadata/SCMMetadataStore.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/metadata/SCMMetadataStore.java

## Purpose

`SCMMetadataStore` is the central interface for SCM persistent metadata tables and lifecycle.

## Important APIs, Types, and Functions

Lifecycle methods are `start(OzoneConfiguration)` and `stop()`. Table accessors include deleted block transactions, valid certs, valid SCM certs, pipelines, containers, sequence IDs, move records, meta key/value strings, and stateful service config. It also exposes `getStore()` for testing and `getBatchHandler()`.

## Control Flow

Implementations initialize the underlying `DBStore`, construct typed tables/codecs, and return handles for managers to read/write. Batch handlers coordinate atomic updates where supported.

## State and Persistence Behavior

All table accessors represent persistent SCM RocksDB state: containers, pipelines, certificates, delete transactions, sequence IDs, move plans, upgrade/layout metadata, and service configs.

## Dependencies and Integration Points

It extends `DBStoreHAManager` and is consumed by SCM container, pipeline, security, HA, upgrade, and balancing managers.

## Risks and Test Signals

Schema/table compatibility is critical across upgrades and HA snapshots. Tests should verify table definitions/codecs, start/stop lifecycle, batch atomicity, checkpoint/HA integration, and persistence across restart.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/metadata/SCMMetadataStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/metadata/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/metadata/package-info.java

## Purpose

This package descriptor documents SCM metadata utilities.

## Important APIs, Types, and Functions

The file has package-level Javadoc only. The package includes metadata-store interfaces, replication annotations, and transaction buffer abstractions.

## Control Flow

No executable code.

## State and Persistence Behavior

No state or persistence in the descriptor.

## Dependencies and Integration Points

It contributes package documentation for SCM metadata code.

## Risks and Test Signals

No runtime risks; Javadoc generation is the relevant signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/metadata/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/net/InnerNodeImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/net/InnerNodeImpl.java

## Purpose

`InnerNodeImpl` is the mutable tree-node implementation for Ozone network topology. Inner nodes represent topology scopes such as datacenters or racks; leaves are datanodes.

## Important APIs, Types, and Functions

It implements `InnerNode` with child management, leaf counts, path lookup, level queries, indexed leaf selection, exclusion-aware leaf selection, protobuf serialization/deserialization, equality, and a `Factory`. Children are kept in insertion order in a `LinkedHashMap` keyed by network name.

## Control Flow

`add(Node)` validates ancestry, creates missing intermediate inner nodes, attaches leaves, and increments `numOfLeaves` along the path only for new additions. `remove(Node)` recursively removes leaves, prunes empty inner nodes, and decrements counts. `getNode` handles absolute and relative paths. `getLeaf` walks children by accumulated leaf counts, with exclusion-aware variants subtracting excluded scopes and ancestor-derived counts.

## State and Persistence Behavior

State is the child map and descendant leaf count. `toProtobuf` persists node topology, leaves, and children; `fromProtobuf` reconstructs a tree, though parent links from deserialization depend on nested conversion behavior.

## Dependencies and Integration Points

It extends `NodeImpl`, uses `NodeSchemaManager` for costs and protobuf conversion, and is the default factory used by `NetworkTopologyImpl`.

## Risks and Test Signals

The class is described as thread-safe but does not lock internally; callers rely on `NetworkTopologyImpl` locks. Deserialized parent pointers may require validation. Tests should cover add/update/remove count invariants, path lookup, exclusion-aware selection, protobuf round trip, insertion-order leaf indexing, and equality.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/net/InnerNodeImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/net/NetworkTopologyImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/net/NetworkTopologyImpl.java

## Purpose

`NetworkTopologyImpl` represents the cluster network tree and implements node membership, random placement selection, affinity/exclusion logic, distance costing, and replica sorting.

## Important APIs, Types, and Functions

Public APIs include `add`, `update`, `remove`, `contains`, ancestor/parent checks, `getNode(String)`, level counts/nodes, multiple `chooseRandom` overloads, indexed `getNode`, `getDistanceCost`, `sortByDistanceCost`, and `toString`. It uses a fair `ReentrantReadWriteLock` around mutable tree access.

## Control Flow

Construction initializes `NodeSchemaManager`, max level, root inner node, and shuffle operation. Add/update validate leaf depth against schema before mutating. Selection normalizes scope, handles reverse scopes, validates excluded scopes and affinity node, narrows scope to affinity ancestor when required, removes duplicate exclusions, computes available leaves, and chooses either a supplied index modulo availability or a random index. Distance cost climbs both nodes to a common ancestor, summing parent costs. Sorting groups nodes by cost and shuffles ties.

## State and Persistence Behavior

State is in-memory: schema manager, root `InnerNode`, max level, factory, shuffle function, and lock. Persistence/serialization of tree nodes is handled by `InnerNodeImpl` protobuf methods and SCM topology RPCs.

## Dependencies and Integration Points

It integrates with placement policies, OM topology cache, `NodeSchemaManager`, `NetUtils`, `InnerNodeImpl`, and datanode `Node` implementations.

## Risks and Test Signals

Several methods call other lock-taking methods while holding read locks; the lock is reentrant-compatible only because it is a `ReentrantReadWriteLock`. Selection mutates local exclusion collections and can return null for exhausted scopes. Tests should cover schema depth rejection, update replacing existing nodes, reverse scopes, affinity narrowing, ancestor-gen exclusions, distance sorting with shuffle tie behavior, and concurrent read/write access.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/net/NetworkTopologyImpl.java -->
