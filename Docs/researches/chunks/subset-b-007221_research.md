# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.5.xml lines 18226-24779

## Scope

This chunk is part 4 of the Hadoop Common 3.3.5 JDiff API snapshot. It starts inside the tail of `org.apache.hadoop.fs.TrashPolicy`, finishes the visible `org.apache.hadoop.fs` package entries in this range, covers `org.apache.hadoop.fs.audit`, `org.apache.hadoop.fs.ftp`, `org.apache.hadoop.fs.statistics`, `org.apache.hadoop.ha`, `org.apache.hadoop.ha.protocolPB`, and begins `org.apache.hadoop.io` through `ShortWritable.toString()`.

The file is generated API metadata, not runtime source. It records public/protected type declarations, inheritance, constructors, methods, parameters, exceptions, fields, deprecation strings, and Javadoc. Control-flow and persistence notes below are therefore derived from signatures and API contracts, especially where the XML documents durable file formats or mutable state.

## Purpose

The source file is a compatibility baseline for Hadoop Common 3.3.5. This slice captures several stable surfaces used by filesystem clients, object-store instrumentation, HA administration, RPC protocol binding, and Hadoop binary serialization.

The filesystem tail records trash policy behavior, unsupported filesystem/upload exceptions, multipart upload handles, extended attribute encoding, and XAttr creation/replacement validation. `CommonAuditContext` captures thread-local and global audit attributes that filesystem audit spans can include in downstream logging or HTTP referrer headers. `FTPFileSystem` exposes the legacy FTP `FileSystem` implementation and its configuration keys.

The statistics package records the low-cost `IOStatistics` contract used by filesystem and stream implementations to publish counters, gauges, min/max values, and mean statistics. It also defines common statistic-name constants for store operations, object-store multipart uploads, HTTP actions, read streams, write streams, buffering, and remote reads.

The HA package defines the client-side failover and fencing API: service health checks, transitions to active/standby/observer, status retrieval, target addressing, fencing configuration, and protocol-buffer RPC marker interfaces. The `org.apache.hadoop.io` section begins Hadoop's core `Writable` data model and persistent file containers, including primitive wrappers, byte/array wrappers, map writables, object serialization, `MapFile`, and `SequenceFile` writer creation.

## Important APIs, Types, and Functions

### Filesystem tail and audit context

- `TrashPolicy` methods in this range include `deleteCheckpointsImmediately()`, legacy `getCurrentTrashDir()`, path-aware `getCurrentTrashDir(Path)`, `getEmptier()`, and factory overloads `getInstance(Configuration, FileSystem, Path)` and `getInstance(Configuration, FileSystem)`. Protected fields `fs`, `trash`, and `deletionInterval` define the policy's filesystem, trash directory, and checkpoint interval state. The legacy current-trash API is documented as unsafe for HDFS encryption-zone deletes, with callers directed to the path-aware overload.
- `UnsupportedFileSystemException` and `UnsupportedMultipartUploaderException` are `IOException` subclasses with string-message constructors, used when a filesystem scheme or multipart uploader implementation is unavailable.
- `UploadHandle` is an opaque multipart-upload identifier. It extends `Serializable`, exposes `bytes()` as a `ByteBuffer`, has a default `toByteArray()`, and requires `equals(Object)`.
- `XAttrCodec` converts XAttr byte arrays to and from textual representations. `decodeValue(String)` recognizes `0x`/`0X` hex, `0s`/`0S` base64, and quoted or unquoted text. `encodeValue(byte[], XAttrCodec)` emits quoted text, hex, or base64 with prefixes.
- `XAttrSetFlag.validate(String, boolean, EnumSet)` validates create/replace flag combinations against whether an xattr already exists.
- `CommonAuditContext` is a final audit metadata holder. It supports string or supplier-valued `put()`, `remove()`, `get()`, `containsKey()`, `reset()`, `getEvaluatedEntries()`, thread-local `currentAuditContext()`, process-unique `currentThreadID()`, global context setters/getters/removal, `getGlobalContextEntries()`, and `noteEntryPoint(Object)`. `PROCESS_ID` is public and is documented as UUID/timestamp based.

