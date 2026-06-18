# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.3.xml lines 18115-24646

## Research scope

This chunk is a JDiff XML API snapshot for Apache Hadoop Common 3.3.3, not Java implementation source. The selected range begins at the tail of `org.apache.hadoop.fs.statistics.IOStatistics`, covers the filesystem I/O statistics support package, Hadoop HA service and fencing contracts, protocol-buffer bridge interfaces, and a large part of `org.apache.hadoop.io` serialization APIs through the opening of `WritableComparator`. Conclusions are based on public signatures, inheritance, field constants, declared exceptions, deprecation metadata, and embedded Javadocs.

## Purpose

The range documents public compatibility contracts for three adjacent Hadoop Common areas.

The `org.apache.hadoop.fs.statistics` section standardizes low-cost per-instance I/O metrics. It defines snapshots, aggregation, logging helpers, mean-statistic arithmetic, and a common vocabulary of operation/stream statistic names used by filesystem and object-store implementations.

The `org.apache.hadoop.ha` section defines administrative service-state control for highly available Hadoop services. It covers health checks, transitions to active/standby/observer states, service target metadata, fencing hooks, and exception types used by failover controllers and health monitors.

The `org.apache.hadoop.io` section defines Hadoop's core binary serialization and comparison framework. It includes primitive and array `Writable` wrappers, map-backed writables with per-instance class registries, byte/text comparable types, generic/object writables, sequence-file writer factory APIs, file helpers such as `MapFile` and `SetFile`, stringification, checksums, utility I/O operations, and the base `Writable`/`WritableComparable` contracts used by MapReduce, RPC payloads, and on-disk data formats.

## Important APIs and types

`IOStatistics` ends in this range with `MIN_UNSET_VALUE` and `MAX_UNSET_VALUE`, sentinel constants used when minimum/maximum statistics have never been recorded. `IOStatisticsAggregator.aggregate(IOStatistics)` is the opt-in contract for merging another statistics instance into a current accumulator and returns whether a non-null source was aggregated.

`IOStatisticsLogging` is a final utility class for robust logging of statistics. It extracts statistics from an `IOStatistics` or `IOStatisticsSource`, converts statistics to compact or sorted pretty strings, builds lazy stringifier objects for cheap log-argument use, and logs extracted statistics at debug or a named level. Its Javadocs explicitly say extraction exceptions are caught and downgraded to debug logging, so logging must not destabilize filesystem operations.

`IOStatisticsSnapshot` is a final, serializable, synchronized snapshot and accumulator implementing `IOStatistics` and `IOStatisticsAggregator`. It can be empty, constructed from a source, cleared, overwritten by `snapshot(source)`, or merged via `aggregate(source)`. It exposes synchronized metric maps for counters, gauges, minimums, maximums, and `MeanStatistic` values. Static `serializer()` and `requiredSerializationClasses()` integrate with Hadoop's JSON serialization and with safer Java deserialization allow-lists.

`IOStatisticsSupport` provides factory and helper entry points: `snapshotIOStatistics(statistics)`, an empty `snapshotIOStatistics()` accumulator, `retrieveIOStatistics(Object)` for direct statistics or source objects, and singleton stub duration tracker factories/trackers for no-op instrumentation paths.

`MeanStatistic` is a final serializable and cloneable mutable statistic with synchronized getters and mutators for sample count and sum. It normalizes invalid sample counts to an empty statistic, computes a mean, adds another mean statistic or a sample, supports `copy()`/`clone()`, and defines equality/hash/string behavior.

`StoreStatisticNames` and `StreamStatisticNames` are final constant catalogs. Store-level names include filesystem operations (`OP_OPEN`, `OP_CREATE`, `OP_RENAME`, `OP_DELETE`, ACL/xattr/status operations), object-store request counters (list, continue-list, bulk delete, metadata, copy, put, select), multipart upload counters, throttle/retry/request metrics, and suffixes such as `.min`, `.max`, `.mean`, and `.failures`. Stream-level names include read-open/close/abort counters, bytes read/discarded/skipped, seek and readFully operations, version mismatches, unbuffering, write exceptions, block upload queue/active/pending/committed counters, upload byte totals, queue wait/put request timing, remote read metrics, and block allocation/release counters.

