# subset-b-007508 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/StoragePolicySatisfier.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/StoragePolicySatisfier.java

## Purpose

`StoragePolicySatisfier` is the NameNode/external-service worker that turns a `satisfyStoragePolicy` request into concrete block movement tasks. It dequeues inode work, reads current file/block placement, compares actual storage media against the file's `BlockStoragePolicy`, chooses source and target DataNodes, submits `BlockMovingInfo` tasks, and tracks attempts until DataNodes report completion or retry limits are reached.

## Important APIs and types

- Implements `SPSService` and `Runnable`; lifecycle is `init(Context)`, `start(StoragePolicySatisfierMode)`, `stop`, `stopGracefully`, `run`, `join`.
- `BlocksMovingAnalysis` and its `Status` enum summarize per-file analysis outcomes: retry, paired targets, no targets, already satisfied, skipped, low redundancy, or task submission failure.
- `analyseBlocksStorageMovementsAndAssignToDN` is the main block-analysis routine.
- `computeBlockMovingInfos`, `findSourceAndTargetToMove`, `chooseTargetTypeInSameNode`, and `chooseTarget` build source/target pairs.
- `DatanodeMap`, `DatanodeWithStorage`, and `StorageDetails` cache live DataNode storage media and available movement capacity.
- `AttemptedItemInfo` extends `ItemInfo` with last attempt/report time and scheduled block set for the attempted-items monitor.

## Control flow

`init` wires the NameNode/external `Context`, `BlockStorageMovementNeeded` queue, attempted-items monitor, work multiplier, and retry limit. `start` rejects `NONE`, starts the main daemon and monitor, activates the needed queue, and builds a `DatanodeCacheManager`.

The `run` loop skips work if the upstream context is down or the NameNode is in safe mode. For each `ItemInfo`, it enforces `blockMovementMaxRetry`, gets file status by inode id, drops deleted directories/files, loads the current storage policy, and analyzes located blocks. Paired or retry-skipped work is put into the attempt monitor; no-target, low-redundancy, and failed movement states are requeued; already satisfied or skipped states remove SPS tracking/xattrs. The loop throttles by sleeping when the queue is empty or when scheduled block count exceeds live DataNodes times the configured work multiplier.

Block analysis rejects under-construction files, skips empty files, validates EC striped policy compatibility, computes expected storage types, removes already-satisfied/non-movable overlaps, and schedules move tasks through `ctxt.submitMoveTask`. Continuous blocks produce a single local `Block`; striped blocks are converted into internal block ids and lengths using `StripedBlockUtil`.

## State and persistence behavior

Runtime state is in memory: `isRunning`, worker thread, queue objects, monitor state, `blockCount`, retry counts, and cached DataNode storage reports. Persistent namespace effects happen indirectly through `BlockStorageMovementNeeded.removeItemTrackInfo`, which can clean the satisfy-storage-policy xattr when work is done or abandoned. The class itself does not write files or edit logs; it relies on the NameNode context, DataNode reports, and queue/monitor collaborators for persistence-visible effects.

## Dependencies and integration points

The class integrates with HDFS file metadata (`HdfsLocatedFileStatus`, `LocatedBlock`, `LocatedStripedBlock`), storage policies, EC policy validation, DataNode topology matching (`Matcher.SAME_NODE_GROUP`, `SAME_RACK`, `ANY_OTHER`), `BlockStorageMovementCommand.BlockMovingInfo`, SPS queues/monitors, and external SPS service contexts. It is also used by `ExternalStoragePolicySatisfier`, `ExternalSPSContext`, and SPS metrics.

## Risks and edge cases

- Target selection mutates the `expectedStorageTypes` and `existing` lists in place; callers must pass throwaway lists.
- The initial `foundMatchingTargetNodesForBlock` value is `true` and is OR-assigned, so careful tests are needed around partial target failures.
- EC striped block movement depends on block index mapping and internal block length calculation; off-by-one/index errors can corrupt movement requests.
- Low redundancy, under-construction files, safe mode, unavailable storage media, and retry limits all affect whether SPS cleans xattrs or requeues work.
- Scheduling capacity is approximate and held in the cached storage details for one analysis pass.

## Test signals

Relevant signals include `TestExternalStoragePolicySatisfier`, `TestPersistentStoragePolicySatisfier`, `TestStoragePolicySatisfierWithHA`, `TestStoragePolicySatisfierWithStripedFile`, WebHDFS SPS coverage, admin command tests, and mover conflict tests. Good coverage should include EC striped policies, unavailable target media, low redundancy, retry-limit cleanup, same-node moves, rack/node-group fallback, and DataNode movement-finished reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/StoragePolicySatisfier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/StoragePolicySatisfyManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/StoragePolicySatisfyManager.java

## Purpose

`StoragePolicySatisfyManager` is the BlockManager-side coordinator for satisfy-storage-policy requests. It holds administrator configuration, tracks pending path inode ids for external SPS mode, enforces the outstanding queue limit, and clears queued SPS hints when the feature or mode is disabled.

## Important APIs and types

- Constructor reads `dfs.storage.policy.enabled`, SPS mode, and max outstanding path config.
- `start`, `stop`, and `changeModeEvent` implement mode transitions for `EXTERNAL` and `NONE`.
- `addPathId`, `getNextPathId`, `removeAllPathIds`, and `getPendingSPSPaths` manage the pending inode id queue.
- `verifyOutstandingPathQLimit` protects the queue from unbounded user requests.
- `isEnabled` means external SPS mode is enabled, not that an internal worker is running.

## Control flow

Startup logs the configured mode but does not start the internal `StoragePolicySatisfier`; this manager is for external or disabled operation. On `stop` in external mode it clears path ids. On `changeModeEvent(EXTERNAL)` it stops any internal satisfier gracefully before switching. On `changeModeEvent(NONE)` it force-stops SPS, removes the xattr for each queued inode through `Namesystem.removeXattr`, clears the queue, and updates mode.

## State and persistence behavior

The path queue is an in-memory `LinkedList<Long>` guarded by synchronization on the queue object. The manager mutates persistent namespace state only while clearing queued ids: it removes `XATTR_SATISFY_STORAGE_POLICY` from each inode so disabled SPS requests do not survive as active hints.

## Dependencies and integration points

It depends on `Namesystem`, `HdfsServerConstants.XATTR_SATISFY_STORAGE_POLICY`, `DFSConfigKeys`, `StoragePolicySatisfierMode`, and the external SPS entry point. BlockManager/NameNode RPC paths use it when users invoke `satisfyStoragePolicy` or when admins reconfigure SPS mode.

## Risks and edge cases

- `getPendingSPSPaths` reads `LinkedList.size()` without synchronizing, so it is only an approximate metric under concurrent mutation.
- Queue entries are plain inode ids; stale ids are handled later by SPS or xattr cleanup.
- `isEnabled` returns true only for `EXTERNAL`, which can be misread as a generic feature-enabled flag.
- `verifyOutstandingPathQLimit` is based on a snapshot size and must be called while higher-level request paths still handle races.