### FTP filesystem

- `FTPException` wraps a message, cause, or both.
- `FTPFileSystem` extends Hadoop's `FileSystem` API with `getScheme()`, `getDefaultPort()`, `initialize(URI, Configuration)`, `open(Path, int)`, `create(Path, FsPermission, boolean, int, short, long, Progressable)`, unsupported `append(Path, int, Progressable)`, `delete(Path, boolean)`, `getUri()`, `listStatus(Path)`, `getFileStatus(Path)`, `mkdirs(Path, FsPermission)`, `rename(Path, Path)`, `getWorkingDirectory()`, `getHomeDirectory()`, and `setWorkingDirectory(Path)`.
- Public constants include defaults for buffer size, block size, timeout, configuration prefixes/keys for user, host, port, password, data connection mode, transfer mode, timeout, and `E_SAME_DIRECTORY_ONLY` for rename restrictions.

### IO statistics

- `DurationStatisticSummary` summarizes duration metrics with key, success flag, count, min, max, and `MeanStatistic`, and can fetch duration or success summaries from an `IOStatistics` source.
- `IOStatistics` is the base interface returning maps for `counters()`, `gauges()`, `minimums()`, `maximums()`, and `meanStatistics()`. `MIN_UNSET_VALUE` and `MAX_UNSET_VALUE` mark unset extrema.
- `IOStatisticsAggregator.aggregate(IOStatistics)` merges statistics into an implementation-specific aggregate and returns whether a non-null source was processed.
- `IOStatisticsLogging` stringifies `IOStatistics` or `IOStatisticsSource`, provides lazy `toString()` wrappers for low-cost logging, and logs statistics at debug or named levels while swallowing source extraction failures into debug logging.
- `IOStatisticsSnapshot` implements `IOStatistics`, `Serializable`, and `IOStatisticsAggregator`. It can be built empty or from a source, synchronizes `clear()`, `snapshot()`, `aggregate()`, and map accessors, exposes `serializer()` as `JsonSerialization`, and lists `requiredSerializationClasses()` for safer deserialization.
- `IOStatisticsSupport` builds empty or populated snapshots, retrieves statistics from either an `IOStatistics` instance or `IOStatisticsSource`, and returns singleton no-op duration tracker factory/tracker implementations.
- `MeanStatistic` is a synchronized, serializable, cloneable `(samples, sum)` pair. It handles invalid sample counts by resetting to empty, supports getters, clear, set, add another statistic, add a sample, `mean()`, equality/hash, clone/copy, and string rendering.
- `StoreStatisticNames` and `StreamStatisticNames` are constant catalogs. Store names cover filesystem API operations, xattr operations, delegation tokens, object-store probes, throttling/rate limiting/retries, list/delete/copy/metadata requests, HTTP verbs, multipart upload lifecycle, and suffixes for min/max/mean/failure metrics. Stream names cover read open/close/abort, read bytes and operations, vectored reads, seeks/skips, unbuffering, write failures, block upload queues, uploaded/failed byte counts, task wait time, buffer reads, remote reads, read-ahead, and block allocation/release.

### High availability APIs

- `BadFencingConfigurationException`, `FailoverFailedException`, `HealthCheckFailedException`, and `ServiceFailedException` are HA-specific exception types with message and message/cause constructors where applicable.
- `FenceMethod` validates fencing method arguments via `checkArgs(String)` and attempts fencing with `tryFence(HAServiceTarget, String)`, returning whether the target was fenced.
- `HAServiceProtocol` defines RPC operations `monitorHealth()`, `transitionToActive(StateChangeRequestInfo)`, `transitionToStandby(StateChangeRequestInfo)`, `transitionToObserver(StateChangeRequestInfo)`, and `getServiceStatus()`, plus `versionID`.
- `HAServiceProtocolHelper` wraps the transition and health RPC calls, preserving the same operation set for callers.
- `HAServiceTarget` abstracts a target used by HA admin clients. It exposes primary, health-monitor, and ZKFC addresses; fencer lookup and configuration checks; normal and health-monitor proxies with timeouts; ZKFC proxy creation; fencing parameters with subclass extension; auto-failover flag; observer support flag; and transition-target HA status accessors.
- `HAServiceProtocolPB` and `ZKFCProtocolPB` are protocol-buffer service marker interfaces extending the generated blocking protobuf interfaces and Hadoop `VersionedProtocol`.

