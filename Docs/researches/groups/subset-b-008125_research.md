# Research Report: subset-b-008125

Grouped research for Apache Ozone Recon task, upgrade, API, and web resource files. Each section is source-tree-aligned and bounded by the reconciliation markers required for per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OMUpdateEventBatch.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OMUpdateEventBatch.java

Purpose: `OMUpdateEventBatch` is the `ReconEvent` wrapper for a batch of OM DB delta events consumed by Recon tasks. It binds a `List<OMDBUpdateEvent>` to the batch sequence number that downstream task status records use as the last processed OM sequence.

Important APIs and types: the constructor accepts the event list and `batchSequenceNumber`; `getLastSequenceNumber()` exposes the sequence internally to the task package; `getIterator()`, `getEvents()`, and `isEmpty()` expose the batch contents; `getEventType()` returns `OM_UPDATE_BATCH`; `getEventCount()` returns `events.size()` for metrics and buffer accounting.

Control flow and integration: `ReconTaskControllerImpl.consumeOMEvents` offers instances to `OMUpdateEventBuffer`; the async event processor dispatches the batch to registered `ReconOmTask.process` implementations. `OmTableInsightTask.process` iterates through this wrapper.

State and persistence: the class is immutable in fields but does not defensively copy the provided list, so outside mutation of the list would affect later consumers. It does not persist data itself; persistence happens through task status updaters and task-specific managers after processing.

Dependencies: Java collection iterators, `OMDBUpdateEvent`, and the local `ReconEvent` interface.

Risks and test signals: tests should cover empty batches, event count metrics, sequence propagation, and mutation assumptions around the input list. The package-private sequence getter means only same-package controller code can update status from it.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OMUpdateEventBatch.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OMUpdateEventBuffer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OMUpdateEventBuffer.java

Purpose: `OMUpdateEventBuffer` is a bounded queue for Recon events while task reprocessing or async delta processing is active. It prevents OM sync from directly blocking on expensive task work and provides overflow signals for full snapshot fallback.

Important APIs and types: `offer(ReconEvent)` enqueues OM update batches or control events, increments `totalBufferedEvents`, updates `ReconTaskControllerMetrics`, and records dropped batches when the queue is full. `poll(long)` blocks up to a timeout, decrements buffered event counts, and increments processed event metrics. `getQueueSize()`, `getDroppedBatches()`, `resetDroppedBatches()`, `clear()`, and `drainTo(Collection)` are used by controller logic and tests.

Control flow and integration: `ReconTaskControllerImpl` owns one buffer. Normal delta events are enqueued by `consumeOMEvents`; `processBufferedEventsAsync` polls and dispatches. Reinitialization events are also enqueued through the same buffer. On overflow, the controller drains events, cleans checkpoint resources, and requests full-snapshot style recovery.

State and persistence: state is in-memory only: a `LinkedBlockingQueue`, total buffered event counter, and dropped batch counter. Metrics mirror queue state but are not authoritative persistence.

Dependencies: `BlockingQueue`, atomics, `ReconEvent`, `ReconTaskControllerMetrics`, SLF4J.

Risks and test signals: `drainTo` subtracts the sum over the entire supplied collection, not only newly drained elements, so callers should pass an empty collection. Overflow tests should verify dropped counters, metric increments, queue size, interrupt handling in `poll`, and counter consistency after drains and clears.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OMUpdateEventBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OmTableHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OmTableHandler.java

Purpose: `OmTableHandler` is the strategy interface used by `OmTableInsightTask` for OM tables that need more than simple record counting. Its implementations calculate object counts plus unreplicated and replicated byte totals for size-related tables.

Important APIs and types: `handlePutEvent`, `handleDeleteEvent`, and `handleUpdateEvent` mutate supplied maps for object counts, logical size, and replicated size. `getTableSizeAndCount` performs full-table scanning during reprocess and returns a `Triple<count, unreplicatedSize, replicatedSize>`. Default key helpers create global stats keys such as `<table>Count`, `<table>ReplicatedDataSize`, and `<table>UnReplicatedDataSize`.

Control flow and integration: `OmTableInsightTask` registers handlers for open key, open file, deleted, and multipart tables. Incremental OMDB events are routed to the handler based on action. Full reprocess calls `getTableSizeAndCount`.

State and persistence: handlers operate on caller-provided maps and do not store durable state. Persistence happens later when `OmTableInsightTask.writeDataToDB` writes global stats via `ReconGlobalStatsManager`.

Dependencies: `OMDBUpdateEvent`, `OMMetadataManager`, Apache Commons `Triple`.

Risks and test signals: implementors must handle null values and old values consistently, must avoid negative counters on deletes, and must return values compatible with global stat key naming. Unit tests should include PUT, DELETE, UPDATE, null payloads, and full table scans for each handler implementation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OmTableHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OmTableInsightTask.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OmTableInsightTask.java

Purpose: `OmTableInsightTask` is a `ReconOmTask` that maintains global Recon stats for every OM metadata table, including table object counts and size totals for selected key-related tables. It supports both full reprocess from OM RocksDB and incremental update from OM delta events.

Important APIs and types: `init()` loads table names and initializes count and size maps from current global stats. `reprocess(OMMetadataManager)` scans all OM tables and writes reconstructed stats. `process(OMUpdateEventBatch, Map)` applies PUT, DELETE, and UPDATE deltas. `getStagedTask` creates a task bound to a staged Recon DB for controller reinitialization. Helpers include `initializeCountMap`, `initializeSizeMap`, key-name builders, and test setters.

