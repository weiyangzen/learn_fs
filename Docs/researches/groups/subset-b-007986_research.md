# Research: subset-b-007986 Ozone HDDS utility, codec, retry, and IPC support files

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/LegacyHadoopConfigurationSource.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/LegacyHadoopConfigurationSource.java

## Purpose
Adapts a Hadoop `Configuration` to Ozone's `MutableConfigurationSource` while preserving access to the original Hadoop configuration for legacy Hadoop APIs.

## Important APIs, Types, And Functions
`LegacyHadoopConfigurationSource` wraps a defensive `Configuration` copy whose `getProps()` returns `DelegatingProperties` with crypto-compliance filtering. Public APIs are `get`, `getPassword`, `getConfigKeys`, `set`, `asHadoopConfiguration`, and `getOriginalHadoopConfiguration`.

## Control Flow
Construction creates an anonymous `Configuration` subclass. On first `getProps()`, it reads the compliance mode without filtering, gathers properties tagged `CRYPTO_COMPLIANCE`, and builds `DelegatingProperties`; `reloadConfiguration()` clears that cache. `iterator()` delegates to the filtered properties. `asHadoopConfiguration()` accepts either a real `Configuration` or this wrapper, and rejects other `ConfigurationSource` implementations.

## State And Persistence
State is the wrapped `Configuration` plus cached `delegatingProps` inside the anonymous subclass. `set()` mutates the wrapped Hadoop configuration in memory; persistence is whatever Hadoop `Configuration` resources provide.

## Dependencies And Integration Points
Integrates `org.apache.hadoop.conf.Configuration`, Ozone `ConfigurationSource`, `MutableConfigurationSource`, `DelegatingProperties`, `ConfigTag`, and `OzoneConfigKeys`. It intentionally catches `NoSuchMethodError` so Hadoop 2 runtimes without `getAllPropertiesByTag` still work.

## Risks
The wrapper makes a new `Configuration(configuration)`, so clients expecting shared object identity can be surprised. Crypto compliance depends on Hadoop property tagging availability. `getConfigKeys()` calls `getPropsWithPrefix("")`, which may force property materialization. `asHadoopConfiguration()` is server-side oriented and throws on non-Hadoop Ozone configs.

## Test Signals
`TestOzoneConfiguration` covers wrapping and `asHadoopConfiguration`. Useful extra tests are crypto-compliance filtering, Hadoop 2 compatibility behavior, reload invalidation, password-provider access, and mutation visibility through `set()`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/LegacyHadoopConfigurationSource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/RatisVersionInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/RatisVersionInfo.java

## Purpose
Loads and exposes build metadata for Apache Ratis as used by Ozone.

## Important APIs, Types, And Functions
The class owns a `Properties info` map loaded from `ratis-version.properties`. Public getters are `getVersion()`, `getRevision()`, and `getBuildVersion()`.

## Control Flow
The constructor resolves the resource through `ThreadUtil.getResourceAsStream`, loads it into `Properties`, and logs a warning on `IOException`. Getters return property values with `"Unknown"` fallbacks.

## State And Persistence
State is in-memory immutable-after-construction metadata. There is no write path; persistence is the packaged build-resource file.

## Dependencies And Integration Points
Depends on Hadoop `ThreadUtil` resource loading, Java `Properties`, and SLF4J. Consumers can use it in version banners, diagnostics, or endpoint metadata.

## Risks
If the resource is missing or unreadable, the object still constructs and silently degrades to `"Unknown"` values except for the warning. The constructor does not explicitly handle a null stream unless `ThreadUtil` throws or supplies a non-null stream.

## Test Signals
Tests should verify packaged resource loading, fallback values when the resource is unavailable, and formatting of `"version from revision"`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/RatisVersionInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/ResourceCache.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/ResourceCache.java

## Purpose
Implements Ozone's `Cache<K,V>` using Guava weighted cache eviction to bound cached resource usage.

## Important APIs, Types, And Functions
The constructor requires a Guava `Weigher<K,V>`, a maximum weight, and an optional `RemovalListener<K,V>`. The `Cache` methods are `get`, `put`, `remove`, `removeIf`, and `clear`.

## Control Flow
Construction builds a `CacheBuilder.maximumWeight(limits).weigher(weigher)` cache, adding the listener when supplied. `get()` delegates to `getIfPresent`, `put()` to `put`, `remove()` to `invalidate`, `removeIf()` scans `cache.asMap().keySet()` and invalidates matching keys, and `clear()` invalidates all entries.

## State And Persistence
All mutable state is Guava cache state in memory. There is no ordering metadata in this class beyond Guava's eviction implementation, and no persistent storage.

## Dependencies And Integration Points
Depends on Guava cache APIs and Ozone's local `Cache` interface. Removal listeners integrate with resource cleanup such as closing buffers or file handles.

## Risks
The class comment says FIFO, but Guava maximum-weight eviction is not a strict FIFO contract. A single overweight entry may exceed the limit until eviction maintenance runs. `removeIf()` iterates a live concurrent view and may race with updates.

## Test Signals
`TestResourceCache` exercises weighted eviction and removal behavior. Additional useful tests are listener invocation, null-argument checks, overweight entries, and concurrent `removeIf()` with puts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/ResourceCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/RetriableTask.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/RetriableTask.java

## Purpose
Wraps a `Callable<V>` with Hadoop `RetryPolicy` handling for local tasks.

## Important APIs, Types, And Functions
`RetriableTask<V>` implements `Callable<V>`. Constructor inputs are a `RetryPolicy`, a task name for logging, and the delegate `Callable<V>`. The key method is `call()`.

## Control Flow
`call()` invokes the delegate. On exception it increments attempts and asks `retryPolicy.shouldRetry(e, attempts, 0, true)`. `RETRY` sleeps the caller thread for `delayMillis` using `ThreadUtil.sleepAtLeastIgnoreInterrupts`; any other action breaks, logs a permanent failure, and throws an `IOException` wrapping the last cause.

## State And Persistence
State is only constructor configuration and local attempt counters during a call. There is no persistence and no cross-call attempt history.

## Dependencies And Integration Points
Uses Hadoop retry policy semantics and Ozone/Hadoop retry-policy factories. Intended for utility tasks that need retry behavior outside dynamic RPC proxies.

## Risks
Interrupts during retry sleep are ignored by `sleepAtLeastIgnoreInterrupts`, so shutdown responsiveness depends on the policy and delegate. Non-IO delegate exceptions are always wrapped into `IOException` after permanent failure. The idempotent flag is hard-coded true.

## Test Signals
`TestRetriableTask` covers success, retry-until-success, and max-retry failure. Extra tests should cover interrupted callers and policies that return failover actions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/RetriableTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/Scheduler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/Scheduler.java

## Purpose
Small wrapper around `ScheduledExecutorService` for delayed and periodic Ozone utility work.