`BadFencingConfigurationException`, `FailoverFailedException`, `HealthCheckFailedException`, and `ServiceFailedException` mark distinct HA failure modes: invalid fencing setup, overall failover failure, failed service health checks, and service transition/operation failure.

`FenceMethod` defines `checkArgs(String)` and `tryFence(HAServiceTarget, String)`. Fencing implementations validate configuration arguments before use and return a boolean success signal when attempting to isolate a target.

`HAServiceProtocol` is the service administration RPC contract. It exposes `monitorHealth()`, `transitionToActive(StateChangeRequestInfo)`, `transitionToStandby(StateChangeRequestInfo)`, `transitionToObserver(StateChangeRequestInfo)`, `getServiceStatus()`, and `versionID`. Methods declare `IOException`, `ServiceFailedException`, `AccessControlException`, and health-check failures as appropriate, so callers must distinguish transport/security failures from service-state failures.

`HAServiceProtocolHelper` wraps the same HA operations as static helper methods. Its role is to invoke service protocol methods and normalize remote failures for callers, especially failover-controller code.

`HAServiceTarget` is an abstract endpoint descriptor. It supplies RPC addresses for the service, health monitor, and ZKFC; an optional `NodeFencer`; fencing configuration checks; RPC proxy creation with retry/sleep controls; health-monitor proxy creation; ZKFC proxy creation; fencing parameter maps; transition-target HA state storage; auto-failover enablement; and observer-state support flags. `addFencingParameters(Map)` lets subclasses enrich the map passed to fencing methods.

`HAServiceProtocolPB` and `ZKFCProtocolPB` are protocol-buffer bridge interfaces extending generated protobuf blocking service interfaces plus `VersionedProtocol`, binding the public Java HA/ZKFC contracts to Hadoop IPC.

`AbstractMapWritable` is a configurable `Writable` base for map-like writables. It maintains a per-instance mapping between classes and small byte ids, supports class registration and copying, exposes `getClass(byte)`/`getId(Class)`, carries a `Configuration`, and serializes/deserializes the class-id map.

`ArrayFile`, `MapFile`, `BloomMapFile`, and `SetFile` are file-format helpers around sorted key/value storage. `ArrayFile` extends `MapFile` for dense integer-keyed arrays. `MapFile` exposes static `rename`, `delete`, `fix`, `main`, and file-name constants `INDEX_FILE_NAME` and `DATA_FILE_NAME`. `BloomMapFile` exposes deletion and bloom metadata constants. `SetFile` extends `MapFile` for set-like storage.

`ArrayPrimitiveWritable`, `ArrayWritable`, and `TwoDArrayWritable` serialize primitive arrays, one-dimensional writable arrays, and two-dimensional writable matrices. `ArrayPrimitiveWritable` preserves declared component type and can wrap primitive arrays. `ArrayWritable` carries a writable value class and supports conversion to strings or object arrays. `TwoDArrayWritable` carries a value class and serializes nested writable arrays.

`BinaryComparable` is the base for byte-backed comparable values. It requires subclasses to expose `getBytes()` and `getLength()`, then provides byte-wise comparison, equality, and hashing. `BytesWritable` and `Text` build on it.

Primitive wrapper writables include `BooleanWritable`, `ByteWritable`, `ShortWritable`, `IntWritable`, `LongWritable`, `FloatWritable`, `DoubleWritable`, `VIntWritable`, and `VLongWritable`. They generally provide default/value constructors, `set`, `get`, `readFields`, `write`, `equals`, `hashCode`, `compareTo`, and `toString`. `VIntWritable` and `VLongWritable` store values in Hadoop variable-length integer encodings.

`ByteBufferPool` defines `getBuffer(boolean direct, int length)` and `putBuffer(ByteBuffer)` for reusable heap/direct byte buffers. `ElasticByteBufferPool` implements the pool with elastic buffer allocation and return.

