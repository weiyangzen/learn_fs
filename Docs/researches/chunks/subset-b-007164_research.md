# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.7.2.xml lines 30558-32555

## Scope

This chunk is the final chunk of the JDiff API snapshot for Apache Hadoop Common 2.7.2. It starts inside the tail of `org.apache.hadoop.service.AbstractService`, completes the `org.apache.hadoop.service` package, covers `org.apache.hadoop.tracing`, covers a set of public `org.apache.hadoop.util` helpers, covers most visible `org.apache.hadoop.util.bloom` filter APIs, then closes with empty package entries for `org.apache.hadoop.util.curator` and `org.apache.hadoop.util.hash`.

The source is generated API metadata, not executable Java source. The useful research surface is therefore the compatibility contract exposed by the XML: public/protected classes, interfaces, constructors, methods, fields, inheritance, implemented interfaces, checked exceptions, synchronization/finality markers, deprecation markers, and embedded Javadoc. Runtime implementation details are inferred only from signatures and documentation visible in this chunk.

## Purpose

This slice captures three main Hadoop Common API areas:

- Service lifecycle support: `Service`, `AbstractService`, `CompositeService`, lifecycle history events, state-change listeners, state transition validation, and helper methods for stopping services safely.
- Operational utilities: trace span receiver administration, application classloader isolation, progress callbacks, Java checksum implementations, reflection and writable-copy helpers, string interning, and the `Tool`/`ToolRunner` command-line contract.
- Probabilistic membership structures: Bloom filters, counting Bloom filters, dynamic Bloom filters, retouched Bloom filters, hash fanout helpers, and remove-scheme constants.

Because this is a JDiff baseline under `dev-support/jdiff`, its repository role is release compatibility checking for Hadoop Common 2.7.2. Any method or field in this XML is part of the documented API baseline that later releases can be compared against.

## Important APIs, Types, and Functions

### Service Lifecycle

- `AbstractService` is already open when the chunk starts. The visible tail includes protected lifecycle hooks `serviceInit(Configuration)`, `serviceStart()`, and `serviceStop()`, plus listener registration, static global listener registration, service metadata accessors, blocker management, and state predicates.
- `AbstractService.serviceInit(Configuration)` is documented as the one-time initialization hook. It can update the service configuration if a subclass created a replacement configuration instance. Exceptions are caught/wrapped by the outer lifecycle operation and can trigger service stop.
- `AbstractService.serviceStart()` is the one-time INITED-to-STARTED hook. Exceptions are caught/wrapped and trigger a stop.
- `AbstractService.serviceStop()` is the one-time transition-to-STOPPED hook. The Javadoc explicitly requires robust shutdown logic that tolerates null fields and continues cleanup after an earlier shutdown failure.
- `AbstractService.registerServiceListener(ServiceStateChangeListener)` and `unregisterServiceListener(...)` manage per-service callbacks. `registerGlobalListener(...)` and `unregisterGlobalListener(...)` expose JVM-wide callbacks for all service state changes.
- `AbstractService.getName()`, synchronized `getConfig()`, `getStartTime()`, synchronized `getLifecycleHistory()`, final `isInState(Service.STATE)`, and `toString()` expose state/identity. `putBlocker(String, String)`, `removeBlocker(String)`, and `getBlockers()` expose live-service blocker diagnostics.
- `CompositeService` extends `AbstractService` and manages child `Service` instances. Its public constructor takes a name. `getServices()` returns a cloned snapshot list; `addService(Service)`, `addIfService(Object)`, and synchronized `removeService(Service)` manage children; `serviceInit`, `serviceStart`, and `serviceStop` cascade lifecycle operations to children.
- `CompositeService.STOP_ONLY_STARTED_SERVICES` is a protected static final shutdown policy flag. The field documentation states the tradeoff between stopping everything and stopping only started services, and notes that children failing during init/start still get `stop()` called.
- `LifecycleEvent` is `Serializable` and carries public mutable fields `time` and `state`, representing a timestamp and the state entered.
- `LoggingStateChangeListener` implements `ServiceStateChangeListener`, has constructors for a supplied Commons Logging `Log` or a default static log, and logs `stateChanged(Service)` callbacks at INFO level.
- `Service` is a public interface extending `Closeable`. It defines the lifecycle contract: `init(Configuration)`, `start()`, `stop()`, `close()`, listener registration, `getName()`, `getConfig()`, `getServiceState()`, `getStartTime()`, `isInState(STATE)`, `getFailureCause()`, `getFailureState()`, `waitForServiceToStop(long)`, `getLifecycleHistory()`, and `getBlockers()`.
- `Service.init(Configuration)` must transition NOTINITED to INITED unless it fails; on failure `stop()` must be invoked and the state becomes STOPPED. `Service.start()` similarly requires INITED to STARTED, with failure driving stop/STOPPED. `Service.stop()` must be a no-op when already STOPPED and best-effort otherwise.
- `Service.close()` is specified as Java 7 close-clause friendly and must relay directly to `stop()`. It declares `IOException`, but the Javadoc says it never throws an `IOException`.
- `Service.waitForServiceToStop(long)` blocks until service stop actions have executed or timeout expires. A timeout of zero means wait forever, and it may be called before init/start to avoid races with fast stops.
- `ServiceOperations` is a final helper class with static `stop(Service)` and `stopQuietly(Service)` / `stopQuietly(Log, Service)` methods. It centralizes null-safe and exception-swallowing service cleanup.
- `ServiceStateChangeListener` defines `stateChanged(Service)`. Its Javadoc is important: callbacks run on the thread that initiated the state change while the service is in a synchronized section, so long-running callbacks and reentrant service calls can delay or deadlock lifecycle transitions.
- `ServiceStateException` extends `RuntimeException`, has constructors for message/cause combinations, and static `convert(Throwable)` / `convert(String, Throwable)` methods that preserve existing runtime exceptions or wrap other throwables as service-state failures.
- `ServiceStateModel` tracks and validates a service's current `Service.STATE`. It has constructors for NOTINITED or an explicit initial state, `getState()`, `isInState(STATE)`, `ensureCurrentState(STATE)`, synchronized `enterState(STATE)`, static `checkStateTransition(String, STATE, STATE)`, static `isValidStateTransition(STATE, STATE)`, and `toString()`.

