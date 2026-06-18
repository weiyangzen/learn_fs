# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.6.xml lines 18229-24759

## Scope

This chunk is a public API snapshot from Hadoop Common 3.3.6 JDiff XML. It begins in the tail of `org.apache.hadoop.fs.Trash`, covers filesystem support APIs (`TrashPolicy`, XAttr codecs, upload handles, audit context, FTP filesystem, IO statistics), HA protocol contracts, and then enters `org.apache.hadoop.io` through the first group of Writable and file-format APIs, ending inside the overloaded `SequenceFile.createWriter(...)` API family. Because the source is API metadata rather than implementation source, the research below focuses on exported contracts, expected control flow, state and persistence surfaces, integration points, risks, and test signals implied by the public signatures and documentation.

## Purpose

The chunk documents several foundational Hadoop Common surfaces:

- Filesystem delete/trash behavior, including pluggable trash policies and path-aware trash directories for HDFS encryption zones.
- Filesystem extension points for unsupported schemes, multipart upload handles, XAttr value encoding, and XAttr create/replace validation.
- Process-wide and thread-local audit context propagated into filesystem audit spans.
- A `FileSystem` implementation backed by Apache Commons Net FTP.
- Low-cost IO statistics contracts, serializable snapshots, metric name constants, and duration/mean aggregation helpers used by object stores and stream implementations.
- HA fencing and service transition protocols used by client-side failover administration.
- Core Hadoop `Writable` building blocks: primitive wrappers, byte arrays, arrays, maps, enum sets, polymorphic object serialization, IO helpers, MD5 hashes, `MapFile`, and the beginning of `SequenceFile` writer creation APIs.

## Important APIs, Types, And Functions

### `org.apache.hadoop.fs`

`Trash` is only partially included here. The visible methods are `expunge()`, `expungeImmediately()`, `getEmptier()`, and `getCurrentTrashDir(Path)`. These expose scheduled and immediate cleanup of trash checkpoints and a superuser-oriented emptier runnable.

`TrashPolicy extends Configured` is the main abstraction for pluggable trash implementations:

- Initialization has a deprecated `initialize(Configuration, FileSystem, Path home)` and the preferred `initialize(Configuration, FileSystem)`. The newer contract avoids assuming trash lives below `/user/$USER`, which matters for HDFS encryption zones where cross-zone rename is disallowed.
- `isEnabled()`, `moveToTrash(Path)`, `createCheckpoint()`, `deleteCheckpoint()`, and `deleteCheckpointsImmediately()` define the lifecycle.
- `getCurrentTrashDir()` is the older pathless API and is explicitly called out as wrong for files deleted from encryption zones. `getCurrentTrashDir(Path)` is the path-aware replacement.
- `getEmptier()` returns a periodic cleanup `Runnable`, intended for the superuser.
- `getInstance(Configuration, FileSystem, Path)` is deprecated in favor of `getInstance(Configuration, FileSystem)`, with both driven by `fs.trash.classname`.
- Protected state includes `fs`, `trash`, and `deletionInterval`.

`UnsupportedFileSystemException` and `UnsupportedMultipartUploaderException` are `IOException` subclasses carrying message-only constructors for unsupported filesystem schemes and unsupported multipart uploaders.

`UploadHandle` is a serializable opaque multipart upload identifier. `bytes()` returns a `ByteBuffer`, `toByteArray()` serializes from that buffer, and implementations must define equality.

`XAttrCodec` encodes and decodes XAttr byte values for shell, HTTP, and JSON surfaces. `decodeValue(String)` accepts hex prefixes `0x`/`0X`, base64 prefixes `0s`/`0S`, quoted text, and unquoted text. `encodeValue(byte[], XAttrCodec)` emits text with quotes, hex with `0x`, or base64 with `0s`.

`XAttrSetFlag` exposes enum values and `validate(String xAttrName, boolean xAttrExists, EnumSet flag)`, the public validation point for create/replace XAttr semantics.

### `org.apache.hadoop.fs.audit.CommonAuditContext`

`CommonAuditContext` is a final context holder for audit attributes shared across all filesystems within a thread and optionally across all threads:

