# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.6.0.xml lines 42402-45596

## Scope

This chunk is a JDiff API description for part of the Hadoop Common 2.6.0 public surface. It starts in `org.apache.hadoop.service`, then covers protocol-buffer translators for user/group mapping, tracing administration protocol types, many `org.apache.hadoop.util` helper APIs, and the beginning of `org.apache.hadoop.util.bloom`. The file records signatures, inheritance, visibility, exceptions, and Javadoc rather than method bodies, so implementation behavior below is inferred from the documented API contract and matching Java sources in the same Hadoop Common tree where available.

## Purpose

The covered APIs provide reusable infrastructure used across Hadoop daemons, command-line tools, RPC protocols, and filesystem utilities:

- Service lifecycle management: state model, transition validation, listeners, logging, and cleanup helpers.
- Protocol adapters: PB client/server translators for `GetUserMappingsProtocol` and tracing administration protocol interfaces.
- Utility foundations: application class loading, IP allow lists, reference counting, version comparison, checksums, disk/exit exceptions, bounded input streams, option wrappers, progress callbacks, protobuf IPC helpers, reflection, shell execution, shutdown hooks, string interning, binary prefix parsing, command runner support, and waitable values.
- Bloom filter data structures: standard, counting, dynamic, and retouched Bloom filters plus hash and removal-scheme helpers.

Because this is an API-diff artifact, its main value is compatibility research: identifying externally visible contracts that downstream code may compile against or depend on at runtime.

## Important APIs, Types, and Functions

### Service lifecycle APIs

- `LoggingStateChangeListener` implements `ServiceStateChangeListener` and logs state-change events at INFO level. It can log to a provided Commons Logging `Log` or to its class log.
- `Service` is the core lifecycle interface. It extends `Closeable` and defines `init(Configuration)`, `start()`, `stop()`, `close()`, listener registration, `getName()`, `getConfig()`, state/failure accessors, `waitForServiceToStop(long)`, lifecycle history snapshots, and blocker maps for remote dependencies preventing liveness.
- `Service.STATE` is a stable-valued enum with `NOTINITED`, `INITED`, `STARTED`, and `STOPPED`; `getValue()` exposes explicit numeric values for array lookup and management interfaces, and `toString()` returns the state name.
- `ServiceOperations` provides static lifecycle helpers. `stop(Service)` invokes `stop()` when non-null; `stopQuietly(Service)` and `stopQuietly(Log, Service)` catch and return `Exception`s for cleanup paths.
- `ServiceOperations.ServiceListeners` manages `ServiceStateChangeListener` registrations. `add`, `remove`, and `reset` are synchronized; `notifyListeners(Service)` snapshots the listener array before callback dispatch so registrations can change while notifications are in progress.
- `ServiceStateChangeListener.stateChanged(Service)` is called after the service state already changed, on the initiating thread and while the service is in a synchronized section. Javadoc explicitly warns that slow callbacks delay state transitions and re-entrant service calls can deadlock.
- `ServiceStateException` is a `RuntimeException` for invalid lifecycle operations and includes `convert(Throwable)` overloads to wrap checked exceptions.
- `ServiceStateModel` owns transition validation. It holds a volatile current `Service.STATE`, supports `ensureCurrentState`, synchronized `enterState`, static `checkStateTransition`, and static `isValidStateTransition`. The valid transition matrix permits `NOTINITED -> INITED|STOPPED`, `INITED -> INITED|STARTED|STOPPED`, `STARTED -> STARTED|STOPPED`, and only `STOPPED -> STOPPED`.

### Protocol and tracing APIs

- `GetUserMappingsProtocolClientSideTranslatorPB` adapts the PB interface to `GetUserMappingsProtocol` and `ProtocolMetaInterface`. It builds `GetGroupsForUserRequestProto`, calls `GetUserMappingsProtocolPB.getGroupsForUser`, converts response groups to `String[]`, supports method capability checks through `RpcClientUtil`, and closes by stopping the RPC proxy.
- `GetUserMappingsProtocolServerSideTranslatorPB` adapts a server-side `GetUserMappingsProtocol` implementation to the PB blocking interface, translating `IOException` into protobuf `ServiceException` and copying group strings into `GetGroupsForUserResponseProto`.
- `SpanReceiverInfo` exposes span receiver id and implementation class name. `SpanReceiverInfoBuilder` constructs it from a class name and configuration pairs.
- `TraceAdminProtocol` exposes `listSpanReceivers()`, `addSpanReceiver(SpanReceiverInfo)`, and `removeSpanReceiver(long)`, all throwing `IOException`; it also publishes `versionID`.
- `TraceAdminProtocolPB` is the protobuf protocol marker/extension point for the tracing administration service.