Control flow: full reprocess iterates over `tables`. Handler tables call `OmTableHandler.getTableSizeAndCount`; non-string key tables use sequential byte-key iteration; string-key count-only tables use `ParallelTableIteratorOperation`. Incremental processing iterates the event batch, skips untracked tables, dispatches by action, updates in-memory maps, then batch-writes global stats. `writeDataToDB` opens an atomic RocksDB batch operation, stores `GlobalStatsValue` entries, and commits.

State and persistence: mutable maps cache stats across processing. Durable state is Recon global stats stored through `ReconGlobalStatsManager`; staged reprocess writes to staged DB before the controller swaps providers.

Dependencies: OM DB definitions, Recon metadata managers, table handlers, RocksDB batch APIs, `ParallelTableIteratorOperation`, Guice, and `Time`.

Risks and test signals: `processTableInParallel` puts the same count key twice, harmless but suspicious. Map state is reused, so tests should cover init ordering, delta after reprocess, negative-bound delete behavior, handler size arithmetic, write failures that only log, non-string table fallback, and staged DB manager binding.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OmTableInsightTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OmUpdateEventValidator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OmUpdateEventValidator.java

Purpose: `OmUpdateEventValidator` validates that an OM DB update event value type matches the expected value type declared by `OMDBDefinition` for the event table.

Important APIs and types: the constructor takes an `OMDBDefinition`. `isValidEvent(String tableName, Object actualValueType, Object keyType, OMDBUpdateAction action)` compares `omdbDefinition.getColumnFamily(tableName).getValueType().getName()` with `actualValueType.getClass().getName()`. `setLogger` is test-only support for verifying warnings.

Control flow and integration: callers use the validator before handing decoded events to task processing. On mismatch it logs table, key, action, expected type, and actual type, then returns false.

State and persistence: state is just the OM DB definition reference and a static logger. It has no durable writes and no metrics.

Dependencies: `OMDBDefinition`, `OMDBUpdateEvent.OMDBUpdateAction`, SLF4J.

Risks and test signals: `actualValueType` and `keyType` are dereferenced without null checks, so null event values can throw if not filtered by callers. `getColumnFamily(tableName)` must exist. Tests should cover matching types, mismatches with logged details, invalid table names, and null handling expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OmUpdateEventValidator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OpenKeysInsightHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OpenKeysInsightHandler.java

Purpose: `OpenKeysInsightHandler` implements `OmTableHandler` for open key and open file tables. It maintains counts and size totals for unclosed keys visible in Recon insights.

Important APIs and types: `handlePutEvent` casts the event value to `OmKeyInfo`, increments count, logical size, and replicated size. `handleDeleteEvent` subtracts those values with zero floors. `handleUpdateEvent` requires both old and new `OmKeyInfo` and applies size deltas without changing count. `getTableSizeAndCount` scans the OM table and totals `OmKeyInfo.getDataSize()` and `getReplicatedSize()`.

Control flow and integration: `OmTableInsightTask` registers this handler for `OPEN_KEY_TABLE` and `OPEN_FILE_TABLE`. Incremental deltas mutate maps that are later persisted to global stats. Full reprocess iterates the actual OM table.

State and persistence: the handler is stateless. Durable state is the caller's eventual write to Recon global stats.

Dependencies: HDDS `Table` and `TableIterator`, `OMMetadataManager`, `OmKeyInfo`, Commons `Triple`.

Risks and test signals: casts assume validated event payload type. Delete subtraction uses `size > delta ? size - delta : 0`, so exact equality becomes zero as intended. Update can drive values negative if old value exceeds current map value. Tests should cover put/delete/update, missing old values, null values, iterator close behavior, and both open key and open file table names.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OpenKeysInsightHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ReconEvent.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ReconEvent.java

Purpose: `ReconEvent` is the small envelope interface that lets `OMUpdateEventBuffer` carry both OM delta batches and Recon control events.

Important APIs and types: implementors expose `getEventType()` and `getEventCount()`. `EventType` currently has `OM_UPDATE_BATCH` and `TASK_REINITIALIZATION`.

Control flow and integration: `OMUpdateEventBatch` returns `OM_UPDATE_BATCH`; `ReconTaskReInitializationEvent` returns `TASK_REINITIALIZATION`. `ReconTaskControllerImpl.processReconEvent` switches on the type to call either delta processing or task reinitialization.

State and persistence: no state or persistence. The event count is used for queue accounting and metrics.

Dependencies: none outside the package.

Risks and test signals: adding a new event type requires controller dispatch support and metrics semantics for event counts. Tests should cover dispatch behavior for all enum values and unknown/default paths if the enum expands.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ReconEvent.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ReconOmTask.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ReconOmTask.java

Purpose: `ReconOmTask` is the common contract for Recon tasks that consume OM metadata deltas and can rebuild themselves from a full OM metadata snapshot.

Important APIs and types: tasks implement `getTaskName`, `process(OMUpdateEventBatch, Map<String,Integer>)`, and `reprocess(OMMetadataManager)`. Optional hooks include `init()` and `getStagedTask(ReconOMMetadataManager, DBStore)`. The nested immutable `TaskResult` carries task name, subtask seek positions, and success. The builder defaults seek positions to an empty map.

Control flow and integration: `ReconTaskControllerImpl` registers task instances, wraps calls in `NamedCallableTask`, records task status, retries failed delta processing with returned subtask positions, and calls staged `reprocess` during reinitialization.