## Important APIs, Types, And Functions
Constructor creates a named daemon or non-daemon scheduled thread pool. Public methods are `schedule(Runnable, ...)`, `schedule(CheckedRunnable, ..., Logger, errMsg)`, `scheduleWithFixedDelay`, `isClosed`, and `close`.

## Control Flow
Tasks are submitted directly to the executor. The `CheckedRunnable` overload catches any `Throwable` and logs it instead of letting the scheduled executor suppress later work. `close()` marks `isClosed`, calls `shutdownNow()`, waits up to 60 seconds, preserves interrupt status, and nulls the executor reference.

## State And Persistence
State is the executor, volatile closed flag, and thread name. Scheduled tasks and futures are in-memory only.

## Dependencies And Integration Points
Depends on Java concurrent scheduling, Ratis `CheckedRunnable`, and SLF4J. It is a lifecycle helper for services needing background timers.

## Risks
`schedule()` does not reject based on `isClosed`; after `close()` it can hit `NullPointerException` or executor rejection. Threads all receive the same name, making multi-thread diagnostics less precise. `shutdownNow()` cancels pending work rather than draining gracefully.

## Test Signals
Useful tests cover delayed execution, fixed-delay execution, checked-runnable exception logging, close idempotency, interrupt preservation, and submissions after close.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/Scheduler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/SimpleStriped.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/SimpleStriped.java

## Purpose
Provides a factory for Guava striped read/write locks with optional fair ordering.

## Important APIs, Types, And Functions
The utility is final with a private constructor. `readWriteLock(int stripes, boolean fair)` returns `Striped<ReadWriteLock>` built with `Striped.custom` and `ReentrantReadWriteLock(fair)`.

## Control Flow
The static factory delegates lock creation to Guava and eagerly returns the striped lock container.

## State And Persistence
The utility owns no state. Lock state lives in returned `ReadWriteLock` instances and is process-local.

## Dependencies And Integration Points
Depends on Guava `Striped`, Java `ReadWriteLock`, and `ReentrantReadWriteLock`. It is used where keyed concurrency control needs lock striping with fairness control.

## Risks
Fair locks can reduce throughput under contention. Stripe count still controls collision rate, so too few stripes serializes unrelated keys. Behavior depends on Guava `Striped.custom` semantics.

## Test Signals
`TestSimpleStriped` verifies lock creation and fairness setting. Additional tests can check stripe stability for equal keys and contention behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/SimpleStriped.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/SlidingWindow.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/SlidingWindow.java

## Purpose
Tracks recent events with both time expiry and a maximum window size, useful for rate or burst accounting.

## Important APIs, Types, And Functions
`SlidingWindow` exposes `add`, `isExceeded`, `getNumEvents`, `getNumEventsInWindow`, `getWindowSize`, and `getExpiryDurationMillis`. A nested `MonotonicClock` uses `System.nanoTime()` converted to milliseconds.

## Control Flow
Construction validates non-negative size and positive expiry, then creates an `ArrayDeque` with bounded initial capacity. `add()` first calls `isExceeded()` and removes one oldest timestamp if already exceeded, then appends the current time. Queries synchronize on a private lock, prune expired timestamps, and compute size or capped size.

## State And Persistence
State is an in-memory deque of millisecond timestamps plus clock and config. There is no persistence. Synchronization protects deque mutation.

## Dependencies And Integration Points
Depends on Java time APIs and `@VisibleForTesting`. The custom clock supports deterministic tests.

## Risks
The constructor permits `windowSize == 0` although its error text says greater than 0; this makes every event exceed the window and `add()` can remove before adding. Expiry uses `< expirationThreshold`, so exact-boundary events remain. Nested synchronization is reentrant but redundant.

## Test Signals
`TestSlidingWindow` covers validation, expiry, max-size behavior, zero-size behavior, and custom-clock advancement. Concurrency tests would add confidence for simultaneous add/query use.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/SlidingWindow.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/UniqueId.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/UniqueId.java

## Purpose
Generates process-local long IDs by combining current time milliseconds with a 16-bit counter.

## Important APIs, Types, And Functions
The class is a non-instantiable utility. `next()` is synchronized, reads `HddsUtils.getTime()`, left-shifts it by `Short.SIZE`, and appends `offset++ & 0xFFFF`.

## Control Flow
Each call validates that the high 16 bits of the time value are clear, returns `(time << 16) | lowCounter`, or throws if time is too large.

## State And Persistence
State is the static `offset` counter in memory. IDs are not persisted and are not globally coordinated across processes.

## Dependencies And Integration Points
Depends on `HddsUtils.getTime()`. Tests and helper code such as `ContainerTestHelper` use it for local IDs.

## Risks
More than 65,536 calls in the same millisecond wrap the low counter and can collide. Clock rollback can produce lower or duplicate IDs. Cluster-wide uniqueness is not guaranteed.

## Test Signals
Useful tests are monotonic-ish generation under normal load, high-throughput same-millisecond collision behavior with a mocked clock, and invalid future time handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/UniqueId.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/VersionInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/VersionInfo.java

## Purpose
Loads build metadata for a named Hadoop/Ozone component from a packaged properties resource.

## Important APIs, Types, And Functions
`VersionInfo(String component)` loads `<component>-version-info.properties`. Getters expose release, version, revision, URL, source checksum, proto versions, compile platform, and formatted build version.

## Control Flow
The constructor opens the resource with `ThreadUtil.getResourceAsStream`, loads `Properties`, logs `IOException`, and closes through Hadoop `IOUtils.closeStream`. Getters use `"Unknown"` defaults.

## State And Persistence
State is an in-memory `Properties` object. The authoritative data is the build-time resource file.

## Dependencies And Integration Points
Annotated public/stable and used by component version singletons such as HDDS version information. Depends on Hadoop IO/resource utilities and SLF4J.

## Risks
Missing resources degrade to unknown values. The loaded keys must match build plugin output. Unlike `RatisVersionInfo`, this class exposes more fields and callers may assume non-unknown strings.

## Test Signals
Tests should verify real component property resources, fallback behavior, build-version formatting, and closing behavior for failed loads.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/VersionInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/BooleanCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/BooleanCodec.java

## Purpose
Serializes Java `Boolean` values for metadata stores.

## Important APIs, Types, And Functions
Singleton `BooleanCodec.get()` implements `Codec<Boolean>`. It supports `CodecBuffer`, writes one byte, reads one byte, and returns immutable booleans directly from `copyObject`.

## Control Flow
`toCodecBuffer()` allocates one byte and writes `1`; `toPersistedFormat()` writes `1` or `0`. Deserialization requires byte-array length one for persisted format; buffer format reads one byte and compares to `1`.

## State And Persistence
No mutable codec state. Persistent bytes are single-byte boolean encodings.