## Test signals

Signals include SPS admin command tests, NameNode reconfiguration tests, persistent SPS tests, HA SPS tests, and external SPS integration tests. Important assertions are mode transitions, xattr cleanup in `NONE`, outstanding queue limit errors, and external queue polling order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/StoragePolicySatisfyManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/package-info.java

## Purpose

This package descriptor marks `org.apache.hadoop.hdfs.server.namenode.sps` as the private, unstable NameNode package that implements storage-policy satisfaction for paths.

## Important APIs and types

It applies `@InterfaceAudience.Private` and `@InterfaceStability.Unstable` to the package. The substantive APIs in the package include `StoragePolicySatisfier`, `StoragePolicySatisfyManager`, SPS queues, context interfaces, and movement listeners.

## Control flow

There is no executable control flow. The file documents package intent and sets classification annotations consumed by developers and generated docs.

## State and persistence behavior

No runtime or persistent state is defined here.

## Dependencies and integration points

The descriptor depends only on Hadoop classification annotations. It frames the SPS package as internal to HDFS NameNode/external SPS implementation rather than a stable public API.

## Risks and edge cases

The unstable/private classification gives maintainers room to change the package, but downstream users that depend on internals can break. The package summary is intentionally brief and does not document the external SPS process boundary.

## Test signals

No direct tests are expected. Indirect signal comes from compiling package annotations and from SPS integration tests that exercise classes in this package.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/AbstractTracking.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/AbstractTracking.java

## Purpose

`AbstractTracking` is the shared internal base for startup-progress tracking records. It stores begin and end timestamps with `Long.MIN_VALUE` as the undefined sentinel.

## Important APIs and types

- Package-private abstract class implementing `Cloneable`.
- Fields `beginTime` and `endTime`.
- `copy(AbstractTracking dest)` copies base timestamp fields into subclass clones.

## Control flow

There is no complex flow. Subclasses call `super.copy(clone)` inside their `clone` implementations to preserve common timing state.

## State and persistence behavior

State is in-memory only and uses monotonic timestamps assigned by `StartupProgress`. No persistence or external reporting happens here.

## Dependencies and integration points

`PhaseTracking` and `StepTracking` extend it. `StartupProgressView` interprets its sentinel values to calculate status and elapsed time.

## Risks and edge cases

All consumers must consistently treat `Long.MIN_VALUE` as undefined, not a real timestamp. Direct package-private field access keeps the type lightweight but relies on local discipline.

## Test signals

`TestStartupProgress` and `TestStartupProgressMetrics` indirectly cover begin/end cloning, elapsed time calculations, and sentinel handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/AbstractTracking.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/Phase.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/Phase.java

## Purpose

`Phase` enumerates the coarse NameNode startup phases in expected execution order: loading fsimage, loading edits, saving checkpoint, and safemode.

## Important APIs and types

Each enum constant has a stable metrics/display name and human-readable description. Public accessors are `getName()` and `getDescription()`.

## Control flow

The enum has no dynamic flow. `StartupProgress` initializes tracking for all enum values, and `StartupProgressView` iterates all phases when computing aggregate percent complete.

## State and persistence behavior

Enum state is immutable JVM metadata. Names are used for metrics identity and should be treated as compatibility-sensitive.

## Dependencies and integration points

Used throughout NameNode startup instrumentation, the startup-progress servlet/UI path, and `StartupProgressMetrics`.

## Risks and edge cases

Adding or reordering phases affects aggregate percent-complete math and emitted metric names. The overall progress calculation treats all phases as equal weight, so phase changes can alter operator-visible progress.

## Test signals

Startup progress tests should verify status transitions for each phase, complete detection through `SAFEMODE`, and metric names derived from `getName`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/Phase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/PhaseTracking.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/PhaseTracking.java

## Purpose

`PhaseTracking` is the mutable internal record for one startup phase. It stores phase-level file/size metadata and a concurrent map of runtime-created steps.

## Important APIs and types

- Extends `AbstractTracking`.
- Fields: `file`, `size`, and `ConcurrentMap<Step, StepTracking> steps`.
- `clone()` deep-copies phase timing, metadata, and each step's `StepTracking`.
- `toString()` uses `ToStringBuilder` for diagnostics.

## Control flow

`StartupProgress` mutates this record when phases begin/end or when phase file/size metadata is set. `StartupProgressView` clones it to create an immutable snapshot for readers.

## State and persistence behavior

All state is in-memory. The step map is concurrent to allow multiple startup threads to record progress without central locking. Cloning isolates readers from later mutations.

## Dependencies and integration points

Depends on `Step`, `StepTracking`, `ConcurrentHashMap`, and Commons Lang string building. It is package-private and only used inside the startup-progress package.

## Risks and edge cases

The `file` and `size` fields are not atomic as a pair, so live mutable reads could be inconsistent; callers should use `StartupProgressView`. Step key equality ignores sequence number, while ordering uses sequence number, so duplicate logical steps are collapsed in the map but sorted by the retained key.

## Test signals

Tests should exercise snapshot immutability, concurrent step creation, phase metadata propagation, and deterministic step iteration from a cloned view.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/PhaseTracking.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StartupProgress.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StartupProgress.java

## Purpose

`StartupProgress` is the thread-safe mutable recorder for NameNode startup instrumentation. Startup code marks phase and step begin/end, records file/size/total metadata, and increments counters for long-running tasks.

## Important APIs and types

- `beginPhase`, `endPhase`, `beginStep`, `endStep` update monotonic timestamps.
- `setFile`, `setSize`, `setTotal`, and `setCount` attach metadata and counters.
- `getCounter(Phase, Step)` returns an atomic `Counter` optimized for repeated loop increments.
- `getStatus(Phase)` reports `PENDING`, `RUNNING`, or `COMPLETE`.
- `createView()` returns `StartupProgressView`, a stable snapshot for readers.

## Control flow

The constructor initializes a `PhaseTracking` for every `Phase`. Mutating methods mostly no-op after overall startup completion, and step methods no-op after their phase completes. `lazyInitStep` uses `putIfAbsent` against the phase's concurrent map so multiple threads can race safely to create a step record.

## State and persistence behavior

State is in-memory, concurrent, and frozen by behavior once all phases complete. Counters use `AtomicLong` through `StepTracking`; timestamps and metadata fields are plain writes relying on eventual consistency until cloned into a view. No filesystem persistence occurs.

## Dependencies and integration points

NameNode startup code calls this class; servlets/JMX call `createView`. It depends on `Time.monotonicNow`, `PhaseTracking`, `StepTracking`, `Step`, and `Status`.

## Risks and edge cases