### General utility APIs

- `ApplicationClassLoader` is a child-first `URLClassLoader` for application isolation. It accepts URL arrays or a classpath string, expands wildcard jar directories, and treats configured system-class patterns as parent-first. `isSystemClass(String, List<String>)` supports positive and negative package/class patterns.
- `IPList` defines `isIn(String)`. `FileBasedIPList` loads IPs and CIDR ranges from a UTF-8 file into a `MachineList`; `CacheableIPList` wraps it with volatile cache expiry and explicit refresh; `CombinedIPWhiteList` checks fixed and optional reloadable allow lists and always allows `127.0.0.1`; `MachineList` accepts hostnames, IPs, CIDRs, and wildcard `*`, resolving hosts through an injectable `InetAddressFactory`.
- `CloseableReferenceCount` is an atomic open/closed plus reference-count guard. `reference()` fails with `ClosedChannelException` after closure, `unreference()` reports when closed with zero references, `unreferenceCheckClosed()` detects asynchronous close, and `setClosed()` atomically marks the object closed.
- `ComparableVersion` is a Maven-derived version comparator. It parses mixed dot/dash/digit/string components, normalizes known qualifiers such as alpha, beta, milestone, rc, snapshot, release/final/ga, and sp, and implements `compareTo`, `equals`, `hashCode`, and `toString`.
- `DataChecksum.Type` exposes checksum enum lookup and fields `id` and `size`, letting callers map wire ids to checksum kinds.
- `DiskChecker.DiskErrorException`, `DiskChecker.DiskOutOfSpaceException`, `ExitUtil.ExitException`, and `ExitUtil.HaltException` expose structured exception types with status codes where applicable.
- `IdentityHashStore.Visitor`, `IntrusiveCollection.IntrusiveIterator`, `LightWeightCache.Entry`, `LightWeightGSet.LinkedElement`, and `LightWeightGSet.SetIterator` are collection support APIs for identity-key visitation, intrusive iteration/removal, cache expiration timestamps, linked hash-set elements, and modification tracking.
- `LimitInputStream` wraps an `InputStream` and enforces a remaining byte limit across `read`, bulk `read`, `skip`, `available`, `mark`, and `reset`.
- `Options` is a typed varargs option framework with wrapper subclasses for boolean, integer, long, class, string, `Path`, `FSDataInputStream`, `FSDataOutputStream`, and `Progressable`. `getOption` returns the first exact-class match; `prependOptions` prefixes new options ahead of old ones.
- `PerformanceAdvisory.LOG` exposes a dedicated SLF4J logger for performance warnings. `Progressable.progress()` is the callback used by Hadoop APIs to report forward progress.
- `ProtoUtil` provides protobuf IPC helpers: raw varint32 reading, IPC connection context creation from protocol/UGI/auth method, UGI reconstruction from protobuf user info, RPC kind conversion, and request header creation including call id, retry count, client id, tracing context, caller context, authorization header, and optional alignment context.
- `PureJavaCrc32` and `PureJavaCrc32C` implement Java `Checksum`-style CRC32 and CRC32C operations with `getValue`, `reset`, and byte-array/single-byte `update`.
- `ReflectionUtils` handles configuration injection, reflective construction with constructor caching, thread dump printing/logging with rate limiting, typed class lookup, Writable copy/clone via Hadoop serialization buffers, and inherited field/method discovery.
- `Shell.CommandExecutor`, `Shell.ExitCodeException`, `Shell.OSType`, and `Shell.ShellCommandExecutor` expose the command execution API. The executor supports command arrays, working directory, environment, timeout, output retrieval, exit code retrieval, and close.
- `ShutdownHookManager` is a singleton priority-ordered shutdown hook registry with add/remove/has/isShutdownInProgress methods. `ShutdownThreadsHelper` interrupts threads or shuts down `ExecutorService`s with default or caller-specified timeouts.
- `StringInterner` exposes strong and weak string interning. `StringUtils.TraditionalBinaryPrefix` maps binary prefixes to bit shifts/masks, parses strings to long values, and formats long values with binary units.
- `ThreadUtil.sleepAtLeastIgnoreInterrupts(long)` preserves minimum sleep duration while ignoring interrupts. `Tool` plus `ToolRunner` define the standard Hadoop command entry point, generic options parsing, usage printing, and interactive confirmation prompt.
- `Waitable<T>` wraps a `Condition`-backed value with `await`, `provide`, `hasVal`, and `getVal`.