## Dependencies And Integration Points
Integrates with the shared `Codec` and `CodecBuffer` abstraction used by RocksDB table codecs.

## Risks
`toCodecBuffer(Boolean object, ...)` writes `TRUE` regardless of `object`, which differs from `toPersistedFormat()` and is a high-value bug signal unless callers never use buffer serialization for false. Deserialization treats any non-`1` value as false.

## Test Signals
Codec round-trip tests should explicitly include `false` through both byte-array and `CodecBuffer` paths. `CodecTestUtil`-style buffer leak checks apply.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/BooleanCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/Buffer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/Buffer.java

## Purpose
Internal reusable `CodecBuffer` holder for fetching variable-sized data from a `PutToByteBuffer` source, typically database direct-buffer reads.

## Important APIs, Types, And Functions
Package-private `Buffer` stores a mutable `CodecBuffer.Capacity`, an optional `PutToByteBuffer<RuntimeException> source`, and a cached `CodecBuffer`. Methods are `getFromDb()` and `release()`.

## Control Flow
`getFromDb()` prepares or allocates a direct resizable buffer. It invokes the source, returns null when the source is unavailable, returns the buffer when readable bytes match the required size, tries `setCapacity(required)`, and otherwise increases the shared capacity hint and reallocates.

## State And Persistence
State is an owned pooled direct buffer and adaptive initial-capacity hint. It must be released to return Netty memory to the pool. No disk persistence is owned here.

## Dependencies And Integration Points
Depends on `CodecBuffer`, `CodecBuffer.Capacity`, `PutToByteBuffer`, and Ratis `Preconditions`. It is a helper for DB APIs that can report required value size.

## Risks
Callers must not retain the buffer across `getFromDb()` reuse without ownership discipline. If `source` writes inconsistent sizes, assertions fail. Missing `release()` leaks pooled buffers.

## Test Signals
Tests should cover unavailable source, exact fit, capacity growth by `setCapacity`, reallocation growth, repeated reuse, and leak detection via `CodecBuffer.assertNoLeaks()`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/Buffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/Codec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/Codec.java

## Purpose
Defines the serialization contract for converting Java metadata objects to persisted bytes and optional `CodecBuffer` instances.

## Important APIs, Types, And Functions
Key methods are `getTypeClass`, `supportCodecBuffer`, `toCodecBuffer`, `toDirectCodecBuffer`, `toHeapCodecBuffer`, `fromCodecBuffer`, `toPersistedFormat`, `toPersistedFormatImpl`, `fromPersistedFormat`, `fromPersistedFormatImpl`, and `copyObject`.

## Control Flow
Default buffer methods throw unless an implementation opts in. Default byte-array methods null-check inputs, delegate to `Impl` methods, and wrap failures in `CodecException` with type/length context.

## State And Persistence
The interface owns no state. Implementations define persisted byte layout and copy semantics for DB keys/values.

## Dependencies And Integration Points
Used by table, cache, and RocksDB layers throughout HDDS/Ozone. `CodecBuffer` support enables direct-buffer DB APIs and reduced copying.

## Risks
Implementations must keep byte-array and buffer encodings consistent. Some primitive codecs permit null byte-array serialization despite the interface comment saying objects should not be null. Incorrect `copyObject` semantics can expose mutable DB cache state.

## Test Signals
`CodecTestUtil` exercises byte-array and `CodecBuffer` round trips, copy behavior, old-codec compatibility, and leak checks. Every codec should use it for both heap and direct buffers where supported.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/Codec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/CodecBuffer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/CodecBuffer.java

## Purpose
Wraps Netty `ByteBuf` as an Ozone codec buffer for pooled heap/direct memory, direct RocksDB-style byte access, protobuf IO, and leak diagnostics.

## Important APIs, Types, And Functions
Important pieces are `Allocator` direct/heap factories, `Capacity`, `allocateDirect`, `allocateHeap`, `wrap(byte[])`, `wrap(ByteString)`, `enableLeakDetection`, `assertNoLeaks`, `release`, `asWritableByteBuffer`, `asReadOnlyByteBuffer`, `getArray`, `startsWith`, `getInputStream`, numeric `put*`, `put(ByteBuffer)`, `put(OutputStream source)`, and package-private `putFromSource`.

## Control Flow
Allocation uses Netty pooled allocators; non-negative capacity fixes max capacity, negative capacity allows growth. `release()` completes a future and releases the underlying buffer. Encoding helpers update writer indexes after source functions write to `ByteBuffer` or `OutputStream`. Leak detection swaps the factory to a subclass whose finalizer calls `detectLeaks`.

## State And Persistence
State is pooled buffer reference count, wrapped source object, captured allocation stack, and release future. No persistent storage is owned, but bytes represent persistent codec data.

## Dependencies And Integration Points
Depends on Ratis-shaded Netty buffers, protobuf `ByteString`, Ratis utilities, Hadoop `StringUtils`, and codec implementations. It is central to DB direct-buffer pathways.

## Risks
Manual release is required for non-empty buffers. `getArray()` consumes readable bytes by advancing the reader index. `asWritableByteBuffer()` exposes max capacity, so writers must respect writer-index handling. Leak detection uses finalization and carries performance cost.

## Test Signals
`CodecTestUtil`, `TestLeakDetector`, and consumers such as multipart key codec tests cover round trips and leaks. Additional tests should cover direct vs heap, zero-capacity release idempotency, `startsWith`, and source-size mismatch behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/CodecBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/CodecException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/CodecException.java

## Purpose
Typed checked exception for codec serialization and deserialization failures.

## Important APIs, Types, And Functions
`CodecException` extends `IOException` and provides default, message, and message-plus-cause constructors.

## Control Flow
No custom logic; it is constructed and thrown by codec implementations and interface defaults.

## State And Persistence
No persistent state beyond standard exception message and cause.

## Dependencies And Integration Points
Used by `Codec`, `DelegatedCodec`, protobuf codecs, and string codec paths so callers can treat codec failures as IO-level DB failures.

## Risks
Because it extends `IOException`, broad IO handlers may hide data-corruption distinctions unless logs preserve context.

## Test Signals
Codec tests should assert `CodecException` wrapping for invalid bytes, malformed strings, and protobuf parse errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/CodecException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/CopyObject.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/CopyObject.java

## Purpose
Declares a lightweight object-level copy hook for codec cache safety.

## Important APIs, Types, And Functions
The functional interface has one method: `T copyObject()`.

## Control Flow
No control flow exists in the interface. `DelegatedCodec.copyObject()` detects this interface and delegates copying to the object itself.

## State And Persistence
No state. Implementations decide whether copying is deep or can return `this` for immutable types.

## Dependencies And Integration Points
Integrates with codec copying and DB cache isolation for mutable metadata objects.

## Risks
An implementation returning a shallow copy for mutable state can leak mutations across cache or DB table callers. Generic type misuse is possible at runtime.