### Hadoop IO and writable APIs in this chunk

- `AbstractMapWritable` implements `Writable` and `Configurable`. It maintains per-instance class-to-id and id-to-class tables for `MapWritable` and related classes, with `addToMap()`, `getClass(byte)`, `getId(Class)`, `copy(AbstractMapWritable)`, configuration accessors, and `write()`/`readFields()`.
- `ArrayFile`, `BloomMapFile`, `MapFile`, and `SetFile` are file-backed containers. `MapFile` exposes directory `rename()`, `delete()`, index repair via `fix(FileSystem, Path, Class, Class, boolean, Configuration)`, `main()`, and `INDEX_FILE_NAME`/`DATA_FILE_NAME`. `BloomMapFile` adds `delete()` and constants `BLOOM_FILE_NAME` and `HASH_COUNT`.
- `ArrayPrimitiveWritable` wraps primitive Java arrays without copying, records declared/component type, supports `set(Object)`, `get()`, `write()`, and `readFields()`.
- `ArrayWritable` serializes homogeneous arrays of `Writable` values, with constructors for value class, value class plus values, and `String[]`; accessors `getValueClass()`, `get()`, `set()`, `toArray()`, `toStrings()`, `readFields()`, `write()`, and `toString()`.
- `BinaryComparable` supplies byte-based comparison over `getBytes()` and `getLength()`, plus byte-slice comparison, equality, and hash.
- Primitive writables present in this range include `BooleanWritable`, `ByteWritable`, `DoubleWritable`, `FloatWritable`, `IntWritable`, `LongWritable`, and `ShortWritable`. Each follows the standard mutable wrapper pattern: constructors, `set()`, `get()`, `readFields(DataInput)`, `write(DataOutput)`, equality, hash, comparison, and string conversion.
- `BytesWritable` is a mutable byte sequence with exact copy access (`copyBytes()`), backing-array access (`getBytes()` and deprecated `get()`), logical length/capacity access and mutation, range `set()` overloads, writable serialization, comparison-compatible equality/hash, and hex-pair `toString()`.
- `ByteBufferPool` provides `getBuffer(boolean direct, int length)`, `putBuffer(ByteBuffer)`, and `release()`. `ElasticByteBufferPool` implements it by creating buffers as needed and retaining released buffers for reuse.
- `CompressedWritable` is a base class for writables that store compressed bytes and inflate lazily. Subclasses implement `readFieldsCompressed(DataInput)` and `writeCompressed(DataOutput)` and must call `ensureInflated()` before accessing fields.
- `DataOutputOutputStream` adapts `DataOutput` to `OutputStream`, including `constructOutputStream(DataOutput)` and byte write overloads.
- `DefaultStringifier<T>` implements `Stringifier<T>` for Hadoop serialization encoded as base64 strings, with static helpers `store()`, `load()`, `storeArray()`, and `loadArray()` against `Configuration`.
- `EnumSetWritable<E>` wraps an `EnumSet`, implements `Writable` and `Configurable`, carries an element type for null/empty sets, and supports iteration, size, add, set, get, serialization, equality/hash, element-type access, and configuration accessors.
- `GenericWritable` wraps one writable from a fixed subclass-declared type list from `getTypes()`, with compact type-index serialization and `Configurable` integration.
- `IOUtils` is a broad stream/file utility class covering `copyBytes()` overloads, compressed-data read wrapping, exact `readFully()` and `skipFully()`, cleanup and close helpers, socket close, full `ByteBuffer` writes to channels/files, directory listing with exception propagation, file/channel `fsync()`, exception wrapping with path/method context, and `readFullyToByteArray()`.
- `MapWritable` implements `Map<Writable, Writable>` and writable serialization, including copy construction and the standard `Map` operations.
- `MD5Hash` is a `WritableComparable` digest wrapper with constructors from empty, hex string, or bytes; `read()` helper; digest setters/getters; static digest helpers for byte arrays, byte-array arrays, strings, and streams; thread-local digester creation; half/quarter digest projections; and natural ordering.
- `MultipleIOException` encapsulates a list of `IOException` instances and has `createIOException(List)` to return a single exception or wrapper.
- `NullWritable` is the singleton no-data writable, with no-op read/write and stable equality/ordering.
- `ObjectWritable` is polymorphic writable serialization for `Writable`, `String`, primitives, and arrays, storing declared class metadata. Static `writeObject()` and `readObject()` have configuration-aware overloads and an `allowCompactArrays` option; `loadClass(Configuration, String)` resolves serialized class names.
- `RawComparator<T>` compares serialized byte ranges directly without requiring object materialization.
- `SequenceFile` exposes default compression type getters/setters and many `createWriter()` overloads, including modern `Writer.Option...` and deprecated legacy overloads for `FileSystem`, `FileContext`, `FSDataOutputStream`, key/value classes, compression type, codec, progress, metadata, buffer size, replication, block size, create-parent flag, create flags, and create options. `SYNC_INTERVAL` is the public default sync interval.
- The `SequenceFile` Javadoc specifies persistent formats: a common header with magic/version, key/value class names, compression flags, codec, metadata, and sync marker; uncompressed records; record-compressed records; and block-compressed records with grouped/compressed key lengths, keys, value lengths, and values.