- `setCount` does not check phase completion, unlike counter increments and total updates, so callers can overwrite counts after completion.
- Overall completion checks all phases; missing an `endPhase(SAFEMODE)` keeps progress mutable and percent below complete.
- Duplicate `Step` objects with same file/size/type compare equal but can carry different sequence numbers for sorting if one becomes the map key.
- Plain field writes are safe from corruption but not strongly ordered across multiple metadata fields.

## Test signals

`TestStartupProgress` covers phase/step status, counters, completion freeze, metadata, view snapshots, and elapsed/percent calculations. Additional useful signals are concurrent counter increments and duplicate logical step behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StartupProgress.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StartupProgressMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StartupProgressMetrics.java

## Purpose

`StartupProgressMetrics` adapts `StartupProgress` to Hadoop Metrics2/JMX. It emits overall elapsed time and percent complete plus per-phase count, elapsed time, total, and percent metrics.

## Important APIs and types

- Implements `MetricsSource`.
- `register(StartupProgress)` constructs and registers a source.
- Constructor registers with `DefaultMetricsSystem` under `StartupProgress`.
- `getMetrics(MetricsCollector, boolean)` builds a snapshot view and populates a metrics record.

## Control flow

On each metrics poll, the class calls `startupProgress.createView()`, adds overall counters/gauges, then iterates every `Phase` from the view and emits named metrics using the phase's stable name/description.

## State and persistence behavior

The only held state is a reference to `StartupProgress`. Metrics are emitted on demand; no durable persistence is performed. Registration in the default metrics system is process-global.

## Dependencies and integration points

Integrates startup progress with Metrics2, JMX, and NameNode monitoring. It depends on metric intern helpers, `MetricsRecordBuilder`, and phase names from `Phase`.

## Risks and edge cases

Repeated construction/register calls with the same source name can collide in the metrics system. Metric names are tied to enum names and should remain stable. Snapshot creation prevents mid-poll inconsistencies but may allocate during metrics collection.

## Test signals

`TestStartupProgressMetrics` should verify source registration and emitted metric values/names for representative phase and counter states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StartupProgressMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StartupProgressView.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StartupProgressView.java

## Purpose

`StartupProgressView` is an immutable read snapshot of NameNode startup progress. It provides aggregate and per-phase/step status, counts, totals, elapsed times, percent complete, and metadata without being affected by later updates.

## Important APIs and types

- Query APIs include `getCount`, `getTotal`, `getElapsedTime`, `getPercentComplete`, `getStatus`, `getFile`, `getSize`, `getPhases`, and `getSteps`.
- Constructor clones all `PhaseTracking` records from `StartupProgress`.
- `getElapsedTime(AbstractTracking...)` and `getBoundedPercent` implement common calculations.

## Control flow

The constructor deep-clones phase and step tracking data. Aggregate count/total methods iterate steps. Overall elapsed time spans `LOADING_FSIMAGE` begin to `SAFEMODE` end/current time. Overall percent complete returns `1.0` once safemode is complete; otherwise it averages all phase percentages equally.

## State and persistence behavior

The view owns a private `HashMap<Phase, PhaseTracking>` clone. It is read-only by convention and has no persistent state. Time-dependent elapsed values for running phases still use `Time.monotonicNow`, so elapsed time can increase even though underlying begin/end data is frozen.

## Dependencies and integration points

Used by startup progress servlets/UI and `StartupProgressMetrics`. It depends on `Phase`, `Step`, `StepTracking`, `Status`, and `Time`.

## Risks and edge cases

- Equal-weight aggregate percent is approximate and can misrepresent startup phases with very different durations.
- Running elapsed time is not fully immutable because it is calculated against current monotonic time.
- `getSteps` sorts by `Step.compareTo`; sequence-number ordering depends on the specific step object retained in the map.
- Undefined totals/sizes are normalized differently: totals become zero, sizes can remain `Long.MIN_VALUE`.

## Test signals

Startup progress tests should check snapshot isolation, bounded percent values, complete safemode behavior, pending/running/complete elapsed calculations, and step ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StartupProgressView.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/Status.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/Status.java

## Purpose

`Status` is the run-state enum for startup phases: not started, currently running, or complete.

## Important APIs and types

The enum constants are `PENDING`, `RUNNING`, and `COMPLETE`. There are no methods beyond enum defaults.

## Control flow

`StartupProgress` and `StartupProgressView` derive status from begin/end timestamp sentinels: no begin is pending, begin without end is running, and both begin/end is complete.

## State and persistence behavior

The enum has immutable JVM state only. Its values are externally visible through startup-progress views and may be serialized by UI/metrics code.

## Dependencies and integration points

Referenced by `Phase` documentation, progress view APIs, and tests.

## Risks and edge cases

Status has no failed/cancelled state, so startup instrumentation can only represent progress, not explicit startup errors.

## Test signals

Tests should cover all three states through phase begin/end transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/Status.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/Step.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/Step.java

## Purpose

`Step` identifies a granular startup task within a phase, optionally by step type, file name, and file size. It is used as the key for per-step tracking.

## Important APIs and types

- Constructors support type-only, file-only, file+size, type+file, and type+file+size forms.
- Fields are immutable: `file`, `size`, `type`, and a generated `sequenceNumber`.
- Implements `Comparable<Step>` for sorted display by file and then sequence number.
- `equals`/`hashCode` use file, size, and type, not sequence number.

## Control flow

Each new instance receives a monotonically increasing process-local sequence number. Concurrent maps use equality/hash for key identity, while `StartupProgressView.getSteps` sorts retained keys with `compareTo` for display ordering.

## State and persistence behavior

State is immutable after construction. `SEQUENCE` is static in-memory state and is not persisted; it only stabilizes ordering among runtime-created step objects.

## Dependencies and integration points

Used by `StartupProgress` callers to identify work such as loading a file or processing inode/delegation-token sections. Depends on Commons Lang builders and `StepType`.

## Risks and edge cases

`compareTo` and `equals` are inconsistent because sequence number participates only in ordering. This is tolerable for display sorting but can be surprising in sorted collections. Null files are allowed and comparison behavior depends on Commons Lang handling.

## Test signals

Tests should cover equality, hash behavior, ordering, constructor metadata, and use as a key in startup progress counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/Step.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StepTracking.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StepTracking.java

## Purpose

`StepTracking` is the mutable internal record for one startup step. It stores begin/end time, an atomic progress count, and an optional total.

## Important APIs and types

- Extends `AbstractTracking`.
- `AtomicLong count` supports concurrent increments.
- `total` uses `Long.MIN_VALUE` as undefined.
- `clone()` deep-copies the atomic count value and timing/total fields.

## Control flow

`StartupProgress` initializes `StepTracking` lazily, increments `count` through returned counters, and updates timing/total fields through step APIs. `StartupProgressView` reads cloned copies.

## State and persistence behavior

State is in-memory only. Count updates are atomic; total and timestamps are plain fields intended for low-contention instrumentation.

## Dependencies and integration points