## Test Signals
Tests should verify mutable implementations really detach internal collections/arrays and immutable implementations may safely return the same instance.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/CopyObject.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/DelegatedCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/DelegatedCodec.java

## Purpose
Builds a codec for type `T` by converting to and from a delegate codec type.

## Important APIs, Types, And Functions
Constructor inputs are delegate `Codec<DELEGATE>`, forward conversion, backward conversion, target class, and `CopyType`. Methods forward buffer and byte-array serialization through the delegate. `decodeOnly` builds codecs without backward conversion. `CopyType` supports `DEEP`, `SHALLOW`, and `UNSUPPORTED`.

## Control Flow
Serialization applies `backward` then delegate encoding. Deserialization delegates then applies `forward`. `copyObject()` returns the same object for shallow, throws for unsupported, calls `CopyObject.copyObject()` when available, or deep-copies by delegate copy plus forward/backward conversion.

## State And Persistence
State is immutable conversion configuration. Persisted layout is exactly the delegate codec layout.

## Dependencies And Integration Points
Depends on Ratis `CheckedFunction` and `JavaUtils`, and is widely useful for wrappers around protobuf, strings, or primitive keys.

## Risks
Forward/backward functions must be inverse-compatible or persisted data becomes lossy. `decodeOnly` cannot serialize and will fail late if used for writes. Deep-copy error wrapping converts `CodecException` to `IllegalStateException`.

## Test Signals
Round-trip tests should cover byte-array and buffer paths, all copy types, `CopyObject` implementations, and decode-only failure on serialization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/DelegatedCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/IntegerCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/IntegerCodec.java

## Purpose
Serializes `Integer` values as four-byte big-endian data.

## Important APIs, Types, And Functions
Singleton `IntegerCodec.get()` implements `Codec<Integer>`, supports `CodecBuffer`, and exposes helpers `toByteArray(int)` and `fromByteArray(byte[])`.

## Control Flow
Buffer encoding allocates `Integer.BYTES` and writes `putInt`. Byte-array encoding returns null for null object or wraps a four-byte array and writes the value. Deserialization wraps input bytes and reads `getInt`.

## State And Persistence
No mutable state. Persistent format is Java `ByteBuffer` big-endian integer encoding.

## Dependencies And Integration Points
Used for DB keys/values that need stable numeric byte representations and direct-buffer serialization.

## Risks
`fromByteArray` does not validate exact length beyond `ByteBuffer.getInt()` behavior; extra bytes are ignored and short arrays throw runtime exceptions. Null persisted values are allowed here.

## Test Signals
Codec round-trip tests should include positive, negative, zero, min/max, null byte-array path, and malformed lengths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/IntegerCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/IteratorType.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/IteratorType.java

## Purpose
Describes whether a DB iterator should read keys, values, both, or neither.

## Important APIs, Types, And Functions
Enum constants are `NEITHER`, `KEY_ONLY`, `VALUE_ONLY`, and `KEY_AND_VALUE`, each with a bit mask. Methods `readKey()` and `readValue()` inspect the mask.

## Control Flow
The two query methods use bitwise comparison against `KEY_ONLY.mask` and `VALUE_ONLY.mask`.

## State And Persistence
Enum constants are immutable; there is no persistence.

## Dependencies And Integration Points
Intended for table iteration APIs where avoiding unused key/value decoding saves IO and CPU.

## Risks
Adding new mask values must preserve bit semantics. Callers must not assume ordinal values.

## Test Signals
Simple enum tests should assert key/value booleans for all four constants and any DB iterator behavior that uses them.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/IteratorType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/LongCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/LongCodec.java

## Purpose
Serializes `Long` values as eight-byte big-endian data.

## Important APIs, Types, And Functions
Singleton `LongCodec.get()` implements `Codec<Long>`, supports `CodecBuffer`, and provides `toByteArray(long)` and `fromByteArray(byte[])`.

## Control Flow
Buffer path writes `putLong` into an eight-byte buffer. Byte-array path returns null for null object and otherwise writes/reads via `ByteBuffer`.

## State And Persistence
No mutable state. Persistent format is Java `ByteBuffer` big-endian long encoding.

## Dependencies And Integration Points
Used by DB tables needing numeric key/value codecs with direct buffer support.

## Risks
Malformed byte-array lengths are not explicitly checked; short arrays throw and extra bytes are ignored. Null handling differs from non-null interface comments.

## Test Signals
Round trips should cover zero, negative, min/max, null byte-array values, direct/heap buffer paths, and invalid lengths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/LongCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/Proto2Codec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/Proto2Codec.java

## Purpose
Provides cached codecs for `com.google.protobuf.MessageLite` protobuf v2 messages.

## Important APIs, Types, And Functions
Static `get(T t)` returns a cached codec keyed by message class. Each codec stores message class and parser. It supports `CodecBuffer`, byte-array serialization, parsing, and immutable copy semantics.

## Control Flow
`get()` uses `ConcurrentHashMap.computeIfAbsent`. Buffer serialization precomputes serialized size, allocates that exact size, and writes via `message.writeTo(OutputStream)`. Buffer parsing reads through `ByteBufInputStream` and closes it. Byte-array parsing delegates to `parser.parseFrom`.

## State And Persistence
State is the static class-to-codec cache and immutable parser metadata. Persisted format is standard protobuf bytes.

## Dependencies And Integration Points
Depends on unshaded Google protobuf v2 APIs, `CodecBuffer`, and HDDS `IOUtils`. Used for legacy protobuf metadata types.

## Risks
Cache keys ignore parser options beyond class. Parse errors are wrapped as `CodecException` on buffer path and via interface wrapping on byte-array path. Large messages allocate exact buffers and require release by callers.

## Test Signals
`Proto2CodecTestBase` and `CodecTestUtil` patterns cover round trips. Tests should include invalid bytes, class cache reuse, direct/heap buffers, and leak checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/Proto2Codec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/Proto3Codec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/Proto3Codec.java

## Purpose
Provides cached codecs for Ratis-shaded protobuf v3 `MessageLite` messages.

## Important APIs, Types, And Functions
Static `get(T)` and `get(T, boolean allowInvalidProtocolBufferException)` return codecs. Methods support `CodecBuffer`, byte-array serialization, parsing from read-only `ByteBuffer`, and immutable copy behavior.

## Control Flow
The first call per class populates a `ConcurrentHashMap`. Buffer serialization allocates serialized size and writes through shaded `CodedOutputStream.newInstance(ByteBuffer)`. Deserialization returns null on parse error when `allowInvalidProtocolBufferException` is true; otherwise it throws or wraps the parse exception.

## State And Persistence
State is the static class-to-codec cache and per-codec parser flag. Persisted format is standard shaded protobuf bytes.

## Dependencies And Integration Points
Depends on Ratis-shaded protobuf APIs and Ozone codec infrastructure. Used for Ratis/HDDS proto3 metadata without mixing unshaded proto classes.