### Tracing Administration

- `org.apache.hadoop.tools.protocolPB` appears as an empty package in this chunk.
- `SpanReceiverInfo` exposes `getId()` and `getClassName()`, representing active trace span receiver metadata.
- `SpanReceiverInfoBuilder` constructs span receiver descriptions from a class name. `addConfigurationPair(String, String)` adds configuration to the pending receiver description, and `build()` returns a `SpanReceiverInfo`.
- `TraceAdminProtocol` is the non-PB tracing admin interface. It exposes `listSpanReceivers()`, `addSpanReceiver(SpanReceiverInfo)`, and `removeSpanReceiver(long)`, all throwing `IOException`, plus a public static final `versionID` field.
- `TraceAdminProtocolPB` extends generated `TraceAdminPB.TraceAdminService.BlockingInterface` and Hadoop IPC `VersionedProtocol`, making the same administrative surface available via protobuf-backed RPC.

### General Utilities

- `ApplicationClassLoader` extends `URLClassLoader`. It has constructors from `URL[]` or a classpath string, parent classloader, and system-class pattern list. It overrides `getResource(String)`, public `loadClass(String)`, and synchronized protected `loadClass(String, boolean)`.
- `ApplicationClassLoader.isSystemClass(String, List)` checks whether a class/resource should be loaded by the system/parent side based on positive and negative system class patterns. `SYSTEM_CLASSES_DEFAULT` documents the default parent-loaded set, including JDK classes, Hadoop classes/resources, and selected third-party classes.
- `IPList` is a small predicate interface with `isIn(String ipAddress)`.
- `Progressable` defines `progress()`, the callback used by long-running operations to report liveness to the Hadoop framework and avoid timeout assumptions.
- `PureJavaCrc32` implements `java.util.zip.Checksum` with constructor, `getValue()`, `reset()`, `update(byte[], int, int)`, and final `update(int)`. Its documentation says it uses the same polynomial as native `java.util.zip.CRC32` and avoids JNI overhead for many small checksums.
- `PureJavaCrc32C` also implements `Checksum`, with the same visible operations, but uses the CRC32-C polynomial used by iSCSI and hardware support on some Intel chipsets.
- `ReflectionUtils` exposes configuration, instantiation, thread-info, writable-copy, and inherited-member helpers. Important methods include `setConf(Object, Configuration)`, generic `newInstance(Class, Configuration)`, `setContentionTracing(boolean)`, synchronized `printThreadInfo(PrintStream, String)`, `logThreadInfo(Log, String, long)`, generic `getClass(T)`, generic `copy(Configuration, T src, T dst)`, `cloneWritableInto(Writable, Writable)`, `getDeclaredFieldsIncludingInherited(Class)`, and `getDeclaredMethodsIncludingInherited(Class)`.
- `StringInterner` exposes static `strongIntern(String)` and `weakIntern(String)`. The documentation emphasizes reducing permanent-generation pressure versus direct `String.intern()` by using strong or weak representative references.
- `Tool` extends `Configurable` and defines `run(String[]) throws Exception`. The long embedded example documents the standard pattern of letting `ToolRunner` handle generic Hadoop command-line options, then using the resulting `Configuration` for application-specific setup.
- `ToolRunner` has static `run(Configuration, Tool, String[])`, `run(Tool, String[])`, `printGenericCommandUsage(PrintStream)`, and `confirmPrompt(String)`. It integrates `Tool` with generic option parsing and configuration mutation before invoking `Tool.run(...)`.