### Bloom filter APIs

- `BloomFilter` extends `Filter` and implements a bit-vector Bloom filter. It supports default construction for `readFields`, parameterized construction with vector size, hash count, and hash type, plus `add`, `membershipTest`, bitwise `and`, `or`, `xor`, `not`, `toString`, `getVectorSize`, and Writable serialization.
- `CountingBloomFilter` extends `Filter` with 4-bit counters instead of bits. It supports `add`, `delete`, `membershipTest`, approximate key counts, `and`, `or`, `toString`, and Writable serialization. `not` and `xor` are declared but unsupported in implementation.
- `DynamicBloomFilter` extends `Filter` with a matrix of standard Bloom filters. It creates new rows when the active row reaches threshold `nr`, and it supports membership across rows plus row-wise logical operations and serialization.
- `HashFunction` wraps `org.apache.hadoop.util.hash.Hash` to generate `nbHash` positions under a `maxValue`; `clear()` is a no-op and `hash(Key)` rejects null/empty key bytes.
- `RemoveScheme` defines retouched Bloom filter clearing modes: `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`.
- `RetouchedBloomFilter` extends `BloomFilter` and implements `RemoveScheme`. It tracks known keys and false-positive keys per bit, supports adding false-positive evidence in single/collection/list/array forms, and `selectiveClearing(Key, short)` chooses a bit to clear according to the requested scheme.

## Control Flow

Service control flow is a state-machine contract. Callers construct a `Service`, call `init(Configuration)`, then `start()`, and eventually `stop()` or `close()`. Implementations are required to transition through the documented states or stop on failure. `ServiceStateModel.enterState` performs the transition check atomically and returns the previous state. State listeners are notified after transitions; `ServiceOperations.ServiceListeners` snapshots the callbacks and invokes them synchronously on the caller's thread.

PB translator flow is adapter-based. On the client side, Java interface calls are converted to request protos, sent through a PB proxy, and converted back to Java arrays or booleans. On the server side, PB requests call the underlying Java implementation, then copy Java values into response protos. Checked `IOException`s cross the PB boundary as protobuf `ServiceException`s.

Utility control flow is mostly synchronous and local. `ApplicationClassLoader` tries child URLs first for non-system classes/resources, then delegates to the parent. IP-list checks flow from `CombinedIPWhiteList` through fixed and cached lists into `MachineList` hostname/CIDR matching. `LimitInputStream` decrements a remaining-byte counter on every successful read or skip. `ToolRunner.run` parses Hadoop generic CLI options into a `Configuration`, sets the tool configuration, and invokes `Tool.run` with remaining arguments.

RPC header construction in `ProtoUtil` layers optional context into a required header: RPC kind, operation, call id, retry count, client id, current tracing span, current caller context, current authorization header, and optional alignment state. UGI serialization differs by auth method: Kerberos sends effective user only, token sends no user info, and simple auth sends effective plus optional real user.

Shell and shutdown flows manage external processes and JVM termination. `Shell.ShellCommandExecutor.execute()` runs a configured command and captures output/exit status. `ShutdownHookManager` registers one JVM hook, sorts registered hooks by priority, executes each through a single-thread executor with timeout enforcement, and then shuts the executor down. `ShutdownThreadsHelper` interrupts threads or shuts down executors and waits before escalating to `shutdownNow()`.

Bloom filter flow is hash-then-mutate or hash-then-test. `HashFunction.hash` derives multiple positions using repeated seeded hash invocations. `BloomFilter.add` sets those positions and `membershipTest` requires all positions to be set. `CountingBloomFilter.add` increments bounded 4-bit counters and `delete` decrements only if the key appears present. `DynamicBloomFilter.add` inserts into the active row or appends a row when full. `RetouchedBloomFilter.selectiveClearing` hashes a known false positive, chooses one candidate bit by the configured removal scheme, and clears it, trading false positives for possible false negatives.