## Risks
The cache is keyed only by class, so the first `allowInvalidProtocolBufferException` value wins for that class; later callers requesting a different behavior may not get it. Returning null on invalid bytes can mask corruption if used outside tolerant paths.

## Test Signals
Tests should cover parse failure with both allow modes, cache behavior when modes differ, buffer and byte-array round trips, and direct/heap leak checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/Proto3Codec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/PutToByteBuffer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/PutToByteBuffer.java

## Purpose
Package-private functional interface for writing source data into a `ByteBuffer` while reporting required size or unavailability.

## Important APIs, Types, And Functions
`PutToByteBuffer<E extends Exception>` extends Ratis `CheckedFunction<ByteBuffer, Integer, E>`.

## Control Flow
Implementations receive a `ByteBuffer`, may write full or partial data, return required size when source exists, and return null when the source is unavailable.

## State And Persistence
The interface owns no state. It is a callback over transient buffers.

## Dependencies And Integration Points
Used by `CodecBuffer.putFromSource`, `Buffer.getFromDb`, and `StringCodecBase` encoding.

## Risks
Implementations must report sizes consistently with bytes written. Returning negative sizes violates `CodecBuffer` preconditions. Partial writes require caller retry logic to be correct.

## Test Signals
Tests should exercise null result, exact result, required-size-larger-than-capacity, negative size rejection, and exception propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/PutToByteBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/ShortCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/ShortCodec.java

## Purpose
Serializes `Short` values as two-byte big-endian data.

## Important APIs, Types, And Functions
Singleton `ShortCodec.get()` implements `Codec<Short>` and supports `CodecBuffer`.

## Control Flow
Buffer serialization writes `putShort` into a two-byte buffer. Byte-array serialization wraps a two-byte array and writes the short. Deserialization reads `getShort`.

## State And Persistence
No mutable state. Persistent format is Java `ByteBuffer` big-endian short encoding.

## Dependencies And Integration Points
Used for DB metadata fields that need compact numeric encoding.

## Risks
Unlike `IntegerCodec` and `LongCodec`, `toPersistedFormat` does not accept null. Length validation is implicit through `ByteBuffer`, so extra bytes are ignored and short arrays fail at runtime.

## Test Signals
Round trips should cover min/max, negative, zero, direct/heap buffers, null handling, and malformed byte lengths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/ShortCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/StringCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/StringCodec.java

## Purpose
Provides the canonical UTF-8 string codec for Ozone DB metadata.

## Important APIs, Types, And Functions
`StringCodec.get()` returns a UTF-8 codec with fallback decoding; `getCodecNoFallback()` returns a strict UTF-8 `Codec<String>` implemented by an anonymous `StringCodecBase`.

## Control Flow
The class only constructs singleton codec instances and delegates all encoding/decoding logic to `StringCodecBase`.

## State And Persistence
No mutable state beyond singleton instances. Persistent layout is UTF-8 encoded bytes.

## Dependencies And Integration Points
Depends on `StringCodecBase` and Java `StandardCharsets.UTF_8`. Used for string DB keys/values and delegated codecs.

## Risks
Fallback decoding can preserve compatibility with older data but may hide malformed UTF-8. Callers needing corruption detection should use the no-fallback codec.

## Test Signals
Tests should cover ASCII, multibyte UTF-8, malformed bytes with fallback and no-fallback codecs, and `CodecBuffer` heap/direct round trips.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/StringCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/StringCodecBase.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/StringCodecBase.java

## Purpose
Abstract charset-based implementation for string codecs with strict encoding and optional fallback decoding.

## Important APIs, Types, And Functions
The class stores `Charset`, fixed-length status, and `maxBytesPerChar`. Important methods are `newEncoder`, `newDecoder`, `isFixedLength`, `toCodecBuffer`, `fromCodecBuffer`, `toPersistedFormat`, `fromPersistedFormat`, `string2Bytes`, `decodeNoFallback`, and nested `WithFallback`.

## Control Flow
Encoding computes an upper-bound size, encodes through a `CharsetEncoder` configured to `REPORT` malformed/unmappable input, and either uses exact array size for fixed-width charsets or a heap `CodecBuffer` for variable width. Buffer serialization allocates the upper bound and sets writer index based on actual encoded bytes. Strict decode throws `CodecException`; fallback logs the strict failure then calls `StringUtils.bytes2String`.

## State And Persistence
Immutable codec configuration only. Persistent bytes are determined by the configured charset.

## Dependencies And Integration Points
Used by `StringCodec` and any future charset-specific string codecs. Depends on Java NIO charset APIs, `CodecBuffer`, Ratis preconditions, and HDDS string utilities.

## Risks
The max-bytes-per-char value must be an integer; unusual charsets can throw at construction. Fallback logs can be noisy on corrupt data. `StringUtils.bytes2String` compatibility behavior may not match strict charset semantics.

## Test Signals
Tests should include variable-length UTF-8, malformed byte arrays, size mismatch protection, direct and heap buffers, fallback log paths, and fixed-length charset behavior if a subclass is added.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/StringCodecBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/UuidCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/UuidCodec.java

## Purpose
Serializes Java `UUID` values as fixed 16-byte big-endian most/least significant bits.

## Important APIs, Types, And Functions
Singleton `UuidCodec.get()` implements `Codec<UUID>`. `getSerializedSize()` returns 16. Buffer and byte-array paths write/read two longs.

## Control Flow
Serialization writes `getMostSignificantBits()` then `getLeastSignificantBits()`. Deserialization validates byte-array length exactly 16 and constructs a new `UUID` from two longs.

## State And Persistence
No mutable state. Persistent layout is a stable 16-byte UUID representation.

## Dependencies And Integration Points
Used for DB keys/values needing compact UUID storage and direct-buffer support.

## Risks
Only byte-array deserialization checks exact length; buffer deserialization assumes enough readable bytes and ignores trailing bytes. Null UUIDs are not supported.

## Test Signals
Round trips should cover random UUIDs, all-zero UUID, max UUID, invalid lengths, and heap/direct `CodecBuffer`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/UuidCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/package-info.java

## Purpose
Documents the `org.apache.hadoop.hdds.utils.db` package as common DB utility classes.

## Important APIs, Types, And Functions
The file contains package Javadoc and the package declaration only.

## Control Flow
No runtime control flow.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Provides package-level documentation for codec, buffer, and iterator utility classes.

## Risks
Documentation is broad and may not describe newer direct-buffer semantics.

## Test Signals
No unit tests are needed beyond Javadoc/package compilation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/io/ByteBufferInputStream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/io/ByteBufferInputStream.java

## Purpose
Adapts a `ByteBuffer` to a read-only `InputStream`.