- Per-thread entries: `put(String, String)`, `put(String, Supplier<String>)`, `remove(String)`, `get(String)`, `containsKey(String)`, `reset()`, and `getEvaluatedEntries()`.
- Accessors: `currentAuditContext()` returns the thread-local context; `currentThreadID()` returns a process-unique thread identifier shared across S3A clients on that thread.
- Global entries: `setGlobalContextEntry`, `getGlobalContextEntry`, `removeGlobalContextEntry`, and `getGlobalContextEntries()`.
- `noteEntryPoint(Object)` records the launched tool/application under the audit command parameter when absent.
- `PROCESS_ID` is a process identifier built from UUID and timestamp.

The API explicitly warns that long-lived supplier entries must not capture large object instances, because audit spans retain references to context entries and may be evaluated later in another thread.

### `org.apache.hadoop.fs.ftp`

`FTPException` is a runtime wrapper for FTP failures, with message, cause, and message-plus-cause constructors.

`FTPFileSystem extends FileSystem` exposes Hadoop FS semantics over Apache Commons Net FTP:

- Identification and setup: `getScheme()` returns `ftp`, `getDefaultPort()`, `initialize(URI, Configuration)`, and `getUri()`.
- File operations: `open(Path, int)`, `create(Path, FsPermission, boolean, int, short, long, Progressable)`, `delete(Path, boolean)`, `listStatus(Path)`, `getFileStatus(Path)`, `mkdirs(Path, FsPermission)`, and `rename(Path, Path)`.
- Directory state: `getWorkingDirectory()`, `getHomeDirectory()`, and `setWorkingDirectory(Path)`.
- `append(Path, int, Progressable)` is documented as unsupported.
- Public constants cover buffer size, block size, timeout, config prefixes for FTP user/password/host/port/data connection mode/transfer mode, and the same-directory-only rename error.

The `create` doc warns that its returned stream must be closed before any other API call on the same filesystem instance, or the next invocation may block.

### `org.apache.hadoop.fs.statistics`

`DurationStatisticSummary` is a serializable reporting/test helper over duration metrics. It stores a key, success/failure side, count, min, max, and a cloned `MeanStatistic`. `fetchDurationSummary(IOStatistics, String, boolean)` and `fetchSuccessSummary(IOStatistics, String)` extract summaries from an `IOStatistics` source.

`IOStatistics` defines five metric maps: `counters()`, `gauges()`, `minimums()`, `maximums()`, and `meanStatistics()`. `MIN_UNSET_VALUE` and `MAX_UNSET_VALUE` define unset sentinel values.

`IOStatisticsAggregator` exposes `aggregate(IOStatistics)` and allows full or selective merging. `IOStatisticsSetters` extends `IOStatistics` with simple setters for counters, gauges, minimums, maximums, and means.

`IOStatisticsLogging` is a final static helper for robust stringification/logging. It retrieves statistics from `IOStatistics` or `IOStatisticsSource`, produces compact or sorted pretty strings, builds lazy demand-stringifier objects for log statements, and logs at DEBUG or a named level while catching/downgrading retrieval failures.

`IOStatisticsSnapshot` is final, serializable, and implements `IOStatistics`, `IOStatisticsAggregator`, and `IOStatisticsSetters`. It can be constructed empty or from a source, `clear()` all maps, `snapshot(IOStatistics)` by overwriting current state, `aggregate(IOStatistics)` by synchronized merge, expose synchronized metric maps, and serialize through a static Jackson `JsonSerialization` helper. `requiredSerializationClasses()` exists for safer deserialization of known classes.

`IOStatisticsSupport` provides static helpers for `snapshotIOStatistics(IOStatistics)`, creating empty snapshots, `retrieveIOStatistics(Object)`, and no-op duration tracker singletons.

`MeanStatistic` is a serializable, cloneable sum/sample-count statistic. It protects invalid sample counts by normalizing nonpositive counts to empty state, calculates mean on demand, supports synchronized sample addition and merging, treats all empty statistics as equivalent, and warns that hash code depends on mutable mean/sample state.