Used inside `PhaseTracking.steps` and interpreted by `StartupProgressView` for counts, totals, elapsed time, and percent complete.

## Risks and edge cases

Undefined totals turn into zero for view APIs, making percent complete zero unless a positive total is set or the phase completes. Plain begin/end/total fields can be overwritten by last writer.

## Test signals

Startup progress tests should verify atomic counter behavior, clone isolation, total handling, and phase-complete percent override.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StepTracking.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StepType.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StepType.java

## Purpose

`StepType` enumerates common kinds of NameNode startup work that may be tracked as steps: awaiting reported blocks, delegation keys/tokens, inodes, cache pools/entries, and erasure coding policies.

## Important APIs and types

Each enum constant has a metrics/display name and a description. Public accessors are `getName()` and `getDescription()`.

## Control flow

The enum is used when constructing `Step` values. It has no dynamic behavior.

## State and persistence behavior

Enum metadata is immutable. Names can become operator-visible through UI/metrics output and should be treated as compatibility-sensitive.

## Dependencies and integration points

Used by fsimage/edit loading instrumentation and startup-progress reporting.

## Risks and edge cases

The enum is not exhaustive for every possible step; callers can also construct file-only steps. Adding values requires UI/metrics tests to ensure naming remains valid.

## Test signals

Tests should verify stable names/descriptions and that `Step` equality/serialization surfaces handle type-bearing and file-bearing steps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StepType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/package-info.java

## Purpose

This package descriptor documents the NameNode startup-progress model: startup consists of coarse `Phase`s, runtime-created `Step`s, mutable recording via `StartupProgress`, immutable reads via `StartupProgressView`, and JMX exposure via `StartupProgressMetrics`.

## Important APIs and types

The package-level API surface includes `Phase`, `Step`, `StartupProgress`, `StartupProgressView`, `StartupProgressMetrics`, `Status`, and `StepType`. It is annotated `@InterfaceAudience.Private`.

## Control flow

There is no executable flow. The Javadoc explains intended flow: NameNode code records progress, readers obtain stable views, and metrics expose those views.

## State and persistence behavior

No state is stored here. It documents in-memory progress tracking and metrics exposure.

## Dependencies and integration points

Depends only on package annotations and references local startup-progress classes. Integrates conceptually with NameNode startup, UI, servlet, and JMX consumers.

## Risks and edge cases

The documentation presents phases as coarse and known in advance; future startup paths that do not fit that model may need new phases or additional step types.

## Test signals

No direct tests are expected. Compile/Javadoc checks plus startup-progress functional tests cover the package.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/TopAuditLogger.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/TopAuditLogger.java

## Purpose

`TopAuditLogger` is an `AuditLogger` implementation that feeds NameNode audit events into NNTop metrics so operators can see top users by operation.

## Important APIs and types

- Default constructor builds `HdfsConfiguration`, `TopConf`, and `TopMetrics`, then registers the metrics source if absent.
- Test/injection constructor accepts a `TopMetrics`.
- `initialize(Configuration)` is a no-op.
- `logAuditEvent` forwards audit event fields to `TopMetrics.report` and emits debug logging.

## Control flow

On each audit event, the logger attempts to report to `topMetrics` and catches `Throwable` so audit logging cannot fail the NameNode operation. If debug logging is enabled, it formats the standard audit fields and permission information.

## State and persistence behavior

The logger holds one `TopMetrics` instance. State is accumulated in rolling metrics windows, not in this class. No persistent logging beyond SLF4J is performed here.

## Dependencies and integration points

Implements the NameNode `AuditLogger` SPI. Integrates with `DefaultMetricsSystem`, `TopConf`, `TopMetrics`, `FileStatus`, and NameNode audit configuration.

## Risks and edge cases

The default constructor creates a fresh `HdfsConfiguration`, so configuration source alignment matters when used outside normal audit logger initialization. Catching `Throwable` protects operations but can hide persistent NNTop failures except for logs. The metrics source is registered only if absent, so multiple logger instances share process-global registration behavior.

## Test signals

`TestAuditLogger`, `TestAuditLogs`, `TestTopMetrics`, and NameNode MXBean top-user tests provide signals. Tests should verify disabled top logger behavior, WebHDFS audit integration, and that report failures do not break audited operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/TopAuditLogger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/TopConf.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/TopConf.java

## Purpose

`TopConf` centralizes NNTop configuration: enabled flag, reporting windows, and the special all-commands marker.

## Important APIs and types

- Public final `isEnabled`.
- Public static `ALL_CMDS = "*"`.
- Public final `int[] nntopReportingPeriodsMs`.
- Constructor reads `NNTOP_ENABLED_KEY` and `NNTOP_WINDOWS_MINUTES_KEY`.

## Control flow

The constructor parses trimmed minute strings, converts them to milliseconds with checked integer casts, and validates that each window is at least one minute.

## State and persistence behavior

Configuration is immutable after construction. It does not persist settings; it snapshots values from `Configuration`.

## Dependencies and integration points

Used by `TopAuditLogger`, `TopMetrics`, and `RollingWindowManager`. It depends on `DFSConfigKeys`, Guava `Ints.checkedCast`, and precondition checks.

## Risks and edge cases

Invalid numeric values, overflow beyond `int`, empty window lists, or sub-minute windows fail construction. Because windows are stored as `int` milliseconds, very large minute values are not accepted.

## Test signals

NameNode MXBean tests cover top-user windows, disabled state, and no-period behavior. Unit tests should also check parsing failures and one-minute minimum enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/TopConf.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/metrics/TopMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/metrics/TopMetrics.java

## Purpose

`TopMetrics` is the metrics-facing interface for NNTop. It accepts audit events, records per-command/per-user counts into rolling windows, exposes JSON-friendly top windows, and publishes flattened counters through Metrics2.

## Important APIs and types

- `rollingWindowManagers` maps reporting periods to `RollingWindowManager`.
- `report(...)` variants normalize audit events down to user and command.
- `getTopWindows()` returns `RollingWindowManager.TopWindow` snapshots for all configured windows.
- Implements `MetricsSource.getMetrics`.
- Metric names are built from operation type, total count, user, and count.

## Control flow

The constructor logs relevant NNTop configuration and creates one `RollingWindowManager` per reporting period. Each report trims the authentication method from the username and records a delta of one in every window manager. Metrics polling skips output when disabled; otherwise it snapshots windows and emits total operation counts plus top-user counts.

## State and persistence behavior

State is in-memory rolling-window data held by `RollingWindowManager`s. Nothing is persisted; old entries age out as windows expire and snapshots garbage-collect zero-sum user windows.

## Dependencies and integration points

Feeds from `TopAuditLogger` and exports to Metrics2 and FSNamesystem MBean JSON (`getTopWindows`). It depends on `UserGroupInformation.trimLoginMethod`, `Time.monotonicNow`, and the rolling-window package.

## Risks and edge cases