## Important APIs, Types, And Functions
Constructor stores `buffer.asReadOnlyBuffer()`. Overrides `read()` and `read(byte[], int, int)`. Package-visible `assertArrayIndex` validates array bounds and overflow.

## Control Flow
Single-byte read returns `-1` at EOF or the next unsigned byte. Bulk read validates arguments, returns `0` for zero-length reads, returns `-1` if no remaining bytes, then copies the minimum of requested and remaining bytes.

## State And Persistence
State is the read-only duplicate buffer and its position. The original buffer position is unaffected. No persistence.

## Dependencies And Integration Points
Useful anywhere APIs require `InputStream` over in-memory `ByteBuffer` content.

## Risks
No `mark/reset` support beyond `InputStream` defaults. It is not synchronized. The constructor does not null-check explicitly, so null produces `NullPointerException`.

## Test Signals
Tests should cover single and bulk reads, EOF, zero-length reads, invalid bounds, overflow bounds, read-only behavior, and original-position independence.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/io/ByteBufferInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/io/LengthOutputStream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/io/LengthOutputStream.java

## Purpose
Counts bytes written while forwarding all writes to an underlying `OutputStream`.

## Important APIs, Types, And Functions
Extends `FilterOutputStream`. Public method `getLength()` returns an `int` counter. Overrides `write(int)` and `write(byte[], int, int)`.

## Control Flow
Each write delegates to `out` first, then increments length by one or by `len`. Exceptions from the underlying stream prevent counter increments.

## State And Persistence
State is an in-memory `int length`; output persistence is owned by the wrapped stream.

## Dependencies And Integration Points
Can be used when serialization code needs to measure emitted byte length without buffering all output.

## Risks
The counter can overflow beyond `Integer.MAX_VALUE`. It does not override `write(byte[])`, but `FilterOutputStream` routes that to the three-argument method. Not synchronized.

## Test Signals
Tests should cover all write overloads, exception-before-count behavior, flush/close forwarding, and large-count overflow expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/io/LengthOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/io/RandomAccessFileChannel.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/io/RandomAccessFileChannel.java

## Purpose
Owns a read-only `RandomAccessFile` and `FileChannel` with synchronized open, seek, read-fill, and close helpers.

## Important APIs, Types, And Functions
Public methods are `isOpen`, `open(File)`, `position(long)`, `read(ByteBuffer)`, and `close`. Fields track the file, `RandomAccessFile`, and channel.

## Control Flow
`open()` asserts no current file, opens the file in `"r"` mode, and stores channel state. `position()` seeks only when the requested position differs. `read()` loops until the target buffer is full or EOF returns false. `close()` clears `blockFile`, closes channel and RAF independently, logs close failures, and nulls fields.

## State And Persistence
State is the currently open file/channel and position in the OS file handle. The class does not mutate file contents.

## Dependencies And Integration Points
Depends on Java IO/NIO, Ratis `Preconditions`, and SLF4J. Used where block/chunk readers need positioned full-buffer reads.

## Risks
All methods synchronize on the object, so concurrent reads serialize. `isOpen()` is based on `blockFile`, not channel state. `read()` can spin if a custom channel returns zero while the buffer remains writable, though file channels normally progress or EOF.

## Test Signals
`TestRandomAccessFileChannel` covers open/close, positioning, full and partial reads, EOF, and internal cleanup. Additional tests can inject close exceptions and concurrent access.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/io/RandomAccessFileChannel.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/io/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/io/package-info.java

## Purpose
Documents the IO utility package.

## Important APIs, Types, And Functions
Contains only package Javadoc and `package org.apache.hadoop.hdds.utils.io;`.

## Control Flow
No runtime behavior.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Provides package-level documentation for stream and file-channel helpers.

## Risks
The wording is minimal and does not enumerate the package's stream/channel utilities.

## Test Signals
Compilation/Javadoc generation is sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/io/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/package-info.java

## Purpose
Documents the `org.apache.hadoop.hdds.utils` package.

## Important APIs, Types, And Functions
Contains only package-level Javadoc and the package declaration.

## Control Flow
No runtime behavior.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Labels a broad package containing HDDS configuration, scheduling, locking, version, retry, ID, cache, and window utilities.

## Risks
The comment says "SCM related utils" even though this package now includes broader HDDS utilities.

## Test Signals
Compilation and Javadoc checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/io_/retry/CallReturn.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/io_/retry/CallReturn.java

## Purpose
Internal value object representing one retry-proxy invocation outcome: returned value, thrown exception, or retry instruction.

## Important APIs, Types, And Functions
Package-private `CallReturn` has enum `State { RETURNED, EXCEPTION, RETRY }`, static singleton `RETRY`, constructors for return values and throwables, `getState()`, and `getReturnValue()`.

## Control Flow
`getReturnValue()` rethrows the stored throwable for `EXCEPTION`, returns the stored value for `RETURNED`, and rejects use when state is `RETRY`.

## State And Persistence
Immutable per-call result state only; no persistence.

## Dependencies And Integration Points
Used by `RetryInvocationHandler.Call.invokeOnce()` to separate retry loop control from method result/exception propagation.

## Risks
It stores `Throwable`, so `getReturnValue()` can throw non-`Exception` errors. `RETRY` carries no delay data; delay and failover state live in the surrounding call object.

## Test Signals
`TestRetryProxy` indirectly covers retry handling. Direct tests could assert returned null values, exception propagation, and invalid `RETRY.getReturnValue()`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/io_/retry/CallReturn.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/io_/retry/RetryInvocationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/io_/retry/RetryInvocationHandler.java

## Purpose
Dynamic-proxy invocation handler that applies Hadoop retry and failover policy to method calls, including RPC call ID/retry-count propagation.

## Important APIs, Types, And Functions
`RetryInvocationHandler<T>` implements `RpcInvocationHandler`. Important nested types are `Call`, `Counters`, `ProxyDescriptor`, and `RetryInfo`. Key methods are `invoke`, `handleException`, `invokeMethod`, `isRpcInvocation`, `close`, and `getConnectionId`.

## Control Flow
`invoke()` detects whether the target is an RPC proxy, assigns a call ID, and loops while `Call.invokeOnce()` returns `RETRY`. A call invokes the method, catches exceptions, computes `RetryInfo` from the policy and idempotence annotations, sleeps until retry time, optionally performs failover once per expected failover count, increments retry/failover counters, and retries. Fail decisions rethrow the selected exception.

## State And Persistence
State includes current proxy provider/proxy, failover count, successful-call flag, a set of proxies failed at least once for log suppression, default and per-method policies, and per-call counters. No persistence.

## Dependencies And Integration Points
Integrates Hadoop retry annotations, `FailoverProxyProvider`, `MultiException`, Ozone-shaded IPC classes, `Client.setCallIdAndRetryCount`, `ProtocolTranslator`, and `RPC.getConnectionIdForProxy`.