State and persistence: the interface itself has no state. Implementations persist through Recon managers and report sequence advancement through `TaskResult` plus status updater calls.

Dependencies: OM metadata manager, Recon OM metadata manager, DB store, Java maps.

Risks and test signals: task names are identity keys in maps and status rows, so they must be stable and unique. Failure results should include seek positions for restartable subtasks. Tests for implementations should cover init idempotence, staged task construction, delta retry with seek map, and full reprocess success/failure status.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ReconOmTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ReconTaskConfig.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ReconTaskConfig.java

Purpose: `ReconTaskConfig` defines typed configuration for periodic Recon background tasks and warmup behavior under the `ozone.recon.task` config group.

Important APIs and types: HDDS `@ConfigGroup` and `@Config` annotations define `ozone.recon.task.pipelinesync.interval`, `missingcontainer.interval`, `safemode.wait.threshold`, and `containercounttask.interval`. Values are `Duration` with defaults of 300 seconds for pipeline sync, missing container, and safemode threshold, and 60 seconds for container size count.

Control flow and integration: Recon configuration injection can populate this POJO and task schedulers can read intervals via getters. Setters support tests and explicit programmatic overrides.

State and persistence: in-memory configuration only; durable values come from Ozone configuration files.

Dependencies: HDDS config annotations and Java `Duration`.

Risks and test signals: config key naming is partly redundant with the group prefix, so tests should verify effective key resolution. Duration parsing, default values, and setter/getter round trips should be covered. Operationally, too-small intervals can increase Recon load.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ReconTaskConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ReconTaskController.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ReconTaskController.java

Purpose: `ReconTaskController` is the public controller contract for registering Recon OM tasks, feeding OM deltas, managing async task execution, and triggering reinitialization after buffer overflow or task failures.

Important APIs and types: `registerTask`, `consumeOMEvents`, `reInitializeTasks`, `getRegisteredTasks`, `start`, and `stop` define normal lifecycle. `hasEventBufferOverflowed`, `hasTasksFailed`, `queueReInitializationEvent`, `updateOMMetadataManager`, and test-visible `getEventBufferSize` support the newer async buffer and checkpoint reinitialization path. `ReInitializationResult` distinguishes successful queueing, retryable timing/checkpoint failures, and max retries.

Control flow and integration: OM sync code calls `consumeOMEvents`; upgrade actions and recovery paths call `queueReInitializationEvent`; controller implementation dispatches to `ReconOmTask` instances and updates status tables.

State and persistence: interface has no state, but it defines operations that change event buffer state, task failure flags, checkpoints, staged Recon DBs, and task status rows.

Dependencies: `OMMetadataManager`, `ReconOMMetadataManager`, `ReconTaskReInitializationEvent`.

Risks and test signals: implementations must handle concurrent event ingestion, backpressure, failure flags, and lifecycle shutdown. Tests should assert return semantics for reinit queueing and that `consumeOMEvents` does not process synchronously after async buffering is introduced.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ReconTaskController.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ReconTaskControllerImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ReconTaskControllerImpl.java

Purpose: `ReconTaskControllerImpl` orchestrates registered `ReconOmTask` instances. It buffers OM delta batches, processes them asynchronously, retries failed task work, creates OM checkpoints for consistent reinitialization, swaps staged Recon DB state after full reprocess, updates task status rows, and reports controller and task metrics.

Important APIs and types: the constructor injects configuration, task set, task updater manager, Recon DB provider, Recon metadata managers, and initializes metrics and `OMUpdateEventBuffer`. `registerTask`, `start`, `stop`, `consumeOMEvents`, `reInitializeTasks`, `queueReInitializationEvent`, and `updateOMMetadataManager` implement the interface. Test-visible helpers expose buffer state, dropped batches, retry counters, failure flags, and checkpoint creation.

Control flow: `start` creates a fixed task executor and a single async event processor. `consumeOMEvents` offers non-empty batches unless task failure is blocking deltas; overflow drains the buffer and cleans checkpoints. The event loop polls the buffer and dispatches by `ReconEvent.EventType`. OM batches run all registered task `process` calls in futures, record task status, retry failed tasks once with subtask seek positions, and set `tasksFailed` if retry fails. Reinitialization queueing validates retry count/delay, drains stale events, creates an OM checkpoint, enqueues a `ReconTaskReInitializationEvent`, and resets flags on success. Reinitialization processes staged task instances in parallel, replaces the staged Recon DB on success, reinitializes managers, calls task `init`, and records final status and sequence.

State and persistence: important in-memory state includes task map, executors, running flag, failure flag, retry counters, event buffer, and current OM metadata manager. Durable effects include staged Recon DB replacement, task status table writes, global/container/namespace/file manager reinitialization, and checkpoint directories on disk.

Dependencies: Guava thread factory, Ozone configuration keys, Recon DB provider and metadata managers, metrics, `DBCheckpoint`, Commons IO file utilities, task wrappers and status updaters.

Risks and test signals: hard-coded overflow log capacity `20000` may diverge from configured capacity. `failedTasks` is a plain `ArrayList` mutated from multiple future callbacks, which is a concurrency risk. `queueReInitializationEvent` can return null if reinit event offer fails. Checkpoint cleanup depends on inferred DB parent paths. Tests should cover lifecycle shutdown, async dispatch, delta retry, failure flags blocking deltas, checkpoint creation failure retry timing, max retry fallback, staged DB swap failure, status rows, metrics, and checkpoint cleanup for drained control events.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ReconTaskControllerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ReconTaskReInitializationEvent.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ReconTaskReInitializationEvent.java