User and operation names are embedded in metric names; whitespace is removed from op names but user names are not similarly sanitized. Metrics source disablement affects Metrics2 output but `getTopWindows` can still return snapshots. High cardinality users/operations can grow memory until windows age out.

## Test signals

`TestTopMetrics`, `TestNameNodeMXBean.testTopUsers*`, and rolling-window tests cover top aggregation, disabled metrics source behavior, configured periods, and user ranking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/metrics/TopMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/window/RollingWindow.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/window/RollingWindow.java

## Purpose

`RollingWindow` tracks event counts over a fixed time interval using a ring of buckets. It supports concurrent increments and approximate rolling sums with bounded memory.

## Important APIs and types

- Constructor accepts `windowLenMs` and bucket count.
- `incAt(long time, long delta)` records an event count at a timestamp.
- `getSum(long time)` returns the sum of non-stale buckets.
- Nested `Bucket` holds atomic value and update time with synchronized stale reset.

## Control flow

`incAt` maps event time to a bucket by modulo window length. If the bucket's update time is outside the current rolling window, `safeReset` clears it and updates its timestamp; then the delta is atomically added. `getSum` iterates buckets and includes only non-stale values for the requested time.

## State and persistence behavior

All state is in-memory. Bucket values and update times are atomic; reset is synchronized per bucket to avoid losing concurrent updates during rollover. Counts expire by staleness rather than background cleanup.

## Dependencies and integration points

Used by `RollingWindowManager` per operation/user. Depends on SLF4J for debug logging and Java atomics.

## Risks and edge cases

The constructor contains a redundant-looking `this.bucketSize % bucketSize` check that always evaluates to zero; real validation is in `RollingWindowManager`. Out-of-order event times are tolerated only within the documented buffering-delay assumption. Bucket granularity trades memory for accuracy, and stale detection uses event/current times supplied by callers.

## Test signals

`TestRollingWindow` should cover bucket rollover, concurrent increments, out-of-order events within the window, stale bucket exclusion, and boundary times at exact window length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/window/RollingWindow.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/window/RollingWindowManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/window/RollingWindowManager.java

## Purpose

`RollingWindowManager` manages all rolling windows for one NNTop reporting period. It records counts by command and user, snapshots ranked top users per operation, and synthesizes an all-commands aggregate.

## Important APIs and types

- `recordMetric(time, command, user, delta)` updates one command/user window.
- `snapshot(time)` returns a `TopWindow`.
- Public snapshot DTOs: `TopWindow`, `Op`, and `User`.
- Internal `RollingWindowMap` maps user names to `RollingWindow`; `metricMap` maps command names to those maps.
- Internal `UserCounts` aggregates duplicate user counts and totals.

## Control flow

Construction validates bucket count, divisibility, and top-user count. Recording creates command and user windows with `putIfAbsent` and increments the chosen window. Snapshot iterates all commands, calculates top user counts for each command, removes zero-sum user windows as garbage collection, adds non-empty operations, then builds an `ALL_CMDS` op by retaining totals for users that appeared in per-op top lists.

## State and persistence behavior

State is in-memory and concurrent through `ConcurrentHashMap` plus thread-safe `RollingWindow`. Expired user windows are removed during snapshot. There is no durable state.

## Dependencies and integration points

Used by `TopMetrics`. Depends on `TopConf.ALL_CMDS`, `DFSConfigKeys`, and `RollingWindow`.

## Risks and edge cases

`Op.compareTo` and `equals` compare only total counts, while `hashCode` uses operation type; this is inconsistent for general sets/maps but current usage is list sorting. `User.compareTo` ranks by count only, so equal counts have unspecified ordering. The all-commands aggregate includes only users that were top users for some operation, not all users in the window.

## Test signals

`TestRollingWindowManager` should verify ranking, top-user limits, all-command synthesis, zero-window garbage collection, invalid configuration, and concurrent recording. NameNode MXBean top-user tests are end-to-end signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/window/RollingWindowManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/visitor/INodeCountVisitor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/visitor/INodeCountVisitor.java

## Purpose

`INodeCountVisitor` traverses a namespace tree and counts how many times each inode id is visited, primarily for validating FSImage/snapshot graph structure.

## Important APIs and types

- Static `countTree(INode root)` returns `Counts`.
- `Counts.getCount(INode)` reports visit count by inode id.
- `INodeSet` stores `SetElement` keys in a `ConcurrentHashMap`.
- Default visitor increments count for every visited `INode`.

## Control flow

`countTree` creates a visitor and starts traversal at `Snapshot.CURRENT_STATE_ID`. Every inode accepted by the traversal hits the default visitor, which inserts or finds a `SetElement` keyed by inode id and atomically increments its count.

## State and persistence behavior

Counts are in-memory only. Snapshot ids are accepted by the visitor but not included in the key, so the count is per inode id across current and snapshot traversals.

## Dependencies and integration points

Depends on `NamespaceVisitor`, `INode`, and `Snapshot`. Used in FSImage validation/test contexts where references and snapshots may cause multiple visits.

## Risks and edge cases

Counting only by inode id intentionally collapses multiple Java object references to the same id. If ids are invalid or reused, counts become misleading. The concurrent map is safe but traversal itself depends on the namespace visitor implementation.

## Test signals

FSImage validation tests can assert expected counts for normal directories, snapshots, and references. Edge coverage should include referred inodes visited through `INodeReference`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/visitor/INodeCountVisitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/visitor/NamespacePrintVisitor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/visitor/NamespacePrintVisitor.java

## Purpose

`NamespacePrintVisitor` renders the in-memory namespace tree as a text tree for tests and diagnostics, including files, symlinks, references, snapshots, quotas, and directory snapshot features.

## Important APIs and types

- Static `print2Sting(FSNamesystem)` and `print2Sting(INode)` return a string rendering.
- Implements specialized visitor methods for files, symlinks, references, directories, snapshottable directories, referred inodes, and child prefix hooks.
- Uses constants `"+-"` and `"\\-"` for branch rendering.

## Control flow

The private `print` starts traversal at current state. Each node-specific visit method writes inode details to a `PrintWriter`. Prefix hooks adjust a shared `StringBuilder` before and after children/referred inodes. Snapshottable directories print quota and snapshot count, validating that snapshot-root diffs match the feature's count.

## State and persistence behavior

State is limited to the output writer and mutable prefix builder for one traversal. It does not persist or mutate namespace state.

## Dependencies and integration points

Depends on `NamespaceVisitor`, `FSNamesystem`, inode subclasses, quota and snapshot feature classes, and inode dump methods. It is test-oriented.

## Risks and edge cases

Prefix manipulation assumes two-character branch markers; mismatched pre/post calls can corrupt output. `print2Sting` is misspelled but likely compatibility-sensitive for tests. Snapshot count mismatch throws through `Preconditions.checkState`.

## Test signals