`StoreStatisticNames` and `StreamStatisticNames` are public constant catalogs. Store names cover common filesystem operations, object-store requests, multipart upload lifecycle, throttle/rate-limit/retry signals, HTTP method actions, metadata/copy requests, and suffixes for min/max/mean/failure counters. Stream names cover read/write counters, read seek/skip/vector/prefetch/cache metrics, remote stream drain/abort/version mismatch, upload queue/timing/byte counters, and block allocation/release signals.

### `org.apache.hadoop.ha`

Exception types in this chunk include `BadFencingConfigurationException extends IOException`, `FailoverFailedException extends Exception`, `HealthCheckFailedException extends IOException`, and `ServiceFailedException extends IOException`, each with message and message-plus-cause constructors where applicable.

`FenceMethod` is the operator/plugin interface for forcing a target node to stop making progress:

- `checkArgs(String)` validates configured arguments at startup.
- `tryFence(HAServiceTarget, String)` attempts fencing and returns true only for known success. False includes failure or indeterminate results.
- Implementations may also implement `Configurable` for configuration injection.

`HAServiceProtocol` is the RPC contract for HA frameworks:

- `monitorHealth()` performs service-specific health checks and may trigger failover if an active service fails.
- `transitionToActive(StateChangeRequestInfo)`, `transitionToStandby(...)`, and `transitionToObserver(...)` request state changes and are no-ops if already in that state.
- `getServiceStatus()` returns `HAServiceStatus`.
- Calls can throw access-control, IO, health-check, or service-transition exceptions.
- `versionID` marks the initial protocol version.

`HAServiceProtocolHelper` wraps HA RPC calls and unwraps `RemoteException` to specific exceptions for monitor and transition methods.

`HAServiceTarget` is an abstract representation of a target node for HA administration. Subclasses provide IPC address, ZKFC address, fencer, and fencing preflight validation. The base class creates service, health-monitor, and ZKFC proxies with timeout/retry parameters, optionally uses a separate health-monitor address, tracks a transition-target HA state, returns fencing parameters for scripts, allows subclasses to add parameters, and advertises whether auto-failover or observer state is supported.

`org.apache.hadoop.ha.protocolPB.HAServiceProtocolPB` and `ZKFCProtocolPB` are protobuf RPC marker interfaces in this chunk.

### `org.apache.hadoop.io` Writable And Utility APIs

`AbstractMapWritable` is a configurable `Writable` base for map-like writables. It keeps per-instance class-to-id mappings rather than static mappings, supports up to 127 distinct classes in a map instance, and serializes those class mappings with the data. `addToMap(Class)` and `copy(Writable)` are synchronized protected helpers.

Array and primitive wrappers:

- `ArrayFile extends MapFile` is a dense file-based mapping from integers to values.
- `ArrayPrimitiveWritable` wraps primitive arrays without copying and provides an optimized wire format.
- `ArrayWritable` serializes homogeneous `Writable[]` values; reducer inputs generally need subclasses that bind a concrete value class.
- `BooleanWritable`, `ByteWritable`, `DoubleWritable`, `FloatWritable`, `IntWritable`, and `LongWritable` are `WritableComparable` primitive wrappers with constructors, `set`, `get`, `readFields`, `write`, equality, hash, comparison, and string conversion.
- `BytesWritable extends BinaryComparable` is a resizable byte-sequence key/value. It distinguishes logical length from backing capacity, exposes `copyBytes()` for exact copies and `getBytes()` for direct backing access, deprecates `get()` and `getSize()`, and compares like `memcmp`.
- `BinaryComparable` defines byte-backed ordering through `getBytes()` and `getLength()`, with compare/equality/hash backed by `WritableComparator` byte helpers.

Buffer and close helpers:

- `ByteBufferPool` defines `getBuffer(boolean direct, int length)`, `putBuffer(ByteBuffer)`, and default `release()`.
- `ElasticByteBufferPool` is a synchronized implementation that allocates on demand and caches returned direct or heap buffers, always selecting the smallest cached buffer large enough and deliberately not bounding cache size.
- `org.apache.hadoop.io.Closeable` is deprecated in favor of `java.io.Closeable`.