`CompressedWritable` is a base class for compressed serialized state. It serializes compressed data through `writeCompressed`, lazily inflates via `ensureInflated`, and asks subclasses to implement `readFieldsCompressed`.

`DataOutputOutputStream` adapts `DataOutput` to `OutputStream`, including a static `constructOutputStream(DataOutput)` and byte/array write overloads.

`Stringifier<T>` defines text serialization with `toString(T)`, `fromString(String)`, and `close()`. `DefaultStringifier<T>` implements it using Hadoop `Configuration` and a target class, plus static helpers to store/load one object or arrays in configuration keys.

`EnumSetWritable<E extends Enum<E>>` is a configurable writable collection for enum sets, preserving element type even when the set is empty. It extends `AbstractCollection`, implements `Writable`/`Configurable`, and exposes iterator, size, add, set/get, serialization, equality, hash, string, and configuration methods.

`GenericWritable` stores one writable instance from a subclass-provided whitelist returned by `getTypes()`. It carries configuration, delegates string form to the contained instance, and serializes the type choice plus value. `ObjectWritable` is broader: it stores declared class plus object instance, supports configurable `writeObject`/`readObject`, class loading, and configuration propagation.

`IOUtils` collects stream and filesystem utility operations: stream copying with explicit buffer sizes, counts, configuration-derived buffer sizes, and close policies; compressed-data reads wrapped as `IOException`; `readFully`; `skipFully`; cleanup helpers that ignore close failures; socket close; full writes to `WritableByteChannel` and positional `FileChannel`; directory listing that preserves `IOException`; file/channel fsync; exception wrapping with path/method context; and `readFullyToByteArray(DataInput)`. It exposes a public SLF4J `LOG`.

`MapWritable` and `SortedMapWritable` are mutable map implementations backed by `AbstractMapWritable`. `MapWritable` exposes standard map operations and writable serialization. `SortedMapWritable` exposes sorted-map navigation (`firstKey`, `lastKey`, `headMap`, `subMap`, `tailMap`, comparator) plus mutation, lookup, serialization, equality, and hashing.

`MD5Hash` is a writable comparable wrapper around a 16-byte MD5 digest. It supports construction from strings or bytes, reading/writing, static digest creation over strings/byte arrays/input streams, `MessageDigest` access, half/quarter digest extraction, equality, hashing, comparison, string conversion, and `MD5_LEN`.

`MultipleIOException` aggregates several `IOException` instances and exposes `getExceptions()` plus `createIOException(List)` for returning a single exception when multiple close or cleanup failures occur.

`NullWritable` is a singleton writable comparable carrying no data. `get()` returns the singleton; read/write are no-ops; comparison/equality/hash/string are stable.

`RawComparator<T>` extends `Comparator<T>` with byte-level `compare(byte[], int, int, byte[], int, int)`, allowing sort and shuffle code to compare serialized keys without full deserialization.

`SequenceFile` is the main flat binary key/value file format. This range includes default compression type getters/setters and many `createWriter` overloads. The preferred API is `createWriter(Configuration, SequenceFile.Writer.Option...)`; many older overloads are deprecated in favor of it. Non-deprecated overloads still support `FileSystem` or `FileContext`, key/value classes, buffer size, replication, block size, parent creation, compression type, codec, metadata, create flags, and create options. The Javadocs define uncompressed, record-compressed, and block-compressed formats, a common header, sync markers, metadata, compression codec fields, and `SYNC_INTERVAL`.

`Text` is Hadoop's UTF-8 byte-backed string type. It supports construction from strings, other `Text`, or bytes; byte copying and backing-array access; length; code-point lookup by byte position; substring find; setting from string/text/bytes; appending; clearing; string conversion; length-limited and known-length reading; skipping serialized text; writing; equality/hash; static decode/encode helpers with replacement control; `readString`/`writeString` with max-length overloads; UTF-8 validation; byte-buffer code-point extraction; UTF-8 length calculation; and `DEFAULT_MAX_LEN`.

`VersionedWritable` writes a version byte before subclass payload and checks it during `readFields`; subclasses implement `getVersion()`. `VersionMismatchException` reports a mismatch between serialized and current versions.