Tests should compare output for normal trees, symlinks, snapshots, references, quotas, and empty/root directories. Snapshot feature invariant failures are useful diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/visitor/NamespacePrintVisitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/visitor/NamespaceVisitor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/visitor/NamespaceVisitor.java

## Purpose

`NamespaceVisitor` is the traversal interface for HDFS namespace trees. It provides default hooks for inode kinds, recursive reference/directory traversal, child/snapshot iteration, and pre/post callbacks around sub-elements.

## Important APIs and types

- Nested `INodeVisitor` default no-op visitor.
- Default methods: `visitFile`, `visitSymlink`, `visitReference`, `visitReferenceRecursively`, `visitDirectory`, `visitDirectoryRecursively`, `visitSnapshottable`, `visitSubs`.
- Static adapters `getChildren` and `getSnapshots` return iterable `Element`s.
- Nested `Element` holds snapshot id and inode.

## Control flow

Concrete `INode.accept` implementations call into the visitor. The default recursive directory flow visits the directory, visits current/snapshot children, and for current-state directories additionally visits snapshottable feature and snapshot roots. Reference recursion visits the reference node, then the referred inode between `preVisitReferred` and `postVisitReferred`.

## State and persistence behavior

The interface has no state. Traversal state is carried by concrete visitors and `Element` values. It does not persist or mutate namespace data by itself.

## Dependencies and integration points

Used by namespace diagnostics and validation visitors. It depends on inode types and snapshot feature/diff classes.

## Risks and edge cases

`visitSubs` names the boolean `isList` but passes it as `isLast`; behavior is correct but the local name is confusing. Snapshot iteration filters only diffs marked snapshot root. Concurrent namespace mutation during traversal is not addressed here and must be controlled by callers.

## Test signals

Visitor tests should exercise all inode kinds, recursive and non-recursive reference behavior, snapshot root traversal, empty child lists, and pre/post hook pairing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/visitor/NamespaceVisitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/web/resources/NamenodeWebHdfsMethods.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/web/resources/NamenodeWebHdfsMethods.java

## Purpose

`NamenodeWebHdfsMethods` is the JAX-RS NameNode-side implementation of WebHDFS. It handles HTTP PUT/POST/GET/DELETE operations, executes metadata operations against `ClientProtocol`, redirects block-data operations to DataNodes, manages delegation-token query construction, and preserves remote-user context across servlet and IPC call-queue boundaries.

## Important APIs and types

- JAX-RS endpoints: `putRoot`/`put`, `postRoot`/`post`, `getRoot`/`get`, `deleteRoot`/`delete`.
- Operation dispatch switches on `PutOpParam.Op`, `PostOpParam.Op`, `GetOpParam.Op`, and `DeleteOpParam.Op`.
- `init` logs parameters, lazily reads `DFS_WEBHDFS_USE_IPC_CALLQ`, and clears response content type.
- `doAs` chooses direct `ugi.doAs` or `ExternalCall` queueing.
- `chooseDatanode`, `bestNode`, and `redirectURI` implement DataNode selection and redirect URI building.
- Token helpers: `createCredentials`, `generateDelegationToken`, `renewDelegationToken`, `cancelDelegationToken`.
- Listing/trash helpers: `getListingStream`, `getDirectoryListing`, `getTrashRoot`, `getTrashRoots`, `getSnapshotRoot`, `getParent`.

## Control flow

The constructor extracts scheme, principal, trusted-proxy-aware remote address/port, and encryption-zone header support from the servlet request because external calls may run in a different thread. Endpoint methods parse URI/query parameters, call `init`, then execute the protected operation method under the request UGI.

PUT handles create redirects, mkdirs, symlink, rename, replication/owner/permission/time changes, delegation token renewal/cancel, ACL and xattr mutations, snapshot operations, storage policy operations, EC policy operations, and quota operations. POST handles append redirects, concat, truncate, and unsetting storage/EC policies. GET handles open/checksum redirects, block locations, file/link status, listing and batched listing, content summary, quota usage, delegation tokens, home directory, ACL/xattr reads, access checks, trash roots, storage and EC policy reads, server defaults caching, snapshot reports/listings, fs status, and EC codecs. DELETE handles delete and deleteSnapshot.

Redirects validate HDFS paths, choose an appropriate DataNode, include either user/doAs parameters or delegation tokens depending on security mode, include the NameNode address, and optionally return JSON `Location` when `noredirect=true`. For encrypted files with `supportEZ`, open redirects use `/.reserved/raw` and return encoded file-encryption metadata in a header.

## State and persistence behavior

The resource stores per-request-derived fields plus cached `useIpcCallq` and `supportEZ`. Persistent namespace changes happen through `ClientProtocol` RPCs: create/mkdir/rename/delete, ACL/xattr, snapshots, quotas, storage policies, EC policies, truncate, and token state. Servlet context caches `"serverDefaults"` JSON and exposes `"name.node"` and current configuration.

## Dependencies and integration points

This class is the bridge between WebHDFS clients, servlet/Jersey injection, Hadoop authentication/UGI, NameNode `ClientProtocol`/`NamenodeProtocols`, BlockManager DataNode placement, DataNode HTTP(S) info ports, JSON serialization via `JsonUtil`, delegation token secret management, encryption zones, trash, snapshots, EC, ACLs, xattrs, and audit/IPC call queue behavior.

## Risks and edge cases

- Redirect operations must preserve security parameters exactly; token kind switches between WEBHDFS and SWEBHDFS based on scheme.
- `chooseDatanode` must respect excluded nodes, offsets, decommissioned nodes, missing blocks, zero-length files, and fallback random selection.
- Streaming directory listings cannot change HTTP status after output begins, so the first batch is fetched before creating `StreamingOutput`.
- `validateOpParams` treats null or empty value strings as missing; parameter defaults must align with each operation's required fields.
- Cached server defaults can become stale if future server defaults become reloadable.
- `getSnapshotRoot` uses string prefix matching and must avoid false positives across similarly named directories.
- The resource has many query parameters and suppresses parameter-count checks in places; adding operations is easy to regress.

## Test signals

Strong signals come from `TestWebHDFS`, `TestWebHdfsDataLocality`, `TestWebHdfsCreatePermissions`, WebHDFS ACL/XAttr/token/auth/HA/URL/timeout tests, encryption-zone WebHDFS tests, trash tests, snapshot tests, storage-policy command tests, and audit-log tests. Key cases include `noredirect`, invalid paths, offset/length bounds, block-location JSON, EC policy APIs, SPS invocation, create permission masking, special-character URLs, proxy-user/delegation behavior, and DataNode locality/exclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/web/resources/NamenodeWebHdfsMethods.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BalancerBandwidthCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BalancerBandwidthCommand.java

## Purpose

`BalancerBandwidthCommand` is a `DatanodeCommand` instructing a DataNode to update the maximum bandwidth it may use for block balancing.

## Important APIs and types

