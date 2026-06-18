# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.5.0.xml lines 24627-30661

## Scope And Purpose

This chunk is a JDiff API snapshot for Apache Hadoop Common 3.5.0. It is not executable Java source; it records the public and protected API surface, signatures, exceptions, inheritance, deprecation text, and extracted Javadoc for part of `hadoop-common`. The line range starts in the middle of `org.apache.hadoop.fs.viewfs.ViewFileSystem` and ends in the middle of `org.apache.hadoop.io.Text`, so the research covers only the members visible in this slice.

The chunk spans three major API areas:

- ViewFS client-side mount-table APIs: `ViewFileSystem`, `ViewFileSystemUtil`, and `ViewFs`.
- High availability and HTTP support APIs: HA protocol, fencing, service-target abstractions, protobuf protocol markers, and small HTTP config enums/constants.
- Hadoop IO serialization and file-format APIs: `Writable` wrappers, map and sequence-file formats, stringification, buffer pools, hash utilities, and the first part of `Text`.

Because this XML is used for API comparison, its main purpose is compatibility tracking. Any signature, return type, exception, visibility, deprecation marker, enum member, nested type reference, or documented behavior in this chunk is part of Hadoop Common's compatibility surface.

## ViewFS APIs

`ViewFileSystem` extends the classic `FileSystem` API and implements a client-side mount table with behavior documented as identical to `ViewFs`. The visible members expose the normal filesystem operations and forward them through ViewFS path resolution: initialization, URI/scheme access, working directory, open/create/append/delete/rename/truncate, mkdirs, status/listing, block locations, checksums, ACLs, xattrs, snapshots, storage policies, content/quota usage, trash roots, filesystem status, child filesystems, mount points, link targets, path capabilities, enclosing root, and close.

The most important behavior documented in this chunk is mount-link status handling. `getFileStatus(Path)` resolves a mount link to its target and returns the target status as a normal file or directory. `listStatus(Path)` defaults to representing immediate mount-link children as symlinks, with `getSymlink()` carrying the target; this can be changed by `fs.viewfs.mount.links.as.symlinks=false`, in which case target attributes are surfaced directly. `listStatus` also considers fallback links and documents that when the same directory path exists in configured mounts and fallback FS, the fallback path is listed except for links.

Trash root behavior is also a high-signal contract. `getTrashRoot(Path)` accounts for a `FORCE_INSIDE_MOUNT_POINT` flag and can return a target filesystem trash root, a corresponding ViewFS path, or `/{mountpoint}/.Trash/{user}` depending on whether the path, trash, fallback filesystem, encryption zone, snapshot root, or cloud-storage home-directory case requires localizing trash under the mount point. `getTrashRoots(boolean)` similarly returns trash roots under each mount point when forced inside mount points.

`ViewFileSystemUtil` is a final utility class with type-detection helpers for `ViewFileSystem` and `ViewFileSystemOverloadScheme`, plus `getStatus(FileSystem, Path)`. Its status helper maps matching ViewFS mount points to `FsStatus` for a path, including internal mount-tree directories such as `/dept` that resolve to root and aggregate all descendant mount points.

`ViewFs` extends `AbstractFileSystem` and exposes the FileContext-era equivalent surface: server defaults, URI default port, home directory, resolve path, `createInternal`, delete, file block locations, checksum, file/link status, `access`, `getFsStatus`, list iterators, `mkdir`, open, truncate, rename overloads, symlink support, link target, owner/permission/replication/times/checksum flags, mount points, delegation tokens, path validation, ACLs, xattrs, snapshots, and storage policies. As with `ViewFileSystem`, listing documentation emphasizes whether immediate mount links are returned as symlinks or target statuses.

## HA And HTTP APIs

The HA section defines exception types and the client-side protocol used by Hadoop HA frameworks:

- `BadFencingConfigurationException`, `FailoverFailedException`, `HealthCheckFailedException`, and `ServiceFailedException` model fencing, failover, health-check, and service-transition failures.
- `FenceMethod` lets operators implement ordered fencing strategies. `checkArgs(String)` validates configured arguments, and `tryFence(HAServiceTarget, String)` returns true only when fencing succeeds; false covers failure or indeterminate outcomes.
- `HAServiceProtocol` is the RPC contract for health monitoring and failover. It exposes `monitorHealth`, `transitionToActive`, `transitionToStandby`, `transitionToObserver`, `getServiceStatus`, and a public `versionID`.
- `HAServiceProtocolHelper` wraps those RPC calls and unwraps `RemoteException` into the specific checked exceptions.
- `HAServiceTarget` is the abstract client-side target used by HA admin commands. It supplies the service IPC address, optional separate health-monitor RPC address, ZKFC address, fencer, fencing preflight validation, service and ZKFC proxies, transition target status, fencing parameters, auto-failover flag, and observer-state support flag.