Purpose: `ReconTaskReInitializationEvent` is the control event used to request asynchronous full reinitialization of Recon OM tasks from a checkpointed OM metadata manager.

Important APIs and types: `ReInitializationReason` includes `BUFFER_OVERFLOW`, `TASK_FAILURES`, and `MANUAL_TRIGGER`. The constructor stores reason, current timestamp, and `ReconOMMetadataManager` checkpoint. Getters expose those values; `getEventType` returns `TASK_REINITIALIZATION`; `getEventCount` returns 1.

Control flow and integration: `ReconTaskControllerImpl.queueReInitializationEvent` creates this event after successful checkpoint creation and offers it to `OMUpdateEventBuffer`. The async processor calls `processReInitializationEvent`, which uses the checkpointed manager in try-with-resources and cleans checkpoint files afterward.

State and persistence: the event holds an in-memory reference to a checkpointed metadata manager backed by temporary checkpoint files. It does not write status itself.

Dependencies: `ReconOMMetadataManager`, `ReconEvent`.

Risks and test signals: because it owns resource-like state, discarded or drained events must close and clean their checkpoint managers. Tests should cover event type/count, timestamp creation, reason propagation, and cleanup paths when queued events are drained before processing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ReconTaskReInitializationEvent.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/package-info.java

Purpose: package documentation for `org.apache.hadoop.ozone.recon.tasks`.

Important APIs and types: declares package-level JavaDoc stating the package contains scheduled tasks used by Recon. It does not define runtime classes.

Control flow and integration: used by JavaDoc and package metadata only. It groups controller, task, event, and insight task classes.

State and persistence: none.

Dependencies: none.

Risks and test signals: no behavioral tests needed. Documentation should stay accurate as the package now includes async event buffering and upgrade-triggered reinitialization support, not only scheduled tasks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/types/NamedCallableTask.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/types/NamedCallableTask.java

Purpose: `NamedCallableTask` wraps a `Callable` with a stable task name so asynchronous execution failures can be attributed to the Recon task that failed.

Important APIs and types: constructor stores `taskName` and `Callable<V>`. `getTaskName()` exposes the name. `call()` delegates directly to the wrapped callable.

Control flow and integration: `ReconTaskControllerImpl` creates these wrappers for both delta `process` calls and reprocess calls. When exceptions occur, the controller wraps them in `TaskExecutionException` with the same name and updates metrics and status for that task.

State and persistence: only holds an in-memory name and callable. Persistence is handled by controller status updates.

Dependencies: Java `Callable`.

Risks and test signals: null task names or callables are not checked. Tests should verify delegation, name retention, and exception propagation without swallowing checked exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/types/NamedCallableTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/types/TaskExecutionException.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/types/TaskExecutionException.java

Purpose: `TaskExecutionException` is a runtime wrapper that associates an exception thrown during async task execution with a Recon task name.

Important APIs and types: constructor accepts `taskName` and cause, passes the cause to `RuntimeException`, and stores the task name. `getTaskName()` returns it.

Control flow and integration: `ReconTaskControllerImpl` throws this wrapper inside `CompletableFuture` suppliers when task calls fail. Exception handlers inspect the cause, extract task name, increment metrics, log context, and update task status.

State and persistence: no durable state; it carries in-memory exception metadata.

Dependencies: Java runtime exceptions.

Risks and test signals: the wrapper uses `super(cause)` rather than a message, so logs rely on cause and separate task-name logging. Tests should cover task-name extraction and cause preservation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/types/TaskExecutionException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/types/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/types/package-info.java

Purpose: package documentation for task tracking helper types.

Important APIs and types: describes wrapper classes for better task tracking. The direct classes are `NamedCallableTask` and `TaskExecutionException`.

Control flow and integration: JavaDoc-only metadata for helpers used by `ReconTaskControllerImpl`.

State and persistence: none.

Dependencies: none.

Risks and test signals: no runtime tests needed. Documentation could be updated if additional async execution helper types are added.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/types/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/updater/ReconTaskStatusUpdater.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/updater/ReconTaskStatusUpdater.java

Purpose: `ReconTaskStatusUpdater` is a small mutable facade over the generated jOOQ `ReconTaskStatusDao` and POJO. It records task run starts, completions, sequence numbers, and status flags in the `RECON_TASK_STATUS` table.

Important APIs and types: constructors create an updater from a DAO and task name or from an existing `ReconTaskStatus` row. Setters update task name, last sequence, timestamp, last run status, and current-running flag. `recordRunStart()` sets running true and timestamp, then writes. `recordRunCompletion()` sets running false and timestamp, then writes. `updateDetails()` inserts if missing or updates if present.

Control flow and integration: `ReconTaskControllerImpl` obtains updaters from `ReconTaskStatusUpdaterManager` before and after delta and reprocess execution. Upgrade-aware manager construction avoids schema access before columns exist.

State and persistence: holds a mutable POJO snapshot and writes it to the SQL Recon task status table.

Dependencies: generated jOOQ DAO/POJO, `DataAccessException`, SLF4J.