## Control Flow

JDiff itself has no runtime flow. Runtime behavior is visible through API contracts.

Trash policy flow is filesystem-configuration driven: callers obtain an implementation via `TrashPolicy.getInstance()`, move/delete paths through policy-specific code outside this chunk, ask for a path-specific trash directory when encryption zones matter, and run the returned emptier as a superuser maintenance task. XAttr flow is decode/validate/encode around shell, HTTP, JSON, or filesystem calls.

Audit flow is context propagation. A caller mutates the thread-local `CommonAuditContext`, optionally sets global attributes, and audit spans retain a reference to the context from the thread where they were created. Supplier-valued entries are evaluated later by `getEvaluatedEntries()`, potentially in another thread.

FTP filesystem flow follows the Hadoop `FileSystem` contract but is constrained by FTP protocol state. `initialize()` configures connection details, `open()` and `create()` create streams, `append()` is explicitly unsupported, and rename/delete/list/status/mkdir/working-directory methods operate through remote FTP commands.

Statistics flow starts with live `IOStatistics` maps on a stream or store. `IOStatisticsSupport.retrieveIOStatistics()` extracts them from a source, `IOStatisticsSnapshot.snapshot()` copies them, `aggregate()` merges them into synchronized map state, and logging utilities defer expensive stringification until a log statement evaluates the wrapper object.

HA control flow is command/RPC oriented. Admin clients identify an `HAServiceTarget`, optionally check fencing configuration, obtain protocol proxies, monitor health, request state transitions, and fence failed peers through a configured `FenceMethod`. Observer transition support is explicit and can be disabled by a target.

Writable control flow is caller-driven serialization. Writers call `write(DataOutput)` in deterministic order; readers instantiate or reuse an object and call `readFields(DataInput)` in the matching order. Containers add length/type/class metadata before delegating nested payloads. `RawComparator` and `BinaryComparable` support sort/shuffle paths that compare serialized bytes directly.

SequenceFile writer flow converges through overloads into a writer configured with filesystem/path or raw output stream, key/value classes, compression type, optional codec, metadata, and creation options. Records are then laid out in one of the documented uncompressed, record-compressed, or block-compressed forms with sync markers for resynchronization.

## State and Persistence Behavior

The XML file persists the Hadoop Common 3.3.5 API surface for compatibility tooling. It does not persist application runtime state.