- Package-private no-arg constructor defaults bandwidth to zero.
- Public constructor sets action `DatanodeProtocol.DNA_BALANCERBANDWIDTHUPDATE`.
- `getBalancerBandwidthValue()` returns bytes per second.

## Control flow

The NameNode/admin path creates this command after `dfsadmin -setBalancerBandwidth`; DataNodes receive it through heartbeat command processing and apply the new bandwidth limit.

## State and persistence behavior

The command is immutable and carries one `long` payload. Any lasting effect is in the receiving DataNode's runtime balancer bandwidth setting, not in this object.

## Dependencies and integration points

Extends `DatanodeCommand` and depends on `DatanodeProtocol` action constants. Covered by balancer/admin command flows.

## Risks and edge cases

There is no local validation for negative or extreme bandwidth; validation must occur before construction or on the receiver. The source comment misspells the admin command, but the class behavior is unaffected.

## Test signals

`TestBalancerBandwidth` and DFSAdmin tests should verify command creation, heartbeat delivery, and DataNode-side bandwidth update behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BalancerBandwidthCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BalancerProtocols.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BalancerProtocols.java

## Purpose

`BalancerProtocols` is a marker interface representing the full RPC protocol set required by the HDFS balancer: client-facing namespace operations plus NameNode internal block-location/movement operations.

## Important APIs and types

It extends `ClientProtocol` and `NamenodeProtocol`, is annotated private, and carries `@KerberosInfo` with the NameNode Kerberos principal key.

## Control flow

No methods are declared directly. RPC implementations use this combined type so the balancer can authenticate and call both parent interfaces through one proxy.

## State and persistence behavior

No state is defined here.

## Dependencies and integration points

Integrates balancer clients, Hadoop RPC security, `DFSConfigKeys.DFS_NAMENODE_KERBEROS_PRINCIPAL_KEY`, `ClientProtocol`, and `NamenodeProtocol`.

## Risks and edge cases

Any method or security annotation changes in parent protocols affect balancer compatibility. The interface is private, but RPC compatibility still matters across rolling upgrades.

## Test signals

Balancer integration tests and secure-cluster RPC tests cover this type indirectly by creating balancer proxies and running balancing operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BalancerProtocols.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockCommand.java

## Purpose

`BlockCommand` is a heartbeat command from NameNode to DataNode for block operations such as transfer/replication or invalidation. It carries blocks and optional target DataNode/storage information.

## Important APIs and types

- Extends `DatanodeCommand`.
- `NO_ACK` sentinel marks deletion commands that do not require explicit DataNode acknowledgment.
- Constructors accept either `List<BlockTargetPair>`, blocks only, or fully formed block/target/storage arrays.
- Getters expose block pool id, blocks, targets, target storage types, and target storage ids.

## Control flow

For transfer commands, the constructor converts `DatanodeStorageInfo` targets into parallel arrays of `DatanodeInfo`, `StorageType`, and storage ids. For block-only actions it uses empty target arrays. DataNode command handling interprets the action code inherited from `DatanodeCommand`.

## State and persistence behavior

The command is a mutable-array DTO but fields are final references. It does not persist state; it is serialized over DataNode protocol and acted on by DataNodes.

## Dependencies and integration points

Used by block management heartbeat scheduling, replication, invalidation, and protobuf conversion. Depends on `Block`, `DatanodeInfo`, `StorageType`, and `DatanodeStorageInfo` conversion helpers.

## Risks and edge cases

Parallel arrays must remain length-aligned with `blocks`. `NO_ACK` assumes no real block size equals `Long.MAX_VALUE`. Array contents are not defensively copied, so callers must avoid later mutation.

## Test signals

Signals include heartbeat handling tests, block manager replication/invalidation tests, and PB helper conversion tests for DataNode commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockECReconstructionCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockECReconstructionCommand.java

## Purpose

`BlockECReconstructionCommand` instructs a DataNode to reconstruct missing internal blocks in an erasure-coded striped block group and send reconstructed data to target storages.

## Important APIs and types

- Extends `DatanodeCommand`.
- Holds `Collection<BlockECReconstructionInfo>`.
- `BlockECReconstructionInfo` carries the block group, source DataNodes, target DataNodes/storage ids/storage types, live block indices, excluded reconstructed indices, and `ErasureCodingPolicy`.
- Constructors accept either target `DatanodeStorageInfo[]` or already-converted arrays.

## Control flow

The NameNode builds reconstruction tasks from block-management state and sends them to a DataNode. The receiver pulls from source nodes and reconstructs missing blocks based on live indices and EC policy. `toString` logs all tasks for diagnostics.

## State and persistence behavior

The command is an RPC DTO. It contains arrays and collections by reference and does not persist state itself. Persistent effects occur when reconstruction succeeds and DataNodes report the new replicas.

## Dependencies and integration points

Integrates EC block management, DataNode reconstruction workers, `DatanodeStorageInfo` conversion helpers, protobuf conversion, and `ErasureCodingPolicy`.

## Risks and edge cases

Array lengths and index semantics are critical; live indices, excluded indices, sources, and targets must match the EC policy. `excludeReconstructedIndices` is not null-normalized, unlike `liveBlockIndices`. Mutable arrays can be changed after construction if callers retain references.

## Test signals

`TestPBHelper`, `TestDatanodeManager`, striped reconstruction tests, rack-awareness reconstruction tests, and EC corruption tests cover conversion and scheduling. Tests should include multiple missing blocks, target storage metadata, and null/empty index arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockECReconstructionCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockIdCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockIdCommand.java

## Purpose

`BlockIdCommand` is a compact DataNode command carrying only block ids for an action tied to a block pool.

## Important APIs and types

- Extends `DatanodeCommand`.
- Constructor accepts action, block pool id, and `long[] blockIds`.
- Getters expose block pool id and block id array.

## Control flow

The NameNode constructs the command with the relevant action code; DataNode-side protocol handling interprets the ids according to that action.

## State and persistence behavior

It is an in-memory/RPC DTO. The `blockIds` array is not copied. No persistence occurs in the command object.

## Dependencies and integration points

Depends on `DatanodeCommand` and protocol action constants. It is used where block ids are sufficient and full `Block` metadata would be unnecessary overhead.

## Risks and edge cases

Array mutation after construction can change command contents. Callers must ensure ids belong to the stated block pool and that the receiving action accepts id-only payloads.

## Test signals

Protocol conversion and DataNode command-processing tests should verify block pool/id preservation and action-specific behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockIdCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockRecoveryCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockRecoveryCommand.java

## Purpose

`BlockRecoveryCommand` tells a DataNode to act as primary for lease/block recovery. It carries recovering blocks, their locations, and the new generation stamp or copy-on-truncate target block.

## Important APIs and types

- Extends `DatanodeCommand` with action `DatanodeProtocol.DNA_RECOVERBLOCK`.
- `RecoveringBlock` extends `LocatedBlock` and adds `newGenerationStamp` plus optional `recoveryBlock`.
- `RecoveringStripedBlock` adds block indices and EC policy and overrides `isStriped`.
- Constructors create empty, capacity-sized, or collection-backed commands.
- `add` appends a recovering block.