Risks and test signals: errors in start/completion logging are swallowed after logging, so task execution may continue with stale status. `updateDetails()` has insert/update race potential if multiple updaters for same name exist. Tests should cover insert, update, run start/completion fields, sequence update, and DAO exception handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/updater/ReconTaskStatusUpdater.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/updater/ReconTaskStatusUpdaterManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/updater/ReconTaskStatusUpdaterManager.java

Purpose: `ReconTaskStatusUpdaterManager` is a singleton cache and lazy loader for `ReconTaskStatusUpdater` instances. It avoids reading task status rows during Guice injection, which matters during schema upgrades.

Important APIs and types: constructor receives `ReconTaskStatusDao` and initializes a `ConcurrentHashMap`. `getTaskStatusUpdater(taskName)` calls `ensureInitialized()` and then `computeIfAbsent`. `ensureInitialized()` double-checks an `AtomicBoolean`, uses jOOQ DSL to inspect schema, loads either full rows or base columns, and populates the cache. `columnExists` checks Derby system catalogs for upgrade columns.

Control flow and integration: the controller requests updaters during task lifecycle. Before the `TASK_STATUS_STATISTICS` upgrade is finalized, the manager can query only old columns and defaults new fields to zero.

State and persistence: cache state is in memory. Persistent data lives in `RECON_TASK_STATUS`.

Dependencies: Guice singleton, jOOQ DAO/DSL, generated `ReconTaskStatus`, Derby system catalog naming.

Risks and test signals: `initialized` is only set on successful load, so transient DB errors retry on later access. Column detection is Derby-specific. Tests should cover pre-upgrade schema, upgraded schema, retry after load failure, concurrent first access, and creation of new updater rows.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/updater/ReconTaskStatusUpdaterManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/updater/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/updater/package-info.java

Purpose: package documentation for task status update utilities.

Important APIs and types: describes utilities that update task status. The concrete classes are the updater and updater manager.

Control flow and integration: JavaDoc-only metadata for SQL task status persistence helpers.

State and persistence: none in this file.

Dependencies: none.

Risks and test signals: no runtime tests needed. The description remains valid as the package now handles lazy initialization for upgrade compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/updater/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/util/ParallelTableIteratorOperation.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/util/ParallelTableIteratorOperation.java

Purpose: `ParallelTableIteratorOperation` parallelizes RocksDB table scanning by deriving key-range bounds from SST metadata, running bounded iterator tasks, and handing batches to worker tasks.

Important APIs and types: the constructor accepts metadata manager, table, key codec, iterator and worker counts, max values in memory, and log threshold. `performTaskOnTableVals(taskName, startKey, endKey, Function<KeyValue<K,V>,Void>)` executes the scan. `close()` shuts down iterator and worker executors.

Control flow: `getBounds` attempts to read RocksDB live SST file metadata from `RDBStore`, filters by column family name, decodes smallest and largest keys, adds optional start/end keys, sorts, and filters. If fewer than two bounds exist, the operation falls back to a single table iterator with optional seek/end stop. Otherwise, it submits one iterator task per adjacent bound pair. Iterator tasks collect key-value batches up to `maxNumberOfVals`, throttle pending worker futures, and submit worker tasks that apply the caller function and update progress counters. The method waits for all iterator and worker futures before returning.

State and persistence: no durable writes. State is executor queues, future queues, decoded bounds, and counters. The caller's function may persist results.

Dependencies: HDDS `Table`, `TableIterator`, `Codec`, `RDBStore`, OM metadata manager, RocksDB `LiveFileMetaData`, Java executors.

Risks and test signals: executor queues are unbounded even though future throttling limits submitted backlog. Bound handling can double-process boundary keys if SST ranges overlap or duplicated bounds are present. `waitForQueueSize` propagates worker failures through future `get`. Tests should cover fallback path, start/end ranges, SST-bound segmentation, duplicate bounds, interruption, worker exception propagation, and executor shutdown.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/util/ParallelTableIteratorOperation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/util/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/util/package-info.java

Purpose: package documentation for Recon task utility classes.

Important APIs and types: describes the utility package. The direct utility in this shard is `ParallelTableIteratorOperation`.

Control flow and integration: JavaDoc-only metadata.

State and persistence: none.

Dependencies: none.

Risks and test signals: no behavioral tests needed. Documentation should stay aligned if more utilities are added.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/util/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/InitialConstraintUpgradeAction.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/InitialConstraintUpgradeAction.java

Purpose: `InitialConstraintUpgradeAction` is the upgrade action for the initial Recon layout feature. It repairs the `UNHEALTHY_CONTAINERS` table check constraint so it includes all current `UnHealthyContainerStates` enum values.

Important APIs and types: annotated with `@UpgradeActionRecon(feature = INITIAL_VERSION)`. `execute(DataSource)` gets a connection, skips work if the unhealthy container table does not exist, builds a jOOQ DSL context, drops the existing `<table>ck1` constraint, and adds a new constraint over `container_state`.

Control flow and integration: `ReconLayoutFeature.registerUpgradeActions()` discovers the annotation, and `ReconLayoutVersionManager.finalizeLayoutFeatures()` executes it when MLV is below the feature version.

State and persistence: modifies SQL schema constraints in the Recon DB. It does not change data rows.

Dependencies: Recon container schema constants, SQL table existence helper, jOOQ DSL, DataSource, SLF4J.

Risks and test signals: dropping a constraint that does not exist may fail. The action assumes the constraint name convention. Tests should cover table missing, constraint replacement, enum value coverage, and SQL exception wrapping. It exposes a test setter for DSL context.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/InitialConstraintUpgradeAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/NSSummaryAggregatedTotalsUpgrade.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/NSSummaryAggregatedTotalsUpgrade.java