## Risks
`failedAtLeastOnce` is a plain `HashSet` touched without synchronization. Method policy lookup by name ignores overload signatures. `SET_CALL_ID_FOR_TEST` is a global thread-local test hook. Reflection uses deprecated `isAccessible`.

## Test Signals
`TestRetryProxy` covers retry policies, failover behavior, `isRpcInvocation`, and failure limits. OM HA follower-read tests exercise call-ID test behavior and integration failover.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/io_/retry/RetryInvocationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/io_/retry/RetryPolicies.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/io_/retry/RetryPolicies.java

## Purpose
Factory and implementation collection for Hadoop `RetryPolicy` strategies used by local tasks and RPC proxies.

## Important APIs, Types, And Functions
Public policies/factories include `TRY_ONCE_THEN_FAIL`, `RETRY_FOREVER`, `retryForeverWithFixedSleep`, `retryUpToMaximumCountWithFixedSleep`, `exponentialBackoffRetry`, and `failoverOnNetworkException`. Nested implementations include `TryOnceThenFail`, `RetryForever`, `RetryLimited`, `RetryUpToMaximumCountWithFixedSleep`, `ExponentialBackoffRetry`, and `FailoverOnNetworkExceptionRetry`.

## Control Flow
Limited policies fail when retry count reaches max and otherwise return retry with fixed or exponential randomized delay. Network failover policy fails on max failovers/retries, SASL failures, invalid tokens, and access denial; failovers on connect/EOF/no-route/unknown-host/timeouts and idempotent socket IO; retries retriable exceptions; delegates all other exceptions to fallback.

## State And Persistence
Policy instances are immutable configuration holders except cached `toString()` in `RetryLimited`. No persistence.

## Dependencies And Integration Points
Depends on Hadoop `RetryPolicy`, IPC `RemoteException`/`RetriableException`, network exceptions, security exceptions, SASL, and Java time units. Used by `RetriableTask`, `Client.ConnectionId`, and `RetryInvocationHandler`.

## Risks
`calculateExponentialTime` can cap to zero when `maxDelayBase` is zero, making failover retries immediate. Retry/failover counters must be interpreted consistently by callers. Wrapped access-control detection walks causes and may classify broad failures as non-retriable.

## Test Signals
`TestRetryProxy` covers fixed, forever, exponential, failover, retriable, and access-control cases. Additional tests should cover zero cap, SASL cause chains, and retry-vs-failover counter boundaries.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/io_/retry/RetryPolicies.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/io_/retry/RetryProxy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/io_/retry/RetryProxy.java

## Purpose
Factory for dynamic proxies whose method calls are handled by `RetryInvocationHandler`.

## Important APIs, Types, And Functions
`create(Class<T>, T implementation, RetryPolicy)` wraps a concrete implementation in `DefaultFailoverProxyProvider`. `create(Class<T>, FailoverProxyProvider<T>, RetryPolicy)` builds a JDK dynamic proxy implementing the requested interface.

## Control Flow
Both factories end in `Proxy.newProxyInstance` using the provider interface class loader and a new retry handler.

## State And Persistence
No static mutable state. Each created proxy owns handler/provider state in memory.

## Dependencies And Integration Points
Depends on Java reflection proxy APIs and Hadoop retry/failover provider interfaces. Used by RPC clients and local retry wrappers.

## Risks
The returned type is `Object`, so callers must cast. The proxy implements only the supplied `iface`; extra implementation interfaces are not exposed. Class-loader mismatches can fail at proxy creation.

## Test Signals
`TestRetryProxy` validates creation, retries, failovers, and annotation-based idempotence behavior through this factory.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/io_/retry/RetryProxy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/AlignmentContext.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/AlignmentContext.java

## Purpose
Interface for propagating and validating replicated state alignment information through IPC request and response headers.

## Important APIs, Types, And Functions
Methods are `updateResponseState`, `receiveResponseState`, `updateRequestState`, `receiveRequestState`, `getLastSeenStateId`, and `isCoordinatedCall`.

## Control Flow
Client-side code calls `updateRequestState` before sending and `receiveResponseState` after success. Server-side code calls `receiveRequestState` while handling request headers and `updateResponseState` while building response headers. Implementations decide whether a protocol/method is coordinated and may reject requests via `IOException`.

## State And Persistence
This interface owns no state; implementations maintain last-seen state IDs and any synchronization thresholds.

## Dependencies And Integration Points
Uses IPC protobuf request/response header builders. `Client.Call` stores an optional `AlignmentContext` and updates it on successful responses.

## Risks
Incorrect implementation can allow stale reads or reject valid calls. Method-name/protocol-name classification must match generated RPC names.

## Test Signals
Tests should cover request header population, response state receipt, threshold rejection, and coordinated-call classification in OM/SCM HA paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/AlignmentContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/CallQueueManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/CallQueueManager.java

## Purpose
Wraps an IPC server call queue and scheduler, adding priority scheduling, optional client backoff, and queue-overflow exceptions.

## Important APIs, Types, And Functions
`CallQueueManager<E extends Schedulable>` extends `AbstractQueue` and implements `BlockingQueue`. Key methods create scheduler/queue instances reflectively, `put`, `add`, `offer`, `take`, `poll`, `peek`, `remainingCapacity`, `drainTo`, scheduler helpers, and nested `CallQueueOverflowException`.

## Control Flow
Construction reads priority levels, builds scheduler and queue via preferred constructors. `put()` blocks unless backoff is enabled; with backoff it checks `scheduler.shouldBackOff`. `add()` maps queue-full or scheduler backoff to `CallQueueOverflowException.DISCONNECT`. Consumers read from `takeRef`; producers write through `putRef`.

## State And Persistence
State is active backing queue references, scheduler, and volatile backoff flag. No persistence. Atomic references are structured for queue swapping, though this file does not expose a swap method.

## Dependencies And Integration Points
Integrates server `Schedulable`, `RpcScheduler`, `DecayRpcScheduler`, `FairCallQueue`, `ProcessingDetails`, Hadoop `Configuration`, UGI, and IPC protobuf status codes.

## Risks
Reflection constructor matching can fail at runtime for custom queues/schedulers. `putRef`/`takeRef` can diverge in future swap logic, so methods intentionally choose one side. `take()` polls every second, so shutdown/empty waits are not immediate. Backoff always uses `DISCONNECT` here.

## Test Signals
Useful tests cover constructor fallback order, priority-level config parsing, queue-full behavior, backoff decisions, custom overflow exceptions, scheduler metric hooks, and blocking `take()` interruption.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/CallQueueManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/CallerContext.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/CallerContext.java

## Purpose
Immutable caller-context metadata for RPC audit attribution, with optional signature and thread-local current context.

## Important APIs, Types, And Functions
Main APIs are `getContext`, `getSignature`, `isContextValid`, `toString`, nested `Builder`, `getCurrent`, and `setCurrent`.