`Writable` defines Hadoop's simple serialization protocol over `DataOutput` and `DataInput`. `WritableComparable<T>` combines `Writable` and `Comparable<T>` and documents that stable `hashCode()` implementations matter for partitioning. `WritableComparator` begins at the end of this chunk as the comparator implementation for writable comparables; only its constructors are visible in this range.

## Control flow and behavior

The statistics APIs follow a capture, aggregate, and report flow. Producers expose `IOStatistics` maps. Consumers call `IOStatisticsSupport.retrieveIOStatistics(source)` when the source may be either the statistics object or an `IOStatisticsSource`. Snapshots either overwrite current maps from a source through `snapshot(source)` or merge into accumulated maps through `aggregate(source)`. Logging helpers delay string conversion until log evaluation and intentionally tolerate nulls, wrong source types, and extraction failures.

Mean-statistic behavior centers on synchronized mutation of `samples` and `sum`. Invalid or non-positive sample counts become an empty statistic. Adding a sample or another statistic mutates the current accumulator; `mean()` derives the average from the two counters.

HA control flow is RPC and failover-controller oriented. Health monitors call `monitorHealth()` and inspect `HAServiceStatus`. Failover controllers use `HAServiceTarget` to locate service, health, and ZKFC endpoints, construct proxies, verify fencing configuration, and inject target-specific fencing parameters. State transitions carry `StateChangeRequestInfo` so services can distinguish request sources and enforce authorization or policy. Fencing methods validate arguments before use and return a boolean success/failure signal when trying to isolate a stale active.

Writable control flow is explicit serialization into `DataOutput` and reconstruction from `DataInput`. Primitive writables write fixed or variable-length binary values. Array writables write element counts and then each element. Map writables write a class-id table followed by entries so dynamic writable types can be deserialized. `GenericWritable` selects among a bounded type whitelist. `ObjectWritable` writes declared class metadata and object payload, using `Configuration` for class loading. `VersionedWritable` inserts a version check before subclass fields.

Sequence-file writer creation is option-assembly flow. Modern callers build `Writer.Option` arrays and call the central factory. Older overloads progressively specify filesystem/context, path, key/value classes, compression, codec, metadata, progress, and file-creation settings before delegating internally to the writer implementation. The on-disk flow begins with a common header and sync marker, then writes records differently depending on no compression, record compression, or block compression.

Text and binary comparison flows avoid unnecessary object creation. `BinaryComparable` compares byte arrays directly. `RawComparator` permits serialized-key byte comparisons. `Text` tracks byte length separately from backing capacity, validates/decodes UTF-8 as needed, and can scan/find/codepoint-traverse without first converting the whole value to `String`.

`IOUtils` control flow is defensive around partial reads/writes and cleanup. `copyBytes`, `readFully`, `skipFully`, and channel `writeFully` loop until requested work completes or fail with `IOException`. Cleanup methods intentionally swallow close failures and are documented as exception-handler-only utilities. `wrapException` preserves or specializes important exception types while adding path and method diagnostics.

## State and persistence behavior

Most statistics objects are in-memory process-local metrics. `IOStatisticsSnapshot`, however, is explicitly serializable and JSON-serializable so frameworks can ship captured statistics back from distributed workers. The snapshot uses map fields for counters, gauges, min/max, and means; synchronized access indicates mutable shared state within a JVM, not atomic capture from arbitrary sources.

`StoreStatisticNames` and `StreamStatisticNames` persist only as stable public string constants. Their practical persistence impact is external: metrics sinks, logs, dashboards, and tests may key on exact names, so renaming or reclassifying constants would be a compatibility break.

HA service state lives in the target service and failover-controller ecosystem, not in these API descriptor objects. `HAServiceTarget` does carry local configuration-derived state such as transition-target HA status and exposes derived addresses, fencers, and fencing parameter maps. Fencing effects are external and operational: they may kill processes, revoke access, or otherwise isolate a target outside the JVM.