Purpose: `NSSummaryAggregatedTotalsUpgrade` is an upgrade action that triggers asynchronous rebuild of the namespace summary tree when aggregated totals are introduced.

Important APIs and types: annotated for `ReconLayoutFeature.NSSUMMARY_AGGREGATED_TOTALS`. `execute(DataSource)` obtains the global Guice injector from `ReconGuiceServletContextListener`, retrieves `ReconTaskController`, and queues a manual reinitialization event.

Control flow and integration: layout finalization invokes this action. The controller's reinitialization path rebuilds tasks against a checkpoint and staged Recon DB. The action logs an error if queueing does not return `SUCCESS`, but does not throw for non-success results.

State and persistence: no direct DB writes through the provided `DataSource`; persistence happens indirectly when reinitialization tasks rebuild Recon state.

Dependencies: global Guice injector, `ReconTaskController`, `ReconTaskReInitializationEvent`.

Risks and test signals: relying on a global injector makes this action startup-order sensitive. Non-success queue result only logs, so finalization may advance even if rebuild is deferred. Tests should cover missing injector, controller lookup, success queueing, and non-success logging behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/NSSummaryAggregatedTotalsUpgrade.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/ReconLayoutFeature.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/ReconLayoutFeature.java

Purpose: `ReconLayoutFeature` enumerates Recon metadata layout versions and binds optional upgrade actions to each feature.

Important APIs and types: features currently include versions 0 through 5: initial layout, task status statistics, unhealthy container replica mismatch, NSSummary aggregated totals, replicated file sizes, and unhealthy container state/container id index. Each enum stores version, description, and optional `ReconUpgradeAction`. `addAction` keeps the first action. `registerUpgradeActions` scans `org.apache.hadoop.ozone.recon.upgrade` for `@UpgradeActionRecon`, instantiates actions, and attaches them. `determineSLV` returns the max feature version.

Control flow and integration: `ReconLayoutVersionManager` calls `registerUpgradeActions` at construction and later finalizes features with version greater than current MLV.

State and persistence: action references are stored in enum instances for the JVM process. Version persistence is handled by schema version table manager elsewhere.

Dependencies: Reflections library and the local upgrade action annotation/interface.

Risks and test signals: reflection registration can fail at runtime if action constructors change. Duplicate actions for a feature are silently ignored after the first. Tests should cover action registration, SLV computation, duplicate behavior, and ordering by version in the manager.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/ReconLayoutFeature.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/ReconLayoutVersionManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/ReconLayoutVersionManager.java

Purpose: `ReconLayoutVersionManager` determines Recon's metadata layout version, compares it with software layout version, and finalizes pending layout features during startup.

Important APIs and types: constructor receives `ReconSchemaVersionTableManager`, `ReconContext`, and `DataSource`, reads current MLV, and registers upgrade actions. `finalizeLayoutFeatures()` finds features with version greater than MLV, opens a transaction, updates schema version, executes feature action if present, commits per feature, and rolls back on failure. `getRegisteredFeatures`, `getCurrentMLV`, and `getCurrentSLV` expose state.

Control flow and integration: startup code creates this manager and calls finalization. On failure, it updates Recon context errors with `UPGRADE_FAILURE`, marks health false, and throws a runtime exception to halt startup.

State and persistence: `currentMLV` is cached in memory and persisted through `ReconSchemaVersionTableManager.updateSchemaVersion`. Upgrade actions mutate schema or trigger rebuilds.

Dependencies: SQL connection and data source, Recon context, schema version manager, `ReconLayoutFeature`.

Risks and test signals: schema version is updated before action execution within the transaction connection, but actions receive `DataSource` and may use separate connections, which can weaken transaction assumptions. Features without actions are logged but their versions are not advanced because update occurs only inside `action.isPresent()`. Tests should cover feature ordering, rollback behavior, context health update, no-action version behavior, and action failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/ReconLayoutVersionManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/ReconTaskStatusTableUpgradeAction.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/ReconTaskStatusTableUpgradeAction.java

Purpose: `ReconTaskStatusTableUpgradeAction` adds task status tracking columns to `RECON_TASK_STATUS` for the task status statistics feature.

Important APIs and types: annotated for `TASK_STATUS_STATISTICS`. `execute(DataSource)` skips missing tables, adds nullable integer columns `last_task_run_status` and `is_current_task_running`, updates existing rows to zero, then sets both columns not null. Helpers perform add-column and set-not-null operations with jOOQ.

Control flow and integration: discovered by `ReconLayoutFeature` and run by `ReconLayoutVersionManager`. `ReconTaskStatusUpdaterManager` has compatibility logic to read old rows before this action runs.

State and persistence: changes SQL schema and initializes column values on existing rows.

Dependencies: generated schema constants, table existence helper, jOOQ DSL and SQL types, Recon task schema definition.

Risks and test signals: the catch block logs `SQLException` or `DataAccessException` but does not rethrow, which may let layout finalization commit despite failed schema migration. Existing columns are not checked, so reruns can fail. Tests should cover missing table, happy path, row defaults, not-null constraints, existing-column behavior, and exception propagation expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/ReconTaskStatusTableUpgradeAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/ReconUpgradeAction.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/ReconUpgradeAction.java

Purpose: `ReconUpgradeAction` is the single-method interface for code that runs during Recon layout feature finalization.