Serialization wrappers:

- `CompressedWritable` stores data compressed and lazily inflates on field access. Its `readFields` and `write` are final; subclasses implement `readFieldsCompressed` and `writeCompressed`.
- `DataOutputOutputStream` adapts `DataOutput` to `OutputStream`, returning the original object when it already is an `OutputStream`.
- `DefaultStringifier<T>` uses Hadoop `SerializationFactory`, `Serializer`, and `Deserializer` to turn objects into base64 strings. It offers static `store/load` and `storeArray/loadArray` helpers for persisting objects in `Configuration` keys.
- `EnumSetWritable<E extends Enum<E>>` wraps `EnumSet` and requires an explicit element type when the value is null or empty; it also carries configuration.
- `GenericWritable` wraps one of a finite set of `Writable` classes supplied by subclass `getTypes()`.
- `ObjectWritable` serializes a `Writable`, `String`, primitive type, or array along with its declared class name. It has `writeObject` overloads, including `allowCompactArrays`: true for RPC/internal usage and false for inter-cluster, file, and other persisted output where compatibility matters. `readObject` reconstructs instances and `loadClass(Configuration, String)` resolves class names through configuration when available.

IO and file-format helpers:

- `IOUtils` provides stream/channel copy, read/skip fully, compressed-read wrapping, cleanup methods that ignore close failures, socket close, full `ByteBuffer` channel writes, directory listing, file/directory `fsync`, exception wrapping with path/method context, and `readFullyToByteArray(DataInput)` until EOF.
- `MapFile` exposes static `rename`, `delete`, `fix`, and `main`, with `INDEX_FILE_NAME` and `DATA_FILE_NAME` constants.
- `MapWritable extends AbstractMapWritable` implements `Map<Writable,Writable>`-like operations plus `write/readFields`.
- `MD5Hash` is a fixed 16-byte hash `WritableComparable`; it can digest strings, byte arrays, byte ranges, input streams, and MD5 digests, return full digest bytes, half/quarter digests, compare, stringify, and parse/set digest.
- `MultipleIOException` aggregates a list of IOExceptions and can create either a single exception or an aggregate.
- `NullWritable` is a singleton zero-value `WritableComparable` with no serialized data.
- `RawComparator<T>` extends `Comparator<T>` with direct binary `compare(byte[], int, int, byte[], int, int)`.

`SequenceFile` begins here. The visible API includes default compression getters/setters and many `createWriter(...)` overloads. The preferred modern surface is `createWriter(Configuration, Writer.Option...)`; most older overloads taking `FileSystem`, `Path`, key/value classes, compression, codec, progress, metadata, buffer size, replication, and block size are deprecated in favor of options. Non-deprecated compatibility overloads still support explicit `createParent` and `FileContext` plus `CreateFlag`/`CreateOpts`.

## Control Flow

Trash flow is policy-driven. `Trash` delegates deletion/checkpoint/expunge operations to the configured `TrashPolicy`. `TrashPolicy.getInstance(...)` selects a policy class from configuration, initializes it with a filesystem, and subsequent delete flows call `moveToTrash(Path)`. Cleanup flows call `createCheckpoint()`, `deleteCheckpoint()`, `deleteCheckpointsImmediately()`, or schedule `getEmptier()`.

XAttr conversion flow is prefix-driven: decode first inspects the textual prefix or quotes to select hex, base64, or text decoding; encode chooses a representation from the requested `XAttrCodec`. XAttr set flow should call `XAttrSetFlag.validate(...)` before applying create/replace semantics to the filesystem.

Audit flow is split between thread-local and global maps. Filesystem entry points populate the current thread's `CommonAuditContext`, optionally register long-lived global attributes, and audit spans retain the context reference. `getEvaluatedEntries()` later forces any suppliers, potentially in a different thread from where they were registered.

FTP filesystem flow wraps an FTP client under the Hadoop `FileSystem` API. `initialize` derives host/user/password/port and transfer settings from URI/configuration. File streams returned by `open` and `create` must be consumed and closed before other operations on the instance proceed reliably.