Writable objects persist their state directly to `DataOutput` streams. This is both wire format and file format for many Hadoop components. Stable serialization matters for MapReduce shuffle keys, RPC arguments, sequence files, map files, configuration-encoded stringified objects, and long-lived data files. `VersionedWritable` adds a version byte to support evolution but will throw `VersionMismatchException` unless subclasses handle mismatches.

`SequenceFile` persists a structured file with header metadata, key/value class names, compression flags, codec class, metadata, sync markers, and binary key/value records or compressed blocks. `MapFile`, `ArrayFile`, `BloomMapFile`, and `SetFile` layer indexed or set-like access patterns on persisted file structures. `MD5Hash` persists a fixed 16-byte digest. `Text` persists UTF-8 bytes preceded by a length encoded using Hadoop's variable-length integer convention.

Byte-array and buffer classes expose mutable backing storage. `BytesWritable.getBytes()` and `Text.getBytes()` return backing arrays whose valid content is bounded by length; capacity can exceed logical length. `ArrayPrimitiveWritable` wraps arrays and its Javadocs in adjacent API docs indicate no-copy behavior, so caller mutation can affect later serialization.

## Dependencies and integration points

Statistics APIs integrate with `IOStatisticsSource`, `DurationTracker`, `DurationTrackerFactory`, `JsonSerialization`, `MeanStatistic`, SLF4J logging, and filesystem/object-store implementations that publish metrics under the shared name constants.

HA APIs integrate with Hadoop IPC (`VersionedProtocol`), generated protobuf services, `ZKFCProtocol`, `NodeFencer`, `HAServiceStatus`, `StateChangeRequestInfo`, `Configuration`, security authorization (`AccessControlException`), network endpoints (`InetSocketAddress`), retry/sleep parameters, and service-specific subclasses of `HAServiceTarget`.

Writable APIs integrate with Java `DataInput`/`DataOutput`, `InputStream`/`OutputStream`, NIO `ByteBuffer`, `WritableByteChannel`, `FileChannel`, `File`, `FilenameFilter`, `Socket`, `Configuration`, `Configurable`, Hadoop `FileSystem`, `FileContext`, `Path`, create flags/options, `FSDataOutputStream`, `Progressable`, compression codecs, and Hadoop's sort/shuffle comparator stack.

Configuration integration is especially broad. `DefaultStringifier` stores serialized values in configuration keys. `EnumSetWritable`, `GenericWritable`, `ObjectWritable`, and `AbstractMapWritable` carry `Configuration` for nested values and class loading. `SequenceFile` consults or mutates configuration for default compression type.

## Risks and edge cases

`IOStatisticsSnapshot.snapshot()` is documented as not atomic through the support helper, so callers aggregating live mutable sources may observe mixed-time values. Snapshot map access is synchronized on the snapshot object, but that cannot make the original source's exported maps atomic.

Statistics logging intentionally catches exceptions. This is safe for production paths but can hide broken statistics providers unless debug logs or tests assert extraction behavior.

Mean statistics can lose information or overflow if sample sums grow past `long` capacity. Empty statistics and invalid sample counts are normalized, so tests must check both `samples` and `sum` rather than relying only on `mean()`.

Metric name constants are compatibility-sensitive. Downstream dashboards, object-store performance tests, and contract tests may assume exact strings and suffix semantics such as min/max/mean/failures.

HA transition APIs are high-risk operational controls. Callers must handle authorization, service failure, health-check failure, and network `IOException` distinctly. Observer-state support is optional, and `supportObserver()` must be checked before assuming observer transitions are valid.

Fencing configuration errors can make failover unsafe. `checkFencingConfigured()` and `FenceMethod.checkArgs()` need to be exercised before a failover event, not only after a stale active is suspected. A `false` fencing result must be treated as failure to isolate the previous active.

`HAServiceTarget` exposes several addresses that may differ: service RPC, health monitor RPC, and ZKFC RPC. Using the wrong endpoint can break health checks or administrative commands even if normal service RPC works.

Writable serialization requires a public no-arg constructor for many deserialization paths. Missing constructors, unstable `hashCode()`, non-deterministic comparison, or changed wire order will break MapReduce sorting, partitioning, RPC compatibility, and persisted data.