Important APIs and types: `execute(DataSource source) throws Exception` gives actions access to the Recon SQL datasource and lets them throw failures to the layout manager.

Control flow and integration: action classes are annotated with `@UpgradeActionRecon`; `ReconLayoutFeature.registerUpgradeActions` instantiates them; `ReconLayoutVersionManager.finalizeLayoutFeatures` invokes `execute`.

State and persistence: no state in the interface. Implementations may alter SQL schema, update data, or trigger controller rebuilds.

Dependencies: `javax.sql.DataSource`.

Risks and test signals: implementations need clear transaction expectations because the manager also manages a connection. Tests should assert that failing actions propagate exceptions unless an implementation deliberately logs and suppresses them.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/ReconUpgradeAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/ReplicatedSizeOfFilesUpgradeAction.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/ReplicatedSizeOfFilesUpgradeAction.java

Purpose: `ReplicatedSizeOfFilesUpgradeAction` triggers a full NSSummary rebuild when the namespace summary model gains replicated file size totals.

Important APIs and types: annotated for `REPLICATED_SIZE_OF_FILES`. `execute(DataSource)` retrieves the global Guice injector, obtains `ReconTaskController`, queues a manual reinitialization event, and throws if queueing is not successful.

Control flow and integration: layout finalization runs this action after the corresponding feature version becomes pending. Reinitialization is performed asynchronously by the controller but this action treats failure to queue as fatal.

State and persistence: no direct SQL mutation. The durable effect is indirect: Recon tasks rebuild namespace summary state after the queued event is processed.

Dependencies: global Guice injector, `ReconTaskController`, `ReconTaskReInitializationEvent`, SLF4J.

Risks and test signals: success only confirms queueing, not rebuild completion. Missing injector or retry-later result fails the upgrade. Tests should cover missing injector, queue success, queue retry/failure, and thrown runtime wrapper.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/ReplicatedSizeOfFilesUpgradeAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/UnhealthyContainerReplicaMismatchAction.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/UnhealthyContainerReplicaMismatchAction.java

Purpose: `UnhealthyContainerReplicaMismatchAction` updates the unhealthy container state check constraint when the replica mismatch state is added.

Important APIs and types: annotated for `UNHEALTHY_CONTAINER_REPLICA_MISMATCH`. `execute(DataSource)` checks table existence, creates a DSL context, drops `<UNHEALTHY_CONTAINERS>ck1`, and adds a new check constraint with all enum names from `ContainerSchemaDefinition.UnHealthyContainerStates`.

Control flow and integration: invoked by layout feature finalization after reflection registration.

State and persistence: mutates SQL schema constraints in Recon DB. No data rows are changed.

Dependencies: container schema definition, SQL table existence helper, jOOQ DSL, DataSource.

Risks and test signals: same name assumptions as `InitialConstraintUpgradeAction`; repeated execution or missing constraint can fail. Tests should cover constraint replacement, missing table skip, enum coverage, and exception wrapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/UnhealthyContainerReplicaMismatchAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/UnhealthyContainersStateContainerIdIndexUpgradeAction.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/UnhealthyContainersStateContainerIdIndexUpgradeAction.java

Purpose: this upgrade action ensures the `idx_state_container_id` index exists on `UNHEALTHY_CONTAINERS` for efficient state and container id lookups after the related layout feature.

Important APIs and types: annotated for `UNHEALTHY_CONTAINERS_STATE_CONTAINER_ID_INDEX`. `execute(DataSource)` checks table existence, checks index existence through `DatabaseMetaData.getIndexInfo`, and creates the index on `container_state` and `container_id` with jOOQ if absent.

Control flow and integration: discovered and run by the layout manager for feature version 5.

State and persistence: creates a SQL index in the Recon DB. It is idempotent if metadata lookup finds the index.

Dependencies: JDBC `DatabaseMetaData`, jOOQ DSL, container schema constants, table existence helper.

Risks and test signals: index lookup depends on DB metadata casing and table name matching. Tests should cover missing table, existing index case-insensitively, index creation, SQL exception wrapping, and query plans or repository methods that rely on the new index.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/UnhealthyContainersStateContainerIdIndexUpgradeAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/UpgradeActionRecon.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/UpgradeActionRecon.java

Purpose: `UpgradeActionRecon` is the runtime annotation used to associate a `ReconUpgradeAction` implementation with a `ReconLayoutFeature`.

Important APIs and types: retained at runtime and targeted at types. Its single element `feature()` returns the layout feature the annotated action should finalize.

Control flow and integration: `ReconLayoutFeature.registerUpgradeActions` scans the upgrade package for annotated classes, constructs them, reads the annotation, and attaches the action to the feature.

State and persistence: no runtime state beyond annotation metadata.

Dependencies: Java annotation APIs and `ReconLayoutFeature`.

Risks and test signals: action classes must have no-arg constructors for reflection. Tests should cover annotation discovery and feature binding.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/UpgradeActionRecon.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/package-info.java

Purpose: package documentation for Recon upgrade action infrastructure.

Important APIs and types: describes `ReconUpgradeAction` and upgrade actions that run automatically during startup to apply schema or layout changes.

Control flow and integration: JavaDoc-only metadata for the upgrade package.

State and persistence: none.

Dependencies: references the local upgrade action interface.

Risks and test signals: no behavioral tests needed. Documentation should remain accurate as action discovery is annotation/reflection based.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/chatbot/recon-api.yaml -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/chatbot/recon-api.yaml