The APIs described here are stateful in several ways. `TrashPolicy` carries filesystem, trash path, and deletion interval. `CommonAuditContext` has thread-local maps, global maps, supplier-valued entries, a process id, and generated thread ids. Its Javadoc warns that long-lived suppliers must not capture large object instances and should be removed when no longer needed.

`IOStatisticsSnapshot` intentionally persists copied statistics maps and is `Serializable` so frameworks such as Spark or Flink can propagate statistics. The docs warn not to deserialize untrusted Java object streams unless the required class list is used. `MeanStatistic` persists sum/sample state and normalizes invalid sample counts to an empty statistic.

Writable classes define binary persistence contracts through `write()` and `readFields()`. Mutable wrappers store current primitive values, byte arrays, array references, maps, declared classes, element types, or class-id maps. `BytesWritable.getBytes()` exposes backing capacity, not only logical length. `ArrayPrimitiveWritable` wraps primitive arrays without copying. `CompressedWritable` stores compressed bytes until lazy inflation.

`AbstractMapWritable` and `MapWritable` persist per-instance class-id tables along with entries. `ObjectWritable` persists class names/declared types and payloads, creating compatibility and classloading dependencies at read time. `DefaultStringifier` stores serialized objects as strings in `Configuration`.

File persistence is explicit in `MapFile` and `SequenceFile`. `MapFile` uses directory state with `data` and `index` files and can rebuild a corrupt index from data. `SequenceFile` persists key/value class names, compression metadata, sync markers, and one of three documented record/block layouts. These formats are durable compatibility contracts for Hadoop data files.

## Dependencies and Integration Points

- Java APIs: `IOException`, `Serializable`, `ByteBuffer`, `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `FileChannel`, `WritableByteChannel`, `Socket`, `MessageDigest`, `URI`, `InetSocketAddress`, collections, `Supplier`, and Java serialization.
- Hadoop configuration and filesystem APIs: `Configuration`, `Configurable`, `FileSystem`, `FileContext`, `Path`, `FileStatus`, `FSDataInputStream`, `FSDataOutputStream`, `FsPermission`, `Options.CreateOpts`, and `Progressable`.
- Hadoop audit and object-store integration: `CommonAuditContext` references `AuditConstants#PARAM_COMMAND` and `HttpReferrerAuditHeader`, and the statistic-name constants are clearly aligned with S3A/object-store operations, multipart uploads, HTTP actions, vectored reads, seeks, and remote stream handling.
- HA/RPC integration: `HAServiceProtocol`, `HAServiceTarget`, `ZKFCProtocol`, protobuf generated blocking interfaces, and Hadoop `VersionedProtocol`.
- Hadoop serialization/data path integration: `Writable`, `WritableComparable`, `RawComparator`, `SequenceFile`, `MapFile`, `ObjectWritable`, `GenericWritable`, `Stringifier`, `JsonSerialization`, and compression codec classes referenced by `SequenceFile`.
- Logging integration: `org.slf4j.Logger` is used by `FTPFileSystem`, `IOStatisticsLogging`, and `IOUtils`.

## Risks and Edge Cases