`AbstractMapWritable` uses byte ids for class mappings, so there is a practical limit on distinct writable classes in one map instance. Dynamic class-id state also means copies and reads must preserve the class table exactly.

Backing-array access in `BytesWritable` and `Text` is easy to misuse. Callers must honor logical length and avoid assuming the returned byte array is trimmed or immutable. `BytesWritable.setCapacity()`/`setSize()` and `Text.append()` can expose stale capacity bytes if callers serialize or compare incorrectly.

`Text` works in UTF-8 byte offsets, not Java UTF-16 character indexes. `charAt`, `find`, decode, validate, and `bytesToCodePoint` can fail or return byte positions that surprise callers mixing byte and character indexing. Max-length overloads must be used when reading untrusted data.

`IOUtils.cleanup*` and `closeStream(s)` swallow all throwables by design and are only appropriate during exception cleanup. Using them on primary close paths can hide data-loss failures. `readFullyToByteArray(DataInput)` warns that infinite inputs never return and can exhaust memory.

`SequenceFile` has many deprecated writer overloads retained for compatibility. New code should use the option-based factory to avoid overload confusion. Compression type, codec, metadata, create flags, parent creation, and sync intervals are part of persisted format and read compatibility.

`ObjectWritable` and Java class loading are security-sensitive when reading untrusted data. Declared classes, configurations, and class loaders must be constrained in code paths that process remote or user-supplied serialized values.

## Test signals

Good coverage for code relying on this chunk should include statistics snapshot tests for null sources, overwrite versus aggregate semantics, synchronized map visibility, mean-statistic merging, empty min/max sentinels, JSON round trips, Java serialization class allow-list coverage, and lazy logging that tolerates wrong source types and provider exceptions.

Metric vocabulary tests should assert stable `StoreStatisticNames` and `StreamStatisticNames` strings for externally consumed counters, including object-store request counters, multipart upload counters, stream seek/read/write counters, and min/max/mean/failure suffixes.

HA tests should cover health-monitor success and failure, access-control failure propagation, active/standby/observer transition requests, optional observer support, `HAServiceProtocolHelper` remote exception handling, service/health/ZKFC proxy construction, fencing parameter injection, invalid fencing arguments, missing fencer configuration, false fencing results, and auto-failover enablement.

Writable tests should round-trip every primitive writable, variable-length integer edge values, arrays, two-dimensional arrays, enum sets including empty sets with explicit element type, `MapWritable`/`SortedMapWritable` with multiple key/value classes, `GenericWritable` accepted and rejected types, `ObjectWritable` declared-class handling, `NullWritable` singleton behavior, `VersionedWritable` mismatch handling, and `MD5Hash` digest/string/compare behavior.

Comparator tests should compare object-level and byte-level ordering for `BinaryComparable`, `BytesWritable`, `Text`, primitive writables, and custom `WritableComparable` keys. They should also assert stable hash codes across JVM instances for types used as keys.

`Text` tests need valid and invalid UTF-8 cases, multibyte code points, byte-offset `charAt`, substring `find`, append/clear/set behavior, max-length read/write enforcement, decode with and without replacement, `utf8Length`, and backing-array capacity larger than logical length.

`IOUtils` tests should cover copy loops with and without close, exact count copying, EOF behavior in `readFully` and `skipFully`, short channel writes, compressed-stream error wrapping, directory listing failures that `File.list()` would hide, fsync for files and directories, close suppression only in cleanup paths, socket close, exception wrapping preserving `InterruptedIOException` and `PathIOException`, and bounded use of `readFullyToByteArray`.

`SequenceFile` tests should exercise the option-based writer factory, deprecated overload compatibility, uncompressed/record-compressed/block-compressed writers, codec selection, metadata preservation, sync marker seekability, create-parent behavior, `FileContext` create flags/options, default compression type configuration, and reader compatibility across files written by old overloads.

File-format helper tests should cover `MapFile.rename/delete/fix`, `ArrayFile` dense key behavior, `SetFile` membership semantics, and `BloomMapFile` sidecar deletion/metadata expectations.