Purpose: `recon-api.yaml` is the OpenAPI 3.0 contract used by the Recon chatbot/resource layer to describe the Ozone Recon REST API. It documents endpoint paths, query parameters, operation ids, response schemas, and sample payloads for containers, keys, namespace metadata, cluster state, datanodes, pipelines, tasks, utilization, and metrics.

Important APIs and types: top-level server URL is `/api/v1/`. Tags group endpoints by domain. Major paths include `/containers`, `/containers/deleted`, `/containers/missing`, `/containers/unhealthy`, `/containers/mismatch`, `/volumes`, `/buckets`, `/keys/open`, `/keys/deletePending`, `/keys/listKeys`, `/containers/{id}/keys`, `/blocks/deletePending`, `/namespace/summary`, `/namespace/usage`, `/namespace/quota`, `/namespace/dist`, `/clusterState`, `/datanodes`, `/datanodes/remove`, `/pipelines`, `/task/status`, `/utilization/fileCount`, `/utilization/containerCount`, and `/metrics/query`. Components define schemas such as `ContainerMetadata`, `DeletedContainers`, `OpenKeys`, `ListKeysResponse`, `DeletePendingKeys`, `NamespaceMetadataResponse`, `MetadataDiskUsage`, `ClusterState`, `DatanodesSummary`, `PipelinesSummary`, `TasksStatus`, and `MetricsQuery`.

Control flow and integration: this file is declarative. Generated clients, chatbot tooling, documentation, or validation layers can use `operationId` values to map user intents or API calls to Recon endpoints. It mirrors server-side resources elsewhere in Recon and should evolve with REST resource signatures.

State and persistence: no runtime state. It describes persisted/derived Recon data returned by REST resources, including OM metadata, SCM state, Recon SQL tables, and Prometheus proxy output.

Dependencies: OpenAPI 3.0 tooling and JSON schema consumers.

Risks and test signals: several schema examples and field names should be linted, including odd example keys such as `isKey"` in `MetadataDiskUsage`, nested `ClusterStorageReport` indentation under `DataNodeStorageReport`, and inconsistent integer/string typing for prefix parameters. Contract tests should validate the YAML, compare documented paths with JAX-RS resources, and exercise pagination, filtering, and error responses for 400 and 503 cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/chatbot/recon-api.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/WEB-INF/web.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/WEB-INF/web.xml

Purpose: `web.xml` configures the Recon web application servlet container integration.

Important APIs and types: declares Servlet 3.0 web-app metadata, registers `org.apache.hadoop.ozone.recon.ReconGuiceServletContextListener`, maps `com.google.inject.servlet.GuiceFilter` to all URLs, and adds a `woff2` MIME mapping for web font delivery.

Control flow and integration: when the webapp starts, the Guice servlet context listener initializes Recon dependency injection and REST/UI bindings. All requests pass through GuiceFilter, which routes configured servlets/resources. Static assets under the Recon webapp rely on MIME mappings for correct browser behavior.

State and persistence: no application state in this file. It influences runtime startup and request routing.

Dependencies: Java Servlet API and Guice Servlet.

Risks and test signals: startup tests should verify listener initialization, Guice filter mapping, and static asset MIME delivery. A broken listener class or filter mapping can prevent the REST API and UI from serving.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/WEB-INF/web.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/.eslintrc.json -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/.eslintrc.json

Purpose: `.eslintrc.json` defines linting rules for the Recon React/TypeScript web UI.

Important APIs and types: it extends recommended ESLint, React, TypeScript, import, and Prettier configs. Plugins include `react`, `@typescript-eslint`, `prettier`, `import`, and `promise`. Rules set quote style to single quotes, two-space indentation, object spacing, unused variable handling, import dependency checks, several React rule relaxations, and TypeScript unused variable ignores for names starting with underscore. Settings configure TypeScript parser/resolver, Node extension resolution, React version detection, and browser/node/es6 environments.

Control flow and integration: frontend build, CI, or developer lint commands load this configuration to enforce consistent style and catch likely errors in the web UI.

State and persistence: no runtime state. It affects source validation before bundling or committing.

Dependencies: ESLint core plus React, TypeScript ESLint, import, promise, and Prettier plugins.

Risks and test signals: comments before JSON rely on JSONC-compatible ESLint config parsing. `import/no-unused-modules` can be noisy in code-splitting or test-only exports. CI should run lint after dependency upgrades, and rule compatibility should be checked when ESLint major versions change.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/.eslintrc.json -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/.prettierrc.js -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/.prettierrc.js

Purpose: `.prettierrc.js` exports the Prettier formatting configuration for the Recon web UI.

Important APIs and types: the default export config sets semicolons on, tab width 2, print width 100, single quotes, JSX single quotes, bracket spacing, and trailing commas for ES5-compatible locations.

Control flow and integration: Prettier and ESLint's Prettier integration consume this config during formatting and linting. It complements `.eslintrc.json` by making formatting deterministic for TypeScript, JavaScript, JSX, and TSX files.

State and persistence: no runtime state. It changes source formatting output.

Dependencies: Prettier with a runtime capable of loading ES module style `export default`, depending on the project's Prettier version and module configuration.

Risks and test signals: older Prettier or CommonJS-only tooling may expect `module.exports` instead of `export default`. CI formatting checks should verify the config loads in the actual frontend toolchain.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/.prettierrc.js -->