### Bloom Filter Utilities

- `BloomFilter` extends `Filter`. It has a zero-argument constructor for `readFields`, a constructor `(int vectorSize, int nbHash, int hashType)`, and operations `add(Key)`, `and(Filter)`, `membershipTest(Key)`, `not()`, `or(Filter)`, `xor(Filter)`, `toString()`, `getVectorSize()`, `write(DataOutput)`, and `readFields(DataInput)`.
- `CountingBloomFilter` is final and extends `Filter`. It adds `delete(Key)` and `approximateCount(Key)` to the same add/membership/boolean-combination/serialization surface. Its Javadoc states count storage is limited by bucket size, with overflow after repeated inserts around 15 and possible underflow after deletes.
- `DynamicBloomFilter` extends `Filter` and has constructors for serialization and `(vectorSize, nbHash, hashType, nr)`. It grows by adding Bloom-filter rows when the active row reaches the configured threshold `nr`. It exposes the same add, logical combination, membership, string, and Writable methods.
- `HashFunction` is a final helper. Its constructor accepts a maximum value, number of hash results, and hash type. `clear()` is a no-op, and `hash(Key)` returns an `int[]` of hash positions.
- `RemoveScheme` is an interface used as a constant holder for retouched Bloom filters. Public static final short constants are `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`, each documenting a different selective-clearing heuristic.
- `RetouchedBloomFilter` is final, extends `BloomFilter`, and implements `RemoveScheme`. It has constructors for serialization and `(vectorSize, nbHash, hashType)`, overrides/extends `add(Key)`, has overloads of `addFalsePositive(...)` for one `Key`, `Collection`, `List`, and `Key[]`, exposes `selectiveClearing(Key, short)`, and implements `write(DataOutput)` / `readFields(DataInput)`.
- Empty package nodes for `org.apache.hadoop.util.curator` and `org.apache.hadoop.util.hash` close the file. In this chunk, `org.apache.hadoop.util.hash` has no class declarations even though Bloom constructors reference `org.apache.hadoop.util.hash.Hash`; the referenced hash APIs must be in an earlier chunk or absent from this JDiff slice.

## Control Flow

The XML itself has no executable control flow, but it documents several important flows:

- Service lifecycle flow starts at `Service.init(Configuration)`, transitions from NOTINITED to INITED, then `start()` transitions from INITED to STARTED, and `stop()` transitions to STOPPED. Failures during init/start must trigger stop and capture failure state/cause.
- `AbstractService` implements the template-method structure around subclass hooks. Public lifecycle methods in earlier parts of the class call protected `serviceInit`, `serviceStart`, and `serviceStop` once per instance; these hooks do not need their own synchronization because the outer lifecycle methods prevent re-entry.
- Composite lifecycle flow is parent-driven. `CompositeService.serviceInit`, `serviceStart`, and `serviceStop` apply lifecycle operations to a snapshot/list of child services. Shutdown policy is governed by `STOP_ONLY_STARTED_SERVICES`, but failed children during init/start still receive `stop()`.
- Listener flow is synchronous with state transition. A service state change first changes the service state, then invokes registered listeners and global listeners on the initiating thread while the service is synchronized. Logging listeners simply record the change.
- Service stop helper flow is defensive. `ServiceOperations.stop(Service)` checks for null and state before stopping, while `stopQuietly` catches and logs exceptions for cleanup paths.
- State model flow centralizes transition validation. Callers query `getState`/`isInState`, assert with `ensureCurrentState`, then call synchronized `enterState` to atomically validate and store a proposed state. Static helpers expose validation without mutating an instance.
- Tracing admin flow lists existing span receivers, builds a `SpanReceiverInfo` with configuration pairs, sends it through `TraceAdminProtocol.addSpanReceiver`, and later removes it by id. The PB interface is the IPC transport boundary for the same operations.
- Application classloading flow checks `isSystemClass` patterns before deciding whether parent/system loading should win or whether application URLs should be consulted first. This supports isolation while preserving Hadoop/JDK/shared classes.
- Tool execution flow wraps application logic with generic Hadoop option parsing. `ToolRunner.run` sets the possibly modified `Configuration` onto the `Tool`, then invokes `Tool.run(String[])`; callers use the integer return code as the process status.
- Checksum flow follows the `Checksum` interface: repeated `update(...)` calls mutate an internal CRC state, `getValue()` reads it, and `reset()` clears it.
- Reflection copy flow serializes a `Writable` source into a buffer and deserializes into the destination, destroying prior destination contents. `cloneWritableInto` performs the same style of mutable target update.
- Bloom filter flow hashes a `Key` to multiple vector positions with `HashFunction`, mutates internal vectors/counters on `add`, and answers `membershipTest` by checking whether the necessary positions are set. Logical `and`, `or`, `xor`, and `not` operate on filter state and require compatible filter shapes.
- Counting filter deletion flow decrements counters for a key only when the key is believed present. Dynamic filter insertion chooses an active row or creates a new row once the active-row threshold is exceeded. Retouched filter flow records known false positives and selectively clears bits using one of the `RemoveScheme` constants.

## State and Persistence Behavior

The JDiff XML file persists an API baseline, not application state. Its own important state is structural: package names, type names, method signatures, field declarations, inheritance relationships, checked exception declarations, and documentation blocks. This file should remain stable for compatibility comparisons.

The APIs described in the chunk expose several runtime state models:

- Service state is explicit and observable through `Service.STATE`, `ServiceStateModel`, lifecycle history, start time, failure cause/state, and blocker maps. Lifecycle history is returned as a snapshot list, and blockers are returned as a snapshotted map.
- `AbstractService.getConfig()` and `getLifecycleHistory()` are synchronized in this baseline, indicating concurrency-sensitive mutable internal state. `ServiceStateModel.enterState(...)` is also synchronized.
- `LifecycleEvent` is serializable and uses public fields, so its serialized shape and field names are part of a durable Java serialization contract.
- `CompositeService` owns a mutable child-service list; `getServices()` returns a clone so callers cannot mutate the manager's internal list directly.
- Trace administration persists active receiver configuration outside the XML. `SpanReceiverInfo` carries receiver id/class and builder-supplied configuration pairs that are sent over the tracing admin protocol.
- `ApplicationClassLoader` persists no external state, but its constructor-supplied URL list, parent loader, and system-class pattern list define class/resource resolution behavior for the life of the loader.
- `PureJavaCrc32` and `PureJavaCrc32C` maintain mutable checksum accumulators compatible with `java.util.zip.Checksum`.
- `ReflectionUtils.copy` and `cloneWritableInto` are serialization-sensitive because they depend on Hadoop `Writable` binary round trips.
- `StringInterner.strongIntern` retains strong references and can grow memory retention; `weakIntern` allows garbage collection.
- `BloomFilter`, `CountingBloomFilter`, `DynamicBloomFilter`, and `RetouchedBloomFilter` implement `write(DataOutput)` and `readFields(DataInput)`, making vector size, hash count/type, bit/counter vectors, row counts, false-positive metadata, and other internal fields durable Hadoop Writable state. Changing the order or meaning of serialized fields would break persisted filters.
- Counting Bloom filters have counter overflow/underflow semantics documented as part of the behavioral contract. Dynamic Bloom filters persist a matrix-like collection of rows and an `nr` threshold. Retouched Bloom filters persist or reconstruct false-positive/selective-clearing state through their Writable methods.

## Dependencies and Integration Points

This chunk integrates with core Java APIs:

- `java.io.Closeable`, `IOException`, `Serializable`, `DataInput`, `DataOutput`, `PrintStream`, and `MalformedURLException`.
- `java.net.URL`, `URLClassLoader`, and class/resource loading.
- `java.util.List`, `Collection`, `Map`, and Java reflection `Class`.
- `java.util.zip.Checksum`.

Hadoop-specific integration points include:

- `org.apache.hadoop.conf.Configuration`, `Configurable`, and the generic command-line option system used by `Tool` and `ToolRunner`.
- `org.apache.hadoop.service.Service.STATE`, `ServiceStateChangeListener`, `ServiceStateException`, and lifecycle model classes used by long-running daemons across Hadoop Common, HDFS, and YARN.
- Commons Logging `org.apache.commons.logging.Log` for service state logging, stop-quietly warnings, and thread-info logging.
- Hadoop tracing protobufs and IPC through `TraceAdminPB.TraceAdminService.BlockingInterface` and `org.apache.hadoop.ipc.VersionedProtocol`.
- Hadoop serialization through `org.apache.hadoop.io.Writable` and `Writable` copy helpers.
- Bloom-filter package types `Filter`, `Key`, and hash-type constants from `org.apache.hadoop.util.hash.Hash`, which are referenced here but defined outside this visible chunk.
- Command-line tools that implement `Tool` commonly combine this API with `Configured`, `GenericOptionsParser`, filesystem paths, MapReduce job setup, and process exit handling.

## Risks and Edge Cases

- This chunk begins mid-`AbstractService`, immediately after the `waitForServiceToStop(long)` method declaration opened in the previous chunk. The merge lane must combine chunk 5 and chunk 6 before making whole-class claims about all `AbstractService` fields and methods.
- JDiff metadata does not contain method bodies. Exact listener collections, blocker map implementation, lifecycle transition tables, Bloom vector encodings, classloader pattern syntax, and exception messages require Java source validation if implementation-level details matter.
- Service listeners are invoked while the service is synchronized and on the transition caller's thread. Long callbacks, recursive service calls, or callbacks that wait on other lifecycle operations can deadlock or stall daemon startup/shutdown.
- `Service.getConfig()` documentation says the returned configuration is normally not cloned. Mutating it after service initialization can have undefined or implementation-specific effects.
- `Service.stop()` must work even when fields were never initialized or were only partially initialized. Subclasses that assume STARTED-only state in cleanup risk failing after init/start errors.
- `CompositeService.getServices()` returns a snapshot; services added after the call are not visible through that list. Code that iterates an older snapshot may miss later children.
- `STOP_ONLY_STARTED_SERVICES` changes shutdown breadth. Child services must tolerate stop after failed init/start even if normal policy skips non-started services.
- `ServiceStateException.convert(Throwable)` preserves runtime exceptions but wraps checked exceptions and other throwables. Callers relying on exact checked exception types lose that static typing at this boundary.
- Trace admin methods throw `IOException`; adding/removing span receivers is an operational RPC surface and can fail due to authorization, IPC, invalid class/configuration, or receiver construction failures.
- `ApplicationClassLoader` class/resource isolation is pattern-driven. Incorrect system-class patterns can cause class version conflicts, parent/application split-brain, resource shadowing, or linkage errors.
- `PureJavaCrc32` documentation cites performance relative to old Java 1.6 native CRC32; modern JVM/hardware behavior may differ, so performance tests should not assume that old ratio.
- `StringInterner.strongIntern` intentionally retains strong references and can create unbounded memory retention if used on high-cardinality data.
- `ReflectionUtils.copy` destroys the destination object's old contents and depends on correct `Writable` serialization. It is unsafe for objects with non-serialized side state unless callers account for that.
- `ToolRunner.run(Tool, String[])` is documented as equivalent to `run(tool.getConf(), tool, args)`. A null or shared `Configuration` can affect command parsing and later code unexpectedly.
- Bloom filter logical operations require compatible vector size/hash configuration. The signatures accept `Filter`, so invalid concrete type or incompatible shape likely fails at runtime.
- Standard Bloom filters can return false positives by design but should not return false negatives after insertion. Counting and retouched variants can introduce underflow/false-negative behavior around deletes and selective clearing.
- Counting Bloom filters overflow when the same key is inserted too many times for the bucket size; the Javadoc explicitly warns that more than 15 inserts can increase error rates for that and other keys.
- `RetouchedBloomFilter.selectiveClearing` trades false positives for false negatives. Users must choose remove schemes based on the expected cost of each error type.
- The empty `org.apache.hadoop.util.hash` package node in this chunk means hash implementations are not visible here, even though Bloom APIs depend on hash type constants and behavior.