## State and Persistence Behavior

The service APIs define in-memory lifecycle state, not durable persistence. `ServiceStateModel.state` is volatile and transition updates are synchronized. `Service.getLifecycleHistory()` and `getBlockers()` return snapshots, while failure cause/state expose first failure metadata maintained by implementations such as `AbstractService`.

The PB translators are mostly stateless wrappers around an RPC proxy or implementation reference. Their external state is the remote RPC connection, closed through `RPC.stopProxy`.

Several utility classes keep process-local mutable state:

- `ApplicationClassLoader` stores parent loader and system-class pattern lists and relies on URLClassLoader's loaded-class cache.
- `CacheableIPList` stores a volatile `FileBasedIPList` and volatile expiry timestamp; refresh forces reload on the next lookup.
- `CloseableReferenceCount` packs open/closed status and reference count into an `AtomicInteger` bit field.
- `ReflectionUtils` caches constructors in a static concurrent map and uses thread-local serialization buffers for object copying.
- `ShutdownHookManager` stores hook entries in a synchronized set and a shutdown-in-progress atomic flag.
- `StringInterner.strongIntern` intentionally retains strong references; `weakIntern` delegates to JVM string interning behavior in this API generation.

Bloom filters persist through Hadoop `Writable` serialization. `Filter.write` records a version marker, number of hashes, hash type, and vector size; `readFields` also handles an older unversioned format by treating the first positive int as `nbHash` and defaulting to Jenkins hash. Concrete filters append their bit vector, counter array, dynamic matrix rows, or retouched vectors. This persistence is binary and parameter-sensitive: readers must reconstruct hash functions and internal arrays from the serialized metadata before using the filter.

## Dependencies and Integration Points

- Service APIs integrate with `org.apache.hadoop.conf.Configuration`, `AbstractService`, `CompositeService`, lifecycle event history, Commons Logging/SLF4J logging, and daemon shutdown code.
- User mapping translators integrate with Hadoop IPC (`RPC`, `RpcClientUtil`, `ProtocolMetaInterface`), shaded protobuf controller/service exceptions, and generated `GetUserMappingsProtocolProtos`.
- Tracing APIs integrate with Hadoop tracing span receiver management and protobuf tracing admin service definitions.
- Utility classes depend on Hadoop FS types (`Path`, `FSDataInputStream`, `FSDataOutputStream`, `FileUtil`), Hadoop IPC protobufs, `UserGroupInformation`, auth methods, `CallerContext`, `AuthorizationContext`, Hadoop serialization, `Writable`, Java management beans, Java concurrency primitives, Apache Commons Net `SubnetUtils`, and logging APIs.
- Shell utilities integrate with OS-specific Hadoop support such as `winutils.exe`, process execution, environment handling, and platform detection.
- `Tool` and `ToolRunner` integrate with `Configurable`, `Configuration`, `GenericOptionsParser`, command audit context, and CLI callers.
- Bloom filters depend on `org.apache.hadoop.util.hash.Hash`, `Key`, `Writable`, and Java collections/bitsets. They are marked public/stable in this API slice and can be used by HDFS, MapReduce, and downstream applications.

## Risks and Edge Cases