IO statistics flow is map-based. Producers expose `IOStatistics` or `IOStatisticsSource`; callers retrieve them through `IOStatisticsSupport`, snapshot them into `IOStatisticsSnapshot`, optionally aggregate multiple sources, and log compact or pretty forms through `IOStatisticsLogging`. Duration summaries derive counts/min/max/mean from a naming convention over the metric maps.

HA control flow is failover-oriented. Admin or failover code builds an `HAServiceTarget`, preflights fencing through `checkFencingConfigured()`, monitors health through `HAServiceProtocol.monitorHealth()`, calls transition methods with `StateChangeRequestInfo`, and invokes configured `FenceMethod` instances in order until one returns success. `HAServiceProtocolHelper` centralizes RPC exception unwrapping.

Writable control flow follows Hadoop's `Writable` binary serialization pattern: default constructor, `readFields(DataInput)` to mutate an empty instance from bytes, and `write(DataOutput)` to persist state. Comparable wrappers add stable sort order. Polymorphic wrappers (`GenericWritable`, `ObjectWritable`, `AbstractMapWritable`) serialize type information so deserialization can instantiate the right class. `IOUtils` operations are procedural helpers around streams/channels and deliberately swallow errors in cleanup variants.

`SequenceFile.createWriter(...)` flow is overloaded compatibility funneling. New code should build a writer through `Writer.Option` values, while old overloads adapt explicit filesystem/path/classes/compression/metadata/storage options into the writer construction path.

## State And Persistence Behavior

`TrashPolicy` holds protected mutable state: the target `FileSystem`, current trash `Path`, and deletion interval. Trash checkpoints are persisted as filesystem directories and renamed/deleted by the policy implementation, while this XML exposes only the abstract lifecycle.

`UploadHandle` instances are opaque but serializable. The exact bytes returned by `bytes()`/`toByteArray()` are a persistence boundary for multipart upload recovery or continuation.

`CommonAuditContext` has JVM-global state and thread-local state. Global context entries apply across all threads and audit spans; thread context is per-thread but audit spans retain references after crossing thread boundaries. Supplier entries are stateful callbacks and can retain captured objects until removed.

`FTPFileSystem` maintains filesystem URI, working directory, connection/client state, and stream lifecycle. Configuration keys persist connection metadata in `Configuration`; FTP itself does not expose Hadoop-style block/replication semantics even though method signatures include those parameters for `FileSystem` compatibility.

`IOStatisticsSnapshot` is explicitly serializable for propagation through frameworks such as Spark and Flink and is annotated for Jackson. It uses concrete sorted map state for counters, gauges, min/max values, and mean statistics. The docs warn against deserializing untrusted Java object streams and provide `requiredSerializationClasses()` for defensive class allowlisting.

`MeanStatistic` stores mutable `samples` and `sum`; mean is computed on demand. Empty state is represented by zero samples and is equivalent regardless of sum. Hash/equality depend on mutable state, so instances are unsafe as hash-map keys after mutation.

`StoreStatisticNames` and `StreamStatisticNames` are constants with no runtime state, but their string values form a compatibility surface for metrics dashboards, tests, and downstream consumers.

Writable classes define persistent binary formats through `write/readFields`. Key persistence surfaces include per-instance class tables in `AbstractMapWritable`, no-copy primitive array storage in `ArrayPrimitiveWritable`, logical length plus capacity in `BytesWritable`, compressed payload caching in `CompressedWritable`, enum element type in `EnumSetWritable`, declared class names in `ObjectWritable`, and MD5 digest bytes in `MD5Hash`.

`DefaultStringifier` persists serialized objects into `Configuration` string values using base64. This makes configuration values dependent on the configured Hadoop serialization framework and the class availability on load.

`MapFile`/`ArrayFile`/`BloomMapFile`-adjacent APIs persist data in filesystem directories with `data` and `index` files; the chunk exposes static maintenance operations rather than reader/writer internals. `SequenceFile` writer APIs create persistent key/value files whose compression type, codec, metadata, replication, block size, and parent creation semantics are caller-controlled.