## Control Flow
Builder stores context and copies non-empty signature bytes. `toString()` returns empty string for invalid context or `context:signatureAsUtf8` when a signature exists. Static current context uses an `InheritableThreadLocal`.

## State And Persistence
Instances are immutable and defensively copy signatures on build and read. Current context is per-thread inherited state. No persistence.

## Dependencies And Integration Points
Used by IPC scheduling/audit paths and Ozone identity provider tests. Depends on Commons Lang builders for equality/hash and UTF-8 for signature rendering.

## Risks
`hashCode()` only appends context while `equals()` includes signature; this violates the usual hash/equals contract for different signatures with same context. Inheritable thread locals can leak caller context into worker threads if not cleared.

## Test Signals
`TestOzoneIdentityProvider` exercises caller-context extraction. Additional tests should cover signature defensive copy, equals/hash behavior, invalid contexts, and inherited-thread cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/CallerContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/Client.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/Client.java

## Purpose
Implements the Hadoop-style IPC client used by Ozone's shaded IPC stack, including connection pooling, request multiplexing, SASL negotiation, pings, retries, response demultiplexing, and call lifecycle management.

## Important APIs, Types, And Functions
Important APIs include ping/timeout config helpers, `call`, `stop`, `close`, `nextCallId`, and `ConnectionId.getConnectionId`. Nested types are `Call`, `Connection`, `Connection.PingInputStream`, `Connection.RpcRequestSender`, `ConnectionId`, and `IpcStreams`.

## Control Flow
`call()` creates a `Call`, attaches optional `AlignmentContext`, obtains or creates a pooled `Connection`, serializes and queues the request, then waits for completion. `Connection.setupIOstreams()` establishes sockets, writes the IPC header, performs SASL if needed, writes connection context, starts the receiver thread and request-sender thread. The sender serializes request buffers to the socket; the receiver reads framed responses, checks client ID, parses headers, updates alignment state on success, completes matching calls, or closes the connection on fatal errors.

## State And Persistence
Client state includes a concurrent connection map, running flag, ref count, socket factory, value class, configuration, client UUID bytes, and per-thread call ID/retry count. Each connection owns socket/streams, active call table, retry config, SASL state, activity timestamps, close reason, and request queue. No durable persistence is owned.

## Dependencies And Integration Points
Integrates Hadoop configuration/security/UGI, NetUtils, SASL RPC client, RPC header protobufs, `RpcWritable`, `ResponseBuffer`, `RetryPolicies`, `AlignmentContext`, `RemoteException`, and server IPC framing constants. `RetryInvocationHandler` injects call ID and retry count for RPC retries.

## Risks
This is a high-concurrency class: call table cleanup, connection replacement, sender/receiver shutdown, and interrupt handling must stay consistent. Client ID mismatch closes calls. SASL fallback is security-sensitive. `ConnectionId.equals()` includes many config fields but not all constructor fields such as max socket timeout retries. Large responses are bounded only by configured max length.

## Test Signals
Coverage should include connection reuse, stop behavior, call interruption, response demux, fatal vs error responses, SASL success/fallback/failure, ping timeouts, address refresh, max response length, and alignment-context state. OM HA and secure-cluster integration tests exercise important RPC paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/Client.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ClientCache.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ClientCache.java

## Purpose
Caches `Client` instances by `SocketFactory` and reference-counts shared IPC clients.

## Important APIs, Types, And Functions
Public methods are `getClient(Configuration, SocketFactory, Class<? extends Writable>)`, overloads with defaults, `stopClient`, and `clearCache`.

## Control Flow
`getClient` synchronizes, creates a new `Client` when no factory entry exists, or increments the existing client's ref count. `stopClient` decrements under lock, removes the client when count reaches zero, and then stops it outside the synchronized block. `clearCache` stops all clients and clears the map.

## State And Persistence
State is a process-local `HashMap<SocketFactory, Client>` and client ref counts. No persistence.

## Dependencies And Integration Points
Used by RPC layers that share IPC clients across protocol proxies. Depends on Hadoop `Configuration`, `Writable`, `ObjectWritable`, and Java `SocketFactory`.

## Risks
Cache keying only by `SocketFactory` means different configurations/value classes can share a client; the comment acknowledges timeout/pooling tradeoffs. `clearCache()` is not synchronized and can race with `getClient`/`stopClient`.

## Test Signals
Tests should verify reuse by factory, ref-count stop behavior, default overloads, config-sharing semantics, and concurrent clear/get behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ClientCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ClientId.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ClientId.java

## Purpose
Generates and converts UUID-based 16-byte IPC client IDs.

## Important APIs, Types, And Functions
Constants are `BYTE_LENGTH = 16` and `shiftWidth = 8`. APIs are `getClientId`, `toString(byte[])`, `getMsb`, `getLsb`, and `toBytes(String)`.

## Control Flow
`getClientId()` generates a random UUID and writes MSB/LSB to a 16-byte `ByteBuffer`. `toString()` accepts null/empty as empty string, validates 16 bytes, reconstructs UUID pieces manually, and formats. `toBytes()` accepts null/empty as empty array or parses UUID string.

## State And Persistence
No mutable state. Client IDs are transmitted in RPC headers and can be represented as bytes or UUID strings.

## Dependencies And Integration Points
Used by `Client` for per-client identity and response validation. Depends on Java UUID/ByteBuffer and Guava preconditions.

## Risks
Null and empty encode to empty string/array rather than a 16-byte UUID, so callers must distinguish absent ID from generated ID. Manual MSB/LSB extraction must stay big-endian compatible with `ByteBuffer.putLong`.

## Test Signals
Tests should cover UUID bytes/string round trips, null/empty conversions, invalid lengths, invalid UUID strings, and compatibility with `UuidCodec`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ClientId.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/CostProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/CostProvider.java

## Purpose
Defines the pluggable cost calculation contract used by `DecayRpcScheduler` to account for RPC operation cost.

## Important APIs, Types, And Functions
The interface has `init(String namespace, Configuration conf)` and `getCost(ProcessingDetails details)`.

## Control Flow
Implementations initialize themselves from namespaced configuration, then compute a long cost from `ProcessingDetails` for each RPC.

## State And Persistence
The interface owns no state. Implementations may hold configuration-derived weights in memory; scheduler accounting uses returned costs.

## Dependencies And Integration Points
Configured through Hadoop `CommonConfigurationKeys.IPC_COST_PROVIDER_KEY` and consumed by `DecayRpcScheduler`. Depends on `ProcessingDetails` timing/cost metadata.

## Risks
Bad implementations can return negative, zero, or excessively large costs and distort scheduling fairness. Namespace parsing must match server IPC config keys.

## Test Signals
Tests should cover default and weighted providers, namespaced config loading, edge-case `ProcessingDetails`, and scheduler priority changes driven by computed cost.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/CostProvider.java -->