- The service listener contract is synchronous and potentially inside service locks. Slow callbacks or callbacks that re-enter the same service can stall lifecycle transitions or deadlock.
- `ServiceOperations.stop` in implementation simply calls `stop()` for non-null services; the XML Javadoc says it checks whether the service needs stopping. Callers should not rely on pre-check semantics without verifying the target version.
- `ServiceStateModel` allows idempotent transitions such as `INITED -> INITED`, `STARTED -> STARTED`, and `STOPPED -> STOPPED`. Code that treats repeated lifecycle calls as errors may diverge from this model.
- `Service.close()` declares `IOException` but the contract says implementations relay directly to `stop()` and never throw `IOException`; callers still need to handle runtime failures.
- PB translators depend on exact protobuf field mapping. Empty or null group arrays, method support checks, and `ServiceException` wrapping are important compatibility points for clients.
- `ApplicationClassLoader` is child-first only for non-system classes. Misconfigured negative/positive system class patterns can load incompatible Hadoop or dependency classes into an isolated application.
- IP allow-list behavior differs for nulls: `FileBasedIPList.isIn(null)` returns false, while `CombinedIPWhiteList.isIn(null)` and `MachineList.includes(null)` throw `IllegalArgumentException`. Callers should normalize inputs before choosing the wrapper.
- `CacheableIPList` uses wall-clock time and double-checked locking with volatile fields. Clock changes or very small cache timeouts can cause unexpected reload frequency.
- `CloseableReferenceCount` reserves bit 30 for closed state; extreme reference counts would collide with status bits, and unbalanced `unreference()` calls fail by precondition.
- `Options.getOption` uses exact class equality, not `isAssignableFrom`, so subclasses of the requested option wrapper are not returned.
- `ProtoUtil.readRawVarint32` must reject malformed or truncated encodings; fuzz tests should cover EOF after each byte and overlong varints.
- `ReflectionUtils` constructor caching pins classes and can matter in classloader-isolated environments. Serialization copy uses a static `SerializationFactory` initialized from the first configuration.
- `ToolRunner.confirmPrompt` reads raw `System.in` and loops until recognized input; tests need controlled streams to avoid hanging.
- `Shell.ShellCommandExecutor` and shutdown helpers depend on OS process behavior and interrupt handling. Timeout cancellation does not guarantee immediate process or hook termination if code ignores interrupts.
- `StringInterner.strongIntern` can grow without release. Use it only for bounded vocabularies.
- `CountingBloomFilter` counters saturate at 15; repeated inserts of the same key increase error rates, and deletion after collisions can introduce false negatives. `not` and `xor` are visible in the API but unsupported.
- `DynamicBloomFilter.membershipTest(null)` returns true in the matching implementation, unlike other Bloom filters that reject null keys. This surprising edge case can mask caller bugs.
- `RetouchedBloomFilter.selectiveClearing` deliberately introduces false negatives. The removal scheme constants are public shorts, so invalid values reach an assertion path rather than a checked exception.

## Test Signals

- Service lifecycle tests should cover every valid and invalid transition in `ServiceStateModel`, listener add/remove/reset behavior during notification, idempotent stop/close, failure cause/state capture, `waitForServiceToStop(0)` semantics, and blocker/lifecycle history snapshot immutability.
- Listener tests should include slow callbacks and re-entrant service calls to document deadlock/stall risks.
- PB translator tests should verify client request construction, server response construction, `IOException` to `ServiceException` wrapping, close behavior, and `isMethodSupported` against a mock proxy.
- Tracing protocol tests should validate span receiver list/add/remove behavior and builder preservation of class name and configuration pairs.
- Classloader tests should cover wildcard classpath expansion, missing classpath entries, child-first loading for application classes, parent-first system classes, and negative system-class overrides.
- IP-list tests should cover missing files, null inputs, wildcard entries, CIDR inclusive host counts, invalid CIDR syntax, unresolved hostnames, cache refresh, cache expiry, localhost whitelist behavior, and injected `InetAddressFactory`.
- Reference-count tests should cover concurrent reference/close races, unbalanced unreference detection, and `AsynchronousCloseException` from `unreferenceCheckClosed`.
- Utility tests should cover version ordering qualifiers, checksum type lookup, `LimitInputStream` mark/reset/skip/EOF behavior, exact-class option lookup, varint malformed input, UGI construction for Kerberos/token/simple auth, RPC header optional context fields, reflection constructor caching/config injection, Writable copy/clone behavior, shell executor timeout/output, shutdown hook priority/timeouts, binary prefix parse/format, and `Waitable` condition wakeups.
- Tool tests should assert generic options are stripped before `Tool.run`, configuration is injected, caller/audit context is set, usage text is emitted, and prompt parsing accepts only yes/no variants.
- Bloom filter tests should round-trip every concrete filter through `write/readFields`, verify membership false-positive/no-false-negative expectations for standard filters, reject incompatible logical operations, exercise counting saturation and delete behavior, force dynamic row expansion at `nr`, validate retouched clearing schemes, and test null/empty key handling for each filter type.