State transitions are explicit: services can be active, standby, observer, initializing, or stopping, and transition calls are documented as no-ops when the service is already in the requested state. `RequestSource` captures who requested a transition, and `StateChangeRequestInfo` is passed into transition methods even though that nested class is outside the direct class inventory lines.

The protobuf protocol marker interfaces `HAServiceProtocolPB` and `ZKFCProtocolPB` appear at the package boundary and mark the protobuf-backed RPC integration points. The HTTP section is small: `JettyUtils` exposes UTF-8 and header-size constants, `HttpConfig.Policy` supports string parsing plus HTTP/HTTPS enablement checks, and `HttpServer2.XFrameOption` exposes enum conversion and string rendering for X-Frame-Options behavior.

## Hadoop IO Serialization APIs

The IO portion is the largest part of this chunk and covers Hadoop's long-lived binary serialization surface.

`AbstractMapWritable` is the base for `MapWritable` and `SortedMapWritable`. It implements `Writable` and `Configurable`, stores class-id mappings per map instance rather than statically, and limits class IDs to 1 through 127. Its synchronized `addToMap` and `copy` methods are important because map serialization must preserve the dynamic class table across nested writable maps.

Primitive and byte-oriented writables include `BooleanWritable`, `ByteWritable`, `ShortWritable`, `IntWritable`, `LongWritable`, `FloatWritable`, `DoubleWritable`, `BytesWritable`, and `MD5Hash`. These generally implement `WritableComparable`, expose constructors, `set`/`get`, `readFields`, `write`, equality, hash, comparison, and string conversion. `BytesWritable` distinguishes logical length from backing capacity and has deprecated aliases `get()` and `getSize()`. `BinaryComparable` supplies bytewise comparison, equality, and hash semantics for byte-backed comparables such as `BytesWritable` and `Text`.

Array wrappers include `ArrayPrimitiveWritable`, which wraps primitive arrays without per-element object creation and without copying the underlying array, and `ArrayWritable`, which wraps homogeneous `Writable` arrays. `EnumSetWritable` serializes enum sets and requires an explicit element type when the set is null or empty. `GenericWritable` efficiently wraps one of a fixed set of `Writable` types by writing a compact type discriminator instead of writing a class name for every record, and it propagates configuration to wrapped configurables before deserialization.

`CompressedWritable` is a lazy-inflation base class. Subclasses implement `readFieldsCompressed` and `writeCompressed`; callers that access fields must call `ensureInflated()`. This contract is performance-sensitive for large map/reduce values because compressed data can be copied without full object inflation.

`DefaultStringifier` implements `Stringifier<T>` by serializing objects through Hadoop's `SerializationFactory` and Base64-encoding the result. It provides configuration-backed `store`, `load`, `storeArray`, and `loadArray` helpers, so it is an integration point between object serialization and `Configuration` persistence. The separate `Stringifier<T>` interface defines `toString(T)`, `fromString(String)`, and `close()`.

`ObjectWritable` is the generic object serializer with constructors for object and declared class, read/write methods, static `writeObject` overloads, static `readObject` overloads, class loading, and configuration propagation. The chunk contrasts it indirectly with `GenericWritable`: `ObjectWritable` writes class declarations more often and is less compact for repeated heterogeneous values.

`MapWritable` implements `Map<Writable, Writable>`, while `SortedMapWritable<K>` implements `SortedMap<K, Writable>`. Both inherit the dynamic class table from `AbstractMapWritable` and expose normal map operations plus `readFields` and `write`. `SortedMapWritable` additionally exposes comparator, first/last key, and range-view methods.

## File Format APIs

`SequenceFile` documents Hadoop's binary key/value container format. It exposes default compression configuration and a large overload set of `createWriter` methods. Many old overloads are deprecated in favor of `createWriter(Configuration, Writer.Option...)`; compatibility still matters because the deprecated signatures remain public. Non-deprecated overloads include filesystem-based creation with buffer size, replication, block size, `createParent`, compression type, codec, and metadata, plus FileContext-based creation with create flags and create options.

The file-format documentation is detailed and compatibility-critical. Sequence files share a header containing the `SEQ` magic/version, key class, value class, compression flags, optional compression codec class, metadata, and sync marker. Three writer formats are described: uncompressed records, record-compressed files where only values are compressed, and block-compressed files where key lengths, keys, value lengths, and values are collected into separately compressed blocks. `SYNC_INTERVAL` is the public default sync spacing, documented as 100 KB.