## Control flow

The NameNode enqueues recovery commands on DataNode heartbeats. The receiving DataNode coordinates with listed locations and uses the recovery id/new generation stamp to finalize block recovery. Copy-on-truncate recovery uses `getNewBlock`.

## State and persistence behavior

The command is a transport DTO. Persistent effects happen in DataNode storage and NameNode block metadata when recovery completes. The backing collection can be externally supplied and mutable.

## Dependencies and integration points

Integrates lease recovery, block management heartbeat handling, inter-DataNode protocol, EC recovery, and protobuf conversion. Depends on `LocatedBlock`, `ExtendedBlock`, `DatanodeInfo`, `Block`, and `ErasureCodingPolicy`.

## Risks and edge cases

Recovery id/new generation stamp correctness is critical to avoid stale writers or inconsistent replicas. Striped recovery must keep block indices aligned with locations. Collection mutability and array references require caller discipline.

## Test signals

`TestHeartbeatHandling`, `TestPendingRecoveryBlocks`, `TestInterDatanodeProtocol`, lease recovery tests, truncate tests, and `TestPBHelper.testConvertRecoveringBlock` provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockRecoveryCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockReportContext.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockReportContext.java

## Purpose

`BlockReportContext` carries metadata for a DataNode block report RPC: how many RPC chunks make up the report, which chunk this is, the report id, and the lease id used for block-report rate limiting.

## Important APIs and types

Fields are immutable: `totalRpcs`, `curRpc`, `reportId`, and `leaseId`. Getters expose each value.

## Control flow

The DataNode sends this context with block reports. The NameNode uses it to correlate split reports and enforce/report lease handling.

## State and persistence behavior

The object is an immutable RPC context and does not persist anything. Lease effects are handled by block-report lease logic elsewhere.

## Dependencies and integration points

Used by `DatanodeProtocol` block report calls and NameNode block-report processing. Related tests include block report lease/rate-limiting coverage.

## Risks and edge cases

The class does no validation: invalid chunk indexes, inconsistent totals, duplicate report ids, or stale lease ids must be rejected by higher-level block-report handling.

## Test signals

`TestBlockReportLease` and block-report processing tests should cover lease ids, multi-RPC reports, bypass lease id zero, and invalid report context rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockReportContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockStorageMovementCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockStorageMovementCommand.java

## Purpose

`BlockStorageMovementCommand` instructs a DataNode to move blocks from source storage media to target DataNodes/storage media to satisfy HDFS storage policies.

## Important APIs and types

- Extends `DatanodeCommand`.
- Holds `blockPoolId` and `Collection<BlockMovingInfo>`.
- `BlockMovingInfo` carries `Block`, source DataNode, target DataNode, source storage type, and target storage type.
- Getters expose all movement fields; `addBlock` can replace the block in a `BlockMovingInfo`.

## Control flow

SPS constructs `BlockMovingInfo` tasks and submits them through its context. DataNodes receiving the command pass tasks to `ExternalSPSBlockMoveTaskHandler`, which schedules physical movement and later reports attempt completion.

## State and persistence behavior

The command is an in-memory/RPC DTO. Persistent effects occur after DataNode block movement and subsequent NameNode reports. The task collection and nested fields are mutable by reference.

## Dependencies and integration points

Directly integrates `StoragePolicySatisfier`, external SPS task handling, DataNode command processing, and `BlocksStorageMoveAttemptFinished` reports.

## Risks and edge cases

Source and target storage type correctness is essential; wrong pairings can move blocks to policy-incompatible media. `addBlock` mutability is unusual for a command DTO. There is no local validation for null nodes or same source/target combinations.

## Test signals

SPS tests should inspect generated `BlockMovingInfo` tasks, DataNode task handler behavior, success/failure reports, retries, and EC internal block movement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockStorageMovementCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlocksStorageMoveAttemptFinished.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlocksStorageMoveAttemptFinished.java

## Purpose

`BlocksStorageMoveAttemptFinished` is the DataNode-to-NameNode report payload listing blocks whose storage movement attempts have finished, whether successful or failed.

## Important APIs and types

- Constructor accepts `Block[] moveAttemptFinishedBlocks`.
- `getBlocks()` returns the array.
- `toString()` formats all blocks for diagnostics.

## Control flow

After a DataNode storage movement attempt finishes, the DataNode reports the affected blocks. SPS attempt monitoring uses these reports to mark blocks complete, update timestamps, retry, or clean tracking.

## State and persistence behavior

This is a simple transport DTO with immutable array reference but mutable contents. It does not persist state itself.

## Dependencies and integration points

Works with SPS, DataNode block movement task handling, and `StoragePolicySatisfier.notifyStorageMovementAttemptFinishedBlk`.

## Risks and edge cases

The payload does not include explicit success/failure status per block, so higher layers infer completion from block reports and storage state. Array mutation after construction can change reported contents.

## Test signals

SPS attempted-items monitor tests and external SPS tests should cover report handling, timeout/retry behavior, and mixed successful/failed movement attempts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlocksStorageMoveAttemptFinished.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlocksWithLocations.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlocksWithLocations.java

## Purpose

`BlocksWithLocations` is a NameNode protocol DTO that returns blocks with their DataNode UUIDs, storage ids, and storage types. It also supports striped block group metadata for erasure-coded files.

## Important APIs and types

- Top-level holds `BlockWithLocations[]`.
- `BlockWithLocations` carries `Block`, `String[] datanodeUuids`, `String[] storageIDs`, and `StorageType[] storageTypes`.
- `StripedBlockWithLocations` extends it with `byte[] indices`, `short dataBlockNum`, and `int cellSize`.
- Getters expose all fields; `toString` formats locations as `[storageType]storageID@datanodeUuid`.

## Control flow

NameNode protocol methods construct these DTOs when clients such as the balancer request blocks for a DataNode. Striped variants wrap a base block-with-locations object and validate that the number of DataNode UUIDs matches the indices array.

## State and persistence behavior

The object is an immutable-reference DTO with mutable arrays. It does not persist state; it serializes over NameNode protocol/PB helpers.

## Dependencies and integration points

Used by `NameNodeRpcServer.getBlocks`, balancer/mover flows, and protobuf conversion tests. Depends on `Block`, `StorageType`, and Hadoop preconditions.

## Risks and edge cases

Parallel arrays must stay aligned. Only striped constructor length-checks UUIDs versus indices; it does not validate storage id/type lengths. Array mutability can cause post-construction changes. String formatting assumes aligned arrays.

## Test signals

`TestPBHelper.testConvertBlocksWithLocations`, balancer/mover tests, and NameNode RPC tests should cover replicated and striped DTO conversion, storage metadata preservation, and array alignment validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlocksWithLocations.java -->