- The chunk starts inside `TrashPolicy` and ends inside `ShortWritable`; adjacent chunk research must be merged before making whole-class claims about either boundary.
- JDiff records API shape and Javadocs, not implementation bodies. Details such as FTP command sequencing, synchronization internals, map implementations, buffer growth, and exact exception messages require Java source validation.
- The old `TrashPolicy.getCurrentTrashDir()` is documented as incorrect for HDFS encryption-zone deletes. Callers deleting encryption-zone paths should use `getCurrentTrashDir(Path)`.
- `CommonAuditContext` supplier entries are long-lived and may be evaluated on another thread. Capturing large objects, request-scoped objects, or mutable state can create memory leaks or misleading audit output.
- `IOStatisticsSupport.snapshotIOStatistics()` is explicitly not atomic. Concurrent updates can produce mixed snapshots unless the source implementation provides its own synchronization.
- `IOStatisticsSnapshot` is serializable, but its Javadoc warns against untrusted Java deserialization. Tests and integrations should prefer controlled class lists or JSON serialization when crossing trust boundaries.
- Statistic-name constants are cross-component contracts. Renaming or reusing a key can break dashboards, assertions, object-store diagnostics, and downstream log parsers.
- FTP filesystem semantics are weaker than HDFS/local filesystems. Append is unsupported; rename is constrained by same-directory behavior; streams may need to be closed before other APIs are used; credentials and host details are configuration-sensitive.
- HA fencing is safety-critical. A `tryFence()` false result or misvalidated args can permit split-brain. Observer transitions require explicit target support.
- Writable binary compatibility is fragile. Changes to field order, class metadata, length prefixes, enum element typing, or `ObjectWritable` compact-array mode can break persisted files, RPC payloads, and inter-version reads.
- Backing-array exposure in `BytesWritable` and no-copy array wrapping in `ArrayPrimitiveWritable` can leak stale bytes, retain large buffers, or allow external mutation after serialization assumptions have been made.
- `SequenceFile` has many deprecated writer overloads kept for compatibility. New code should use `createWriter(Configuration, Writer.Option...)`, but compatibility tests must still cover legacy overload behavior.
- `MapFile.fix()` can repair an index from data, but incorrect key/value classes or data corruption can produce partial recovery or misleading valid-entry counts.

## Test Signals

- API baseline tests should verify this JDiff slice remains well-formed around the chunk boundaries and that generated signatures/deprecations match Java sources for Hadoop Common 3.3.5.
- Trash tests should cover checkpoint deletion, path-aware trash location under encryption-zone and non-encryption-zone paths, emptier behavior, configured policy instantiation, and deprecation compatibility for the old factory.
- XAttr tests should round-trip text, quoted text, hex, base64, invalid encodings, and `XAttrSetFlag.validate()` create/replace combinations.
- Audit tests should cover thread-local isolation, global context propagation, `noteEntryPoint()`, supplier evaluation/removal, `reset()` behavior, process/thread id stability, and memory-sensitive supplier cleanup.
- FTP tests should cover configuration keys, default port/scheme, open/create stream close ordering, unsupported append, recursive and nonrecursive delete, same-directory rename constraints, list/status/mkdirs, working directory behavior, and timeout/data-transfer modes.
- IO statistics tests should cover all map categories, unset min/max sentinels, `DurationStatisticSummary` extraction, synchronized snapshot and aggregate behavior, mean-statistic invalid sample handling, JSON serialization, required deserialization classes, lazy logging wrappers, null/wrong-type sources, and stable statistic-name constants.
- HA tests should cover `FenceMethod.checkArgs()` and `tryFence()`, target proxy creation with timeouts, transition request helper methods, health-monitor address fallback/separation, ZKFC proxy lookup, fencing parameter extension, auto-failover flags, observer support, and protobuf protocol version compatibility.
- Writable tests should round-trip every primitive writable in this chunk, `BytesWritable`, arrays, enum sets, maps, object wrappers, `MD5Hash`, `NullWritable`, and compressed writables. Include golden-byte compatibility tests against earlier Hadoop versions where serialized formats are durable.
- Comparator tests should compare object-level ordering with raw byte ordering for `BinaryComparable`, primitive writables, `BytesWritable`, and `MD5Hash`.
- `IOUtils` tests should simulate partial reads/skips/writes, EOF, cleanup swallowing/logging, socket close, directory-list exceptions, fsync on file and directory paths, compressed-read exception wrapping, and unbounded `readFullyToByteArray()` memory risk.
- `MapFile`/`SequenceFile` tests should cover writer overloads, metadata, compression type defaults, codec use, sync markers, create-parent behavior, raw output-stream writers, corrupt/missing index repair, dry-run repair, and directory constant expectations.

## Cross-Chunk Notes

`subset-b-007220` should contain the earlier part of `TrashPolicy` and filesystem APIs preceding this slice. `subset-b-007222` should continue after `ShortWritable`, including the rest of `org.apache.hadoop.io` and subsequent packages. The merge lane should preserve this chunk as a source-aligned subsection and avoid treating it as a complete file-level analysis until all seven chunks for `Apache_Hadoop_Common_3.3.5.xml` are present.