`MapFile` is a directory-backed sorted key/value map with `data` and `index` files. The index is read fully into memory, so key size affects reader memory use. Map files are created by appending entries in order; large updates are expected to be handled by copying an old database and merging a sorted change list. Static APIs support rename, delete, repair-by-recreating-index through `fix`, and a command-line `main`. `ArrayFile`, `SetFile`, and `BloomMapFile` build on this family: dense integer-to-value maps, file-based key sets, and MapFiles with dynamic Bloom filters for faster sparse key lookup. `BloomMapFile` exposes `BLOOM_FILE_NAME` and `HASH_COUNT`.

`NullWritable` is the singleton zero-value writable used where a key or value slot is intentionally empty. `MultipleIOException` aggregates multiple IOExceptions and has a factory method that returns a convenient IOException wrapper. `DataOutputOutputStream` adapts a `DataOutput` to `OutputStream`, returning the original object if it already is an `OutputStream`.

## Buffer, Stream, And Filesystem Utility APIs

`ByteBufferPool` defines `getBuffer(boolean direct, int length)`, `putBuffer(ByteBuffer)`, and a default `release()` method to clear buffers. The documentation promises a returned buffer with at least one byte of capacity, while the `direct` flag requests direct versus heap buffers. `ElasticByteBufferPool` implements this with synchronized get/put methods, caches released buffers, returns the smallest cached buffer with enough capacity, and intentionally does not impose a maximum cache size. This creates a memory-retention risk for large or adversarial buffer sizes.

`IOUtils` collects stream, channel, socket, directory, and fsync helpers. Key methods include `copyBytes` overloads with buffer size, count, configuration-derived buffer size, and optional close behavior; `wrappedReadForCompressedData`; `readFully`; `skipFully`; cleanup methods that deliberately ignore throwables; socket close; channel `writeFully` overloads for short-write handling; `listDirectory` that preserves IOExceptions rather than silently returning null; `fsync(File)` and `fsync(FileChannel, boolean)`; `wrapException` that adds path and method diagnostics while preserving special IOException types; and `readFullyToByteArray(DataInput)` which reads until EOF and must not be used with infinite inputs.

## Text API Slice

The chunk reaches the beginning of `org.apache.hadoop.io.Text`, Hadoop's mutable UTF-8 byte-string implementation extending `BinaryComparable` and implementing `WritableComparable<BinaryComparable>`. Visible constructors accept empty, `String`, another `Text`, or a UTF-8 byte array.

The visible API distinguishes efficient access to the backing array from exact copies: `getBytes()` returns the raw backing bytes valid only up to `getLength()`, while `copyBytes()` returns an exact-length copy. `getTextLength()` returns Unicode code-unit length, `charAt(int)` returns a Unicode scalar value without constructing a `String`, and `find(String[, int])` searches the UTF-8 backing buffer by byte position. Mutators include `set(String)`, `set(byte[])`, `set(Text)`, `set(byte[], int, int)`, `append(byte[], int, int)`, and `clear()`. `clear()` resets logical content but intentionally does not clear or free the backing array; callers must set an empty byte array to release that storage.

The visible serialization methods include `readFields(DataInput)`, `readFields(DataInput, int maxLength)`, static `skip(DataInput)`, `readWithKnownLength(DataInput, int)`, `write(DataOutput)`, and `write(DataOutput, int maxLength)`. The visible part ends at static `decode(byte[])`; later `Text` methods are outside this chunk.

## State And Persistence Behavior

The XML file itself is generated metadata and has no runtime state beyond representing Hadoop's public API at release 3.5.0. The APIs it describes do manipulate or encode persistent state:

- ViewFS state is configuration-derived mount-table state. Operations resolve ViewFS paths to target filesystems, fallback filesystems, trash roots, mount links, and child filesystem instances; persistence is delegated to the target filesystem.
- HA state lives in the managed service, ZKFC, fencing configuration, and RPC endpoints. This API controls transitions and health monitoring but does not itself persist active/standby state.
- Writable objects persist binary records through `DataInput` and `DataOutput`. Backing arrays and map class tables are object-local state that directly affect serialized bytes.
- `SequenceFile`, `MapFile`, `ArrayFile`, `SetFile`, and `BloomMapFile` persist Hadoop's on-disk binary formats. Their headers, sync markers, compression settings, index files, data files, Bloom filter files, and class names are compatibility-critical.
- `DefaultStringifier` persists serialized objects into `Configuration` keys as Base64 text.
- `ElasticByteBufferPool` retains buffers in memory after release and exposes an explicit release hook through `ByteBufferPool`.

## Dependencies And Integration Points

This chunk integrates with core Hadoop and Java APIs: `FileSystem`, `AbstractFileSystem`, `FileContext`, `Path`, `FileStatus`, `LocatedFileStatus`, `FsStatus`, `FsServerDefaults`, `ContentSummary`, `QuotaUsage`, `BlockStoragePolicySpi`, ACL and xattr types, `FsPermission`, `FsAction`, `CreateFlag`, `Options.CreateOpts`, delegation `Token`, `Configuration`, and `Progressable`.