## Dependencies And Integration Points

Major Hadoop dependencies surfaced here include `Configuration`, `Configured`, `FileSystem`, `FileContext`, `Path`, `FileStatus`, `FSDataInputStream`, `FSDataOutputStream`, `FsPermission`, `Options.CreateOpts`, `Progressable`, `RemoteException`, HA service/status/request types, `NodeFencer`, `ZKFCProtocol`, `Writable`, `WritableComparable`, `WritableComparator`, `JsonSerialization`, and Hadoop serialization factories.

Java dependencies include `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `File`, `FileChannel`, `WritableByteChannel`, `ByteBuffer`, `Socket`, `URI`, `InetSocketAddress`, `IOException`, `RuntimeException`, collections, `Supplier`, `Serializable`, `Cloneable`, and cryptography `MessageDigest`.

External integration is visible through Apache Commons Net for FTP and Jackson JSON serialization for statistics snapshots. The audit docs explicitly reference S3A clients and hadoop-aws auditing architecture; statistics names also map heavily to object-store operations such as list, PUT, metadata, copy, bulk delete, multipart upload, throttling, retry, and HTTP actions.

Metrics constants are integration contracts for filesystem implementations, stream implementations, logging, tests, and operational dashboards. HA interfaces integrate with RPC protocol PB interfaces, ZooKeeper Failover Controller addresses, fencer implementations, and operator-provided fencing scripts or devices. Writable and SequenceFile APIs integrate with MapReduce, RPC, inter-cluster file interchange, and long-lived on-disk Hadoop data formats.

## Risks And Edge Cases

- The chunk starts mid-class and ends mid-`SequenceFile`, so this research covers only the visible public API segment; adjacent chunks must reconcile full class-level behavior.
- Pathless trash APIs can choose the wrong trash directory for HDFS encryption zones, causing rename failures across zones. New code should prefer `getCurrentTrashDir(Path)` and the newer `initialize(Configuration, FileSystem)` / `getInstance(Configuration, FileSystem)` contracts.
- `TrashPolicy.getInstance` depends on a configured class name. Bad classes, incompatible constructors, or incorrect initialization can break deletion behavior at runtime.
- `moveToTrash(Path)` returns false both when trash is disabled and when a path is already in trash; callers that need diagnostics must distinguish this elsewhere.
- `UploadHandle` equality and byte serialization are implementation-defined. ByteBuffer position/limit handling is a common source of inconsistent `toByteArray()` results if implementations are sloppy.
- `XAttrCodec` must reject malformed hex/base64 cleanly and preserve exact bytes for text encodings. Ambiguous unquoted strings are treated as text, not errors.
- Audit supplier entries can retain large object graphs or evaluate in unexpected threads. Global context entries are shared process-wide and can leak cross-tenant/application metadata in long-lived JVMs if not removed.
- FTP operations are constrained by FTP semantics. Append is unsupported, rename may be limited to the same directory, block size/replication are mostly advisory compatibility parameters, and unclosed create streams can block subsequent operations.
- `IOStatisticsSnapshot.snapshot()` is documented as non-atomic when reading a live source. Concurrent metric mutation can produce internally inconsistent snapshots unless producers provide stronger synchronization.
- `IOStatisticsSnapshot` Java serialization should not be used on untrusted streams. JSON/Jackson deserialization must include the required classes.
- `MeanStatistic` is mutable and hash-code-sensitive; using it as a map key after mutation is unsafe. Arithmetic sum/sample accumulation can also overflow `long`.
- Metric name constants are string compatibility contracts. Renaming or reusing constants breaks dashboards and tests even when Java signatures compile.
- HA fencing can return false for indeterminate results, so failover orchestration must treat non-true as unsafe. Misconfigured fencing parameters or missing superclass `addFencingParameters` delegation can break shell-script fencers.
- Separate health-monitor addresses protect the main RPC handler pool, but incorrect address configuration can make healthy services appear unhealthy.
- Writable binary formats are compatibility-sensitive. `ObjectWritable.writeObject(..., allowCompactArrays=true)` is only for RPC/internal usage; using compact arrays in persisted files can reduce interchange compatibility with other Hadoop versions.
- `AbstractMapWritable` has a per-instance class id range of 1-127. Maps containing too many distinct writable classes can exceed the representable range.
- `ArrayPrimitiveWritable` and `BytesWritable.getBytes()` expose backing storage. Callers can mutate internal state unintentionally or read beyond logical length.
- `ElasticByteBufferPool` intentionally lacks a max cache size, which can retain large heap or direct buffers after bursts.
- Cleanup methods in `IOUtils` ignore failures by design. They are inappropriate when close/fsync failures must be reported to preserve durability guarantees.
- `DefaultStringifier` stores opaque base64 serialized payloads in configuration; changes to serializers or missing classes can make old configuration values unreadable.
- Deprecated `SequenceFile.createWriter` overloads remain source-compatible but should not be expanded in new code; option-based writer creation is the stable direction.

## Test Signals

Focused validation for code touching these APIs should include:

- Trash: policy selection from `fs.trash.classname`, initialization overload behavior, enabled/disabled delete paths, already-in-trash handling, checkpoint creation/deletion, immediate expunge, superuser emptier execution, and encryption-zone path-aware trash directory selection.
- XAttrs: round-trip encode/decode for hex, base64, quoted text, unquoted text, malformed inputs, empty values, and `XAttrSetFlag.validate` create/replace combinations with existing and absent attributes.
- Upload handles: stable byte serialization independent of `ByteBuffer` position, equality/hash behavior for equivalent handles, and Java serialization compatibility if implementations support it.
- Audit context: thread-local isolation, global entry propagation, `noteEntryPoint` idempotence, supplier lazy evaluation, removal of supplier references, `reset()` restoring standard options, and cross-thread span evaluation behavior.
- FTP filesystem: initialization from URI/config keys, default port, login failure, open/create close sequencing, unsupported append, delete recursive/nonrecursive cases, list/status behavior, mkdirs, working directory resolution, home directory, same-directory rename limits, and timeout handling.
- IO statistics: map exposure for all metric classes, unset min/max sentinels, snapshot overwrite semantics, aggregate null handling, synchronized map/setter behavior, JSON round trip, Java serialization allowlist classes, pretty/compact logging output, and no-op duration tracker behavior.
- Mean/duration statistics: empty equivalence, invalid sample normalization, synchronized add/merge/copy, overflow edge cases, mean calculation, mutable hash-code warning, and success/failure duration summary extraction with missing keys.
- Metrics constants: tests that emitted operation and stream metrics use exact expected names for object-store requests, multipart upload, throttling, vector reads, seek/skip, prefetch, cache, and write queue counters.
- HA: fencing argument validation, ordered fencing false/true behavior, runtime `BadFencingConfigurationException`, transition no-op behavior when already in target state, monitor health exception propagation, `RemoteException` unwrapping through helper methods, health monitor address fallback/override, proxy timeouts/retries, fencing parameter map contents, auto-failover flag, and observer support.
- Writables: default-constructor/readFields round trips, write/read compatibility across versions, comparison/equality/hash consistency, backing-array mutation hazards, `BytesWritable` length versus capacity, primitive wrapper ordering, `EnumSetWritable` null/empty element type requirements, `GenericWritable` rejection of unsupported types, and `ObjectWritable` declared-class handling.
- IO utilities: exact-byte copy, count-limited copy, close flag behavior, short channel writes, positioned writes, read/skip fully EOF handling, cleanup swallowing behavior, fsync for files and directories, exception wrapping with path/method context, and `readFullyToByteArray` memory behavior on large inputs.
- File formats: `MapFile.rename/delete/fix` on missing/corrupt index/data files, `MD5Hash` digest sources and string parsing, `MultipleIOException.createIOException` for zero/one/many exceptions, `NullWritable` singleton serialization, `RawComparator` byte-range ordering, and `SequenceFile.createWriter` option-based and legacy overload parity for compression, codec, metadata, parent creation, `FileSystem`, and `FileContext` paths.