## Test Signals

Useful tests or compatibility checks for this chunk include:

- JDiff/schema checks that every package/type/method/field in lines 30558-32555 remains parseable and that generated metadata preserves visibility, static/final/synchronized flags, return types, parameters, checked exceptions, and deprecation markers.
- Service lifecycle tests for NOTINITED-to-INITED-to-STARTED-to-STOPPED transitions, invalid transitions, double init/start/stop behavior, failure cause/state recording, start time, lifecycle history snapshots, and `waitForServiceToStop(0)` / timeout behavior.
- `AbstractService` tests for subclass hook invocation exactly once, configuration replacement during `serviceInit`, robust stop after partial initialization, blocker map put/remove/snapshot behavior, local/global listener registration, unregister return values, and close delegating to stop.
- Listener tests that assert callbacks see the updated state, that callbacks run synchronously on the initiating thread, that slow listeners delay transition completion, and that reentrant listener behavior is documented or guarded.
- `CompositeService` tests for child init/start/stop ordering, child failure cleanup, removing services, `addIfService(Object)` true/false behavior, snapshot semantics of `getServices()`, and shutdown behavior around `STOP_ONLY_STARTED_SERVICES`.
- `ServiceOperations` tests for null-safe stop, state-checked stop, `stopQuietly` exception capture, optional logging, and non-catching behavior for non-Exception `Throwable` if the implementation follows the Javadoc strictly.
- `ServiceStateModel` tests for every valid and invalid transition, synchronized concurrent `enterState`, `ensureCurrentState` errors, and `toString()` state text.
- Tracing admin tests for `SpanReceiverInfoBuilder` configuration-pair construction, `listSpanReceivers`, `addSpanReceiver`, `removeSpanReceiver`, protobuf protocol versioning, error propagation, and access-control/invalid-receiver failures.
- `ApplicationClassLoader` tests for URL and classpath-string constructors, malformed classpath errors, resource child-first behavior, class child-first behavior, parent/system class exclusions, negative pattern handling, and compatibility with `SYSTEM_CLASSES_DEFAULT`.
- `Progressable` integration tests in long-running operations to confirm progress calls prevent framework timeouts.
- CRC tests comparing `PureJavaCrc32` against `java.util.zip.CRC32` golden values and `PureJavaCrc32C` against CRC32-C golden values, including byte-array chunking, single-byte updates, reset, and empty input.
- `ReflectionUtils` tests for `setConf` on `Configurable` and non-`Configurable` objects, `newInstance` configuration injection, thread-info logging interval behavior, `copy`/`cloneWritableInto` golden Writable round trips, and inherited field/method enumeration.
- `StringInterner` tests for equal strings returning representative instances, weak references becoming collectible, strong references remaining retained, and null handling if supported by implementation.
- `Tool`/`ToolRunner` tests for generic option parsing, configuration mutation before `run`, run return-code propagation, exception propagation, `printGenericCommandUsage`, and `confirmPrompt` yes/no parsing.
- Bloom filter tests for add/membership false-positive bounds, no false negatives for inserted keys in plain Bloom filters, logical and/or/xor/not compatibility checks, serialization round trips, vector-size reporting, and constructor/readFields behavior.
- Counting Bloom filter tests for delete of absent keys, count approximation, repeated insert overflow warnings, underflow after deletes, serialization, and logical operations against incompatible filters.
- Dynamic Bloom filter tests for row growth when `nr` is reached, membership across multiple rows, serialization of row thresholds/state, and logical operation behavior across dynamic filters.
- Retouched Bloom filter tests for adding false positives through all overloads, null false-positive handling, selective clearing with each `RemoveScheme`, tradeoff effects on false positives/false negatives, and Writable round trips.

## Cross-Chunk Notes

The previous chunk owns the beginning and middle of `AbstractService`, including the public lifecycle method declarations that lead into this chunk. This chunk closes the XML file, so there is no next chunk. The merge/reconciliation lane should combine all six chunks for `Apache_Hadoop_Common_2.7.2.xml` before producing the final source-tree-aligned per-file report.