HA APIs integrate with Hadoop IPC and protobuf RPC, `RemoteException` unwrapping, `ZKFCProtocol`, `NodeFencer`, operator-provided fencing scripts or classes, access-control exceptions, and optional lifeline/health-monitor RPC addresses.

IO APIs depend on Java `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `File`, `FileChannel`, `WritableByteChannel`, `ByteBuffer`, `Socket`, `MessageDigest`, collections, enums, and Hadoop serialization infrastructure such as `Writable`, `WritableComparable`, `RawComparator`, `WritableComparator`, `Serialization`, `Serializer`, `Deserializer`, `SerializationFactory`, compression codecs, and SLF4J logging.

The JDiff XML integrates with Hadoop's API compatibility tooling. Consumers compare these generated snapshots across releases to detect additions, removals, deprecations, signature changes, and doc-visible API changes.

## Risks And Edge Cases

- The chunk begins and ends mid-class. A reconciliation pass must merge it with adjacent chunks before drawing whole-file conclusions about `ViewFileSystem` and `Text`.
- ViewFS mount-link status semantics are subtle. `getFileStatus` resolves links, while `listStatus` may present immediate mount children as symlinks unless configured otherwise. Tests must cover both default and `fs.viewfs.mount.links.as.symlinks=false` behavior.
- Fallback filesystem handling can hide configured mount-path entries in listings, so regressions can appear as missing or duplicate directory children.
- Trash-root behavior depends on mount-point boundaries, fallback filesystems, cloud storage home semantics, encryption zones, snapshot roots, and `FORCE_INSIDE_MOUNT_POINT`.
- HA transition APIs are state-changing RPC calls. Incorrect exception unwrapping, access-control handling, or health-monitor address selection can cause failover automation to misclassify service state.
- Fencing APIs deliberately allow custom operator code. Argument validation must happen at startup through `checkArgs`, but `tryFence` can still discover runtime configuration errors.
- Writable serialization is binary compatibility sensitive. Changing field order, class-id assignment, compression markers, sequence-file headers, map-file index behavior, or Text length encoding can break old data.
- `AbstractMapWritable` supports only 127 distinct classes in one instance; large heterogeneous maps can exceed the class-id space.
- `ArrayPrimitiveWritable` and `BytesWritable.getBytes()` expose backing arrays. Callers can mutate internal state or retain oversized arrays if they do not use copy APIs.
- `Text.clear()` does not free the backing byte array. Long-lived `Text` reuse after large values can retain memory.
- `ElasticByteBufferPool` intentionally has no maximum cache size, so it can retain large direct or heap buffers until released or discarded.
- Several SequenceFile writer overloads are deprecated but public; removing or changing them would be an API compatibility break even if newer option-based construction is preferred.
- `readFullyToByteArray(DataInput)` reads until EOF and can hang or exhaust memory on unbounded inputs.

## Test Signals

Useful validation signals for this chunk include:

- JDiff/API compatibility checks between Hadoop Common versions, especially for public/protected signatures, exceptions, visibility, deprecation text, enum identities, fields, and nested type references.
- ViewFS unit and integration tests for mount resolution, fallback links, symlink-vs-target listing modes, ACL/xattr forwarding, snapshots, storage policies, content/quota usage, trash-root selection, status aggregation, and path capabilities.
- HA tests that mock or run HA services to validate health checks, active/standby/observer transitions, access-control failures, service-failure exceptions, lifeline health-monitor addresses, ZKFC proxy creation, and ordered fencing behavior.
- Serialization round-trip tests for every visible `Writable`, including null and empty enum sets, nested `MapWritable`/`SortedMapWritable`, heterogeneous `GenericWritable`, `ObjectWritable` class loading, compressed lazy inflation, exact backing-array length behavior, and configuration propagation.
- Golden-file compatibility tests for `SequenceFile` uncompressed, record-compressed, and block-compressed formats, including header fields, sync markers, metadata, compression codecs, deprecated and option-based writer creation paths, and old-reader/new-writer interoperability.
- MapFile repair and persistence tests for `data`/`index` files, sorted insertion requirements, index memory behavior, rename/delete, dry-run `fix`, `ArrayFile`, `SetFile`, and `BloomMapFile` membership lookup.
- IO utility tests for short reads/writes, EOF handling, close-on-copy semantics, ignored cleanup exceptions, socket close, directory listing errors, fsync files versus directories, exception wrapping, and unbounded-input safeguards.
- `Text` tests for UTF-8 validation, byte-position search, Unicode scalar `charAt`, exact versus backing-byte access, max-length guarded reads/writes, skip behavior, known-length reads, and memory retention after `clear()`.
