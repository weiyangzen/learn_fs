# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.7.2.xml lines 11916-17986

## Purpose

This chunk is part 3 of the Hadoop Common 2.7.2 JDiff API XML. It records generated public API metadata, not executable implementation bodies. The useful research signal is the public contract: packages, class/interface names, inheritance, implemented interfaces, method and constructor signatures, checked exceptions, fields, deprecation state, and Javadoc summaries.

The span starts at the tail of `org.apache.hadoop.fs.Syncable`, covers filesystem trash, xattr, FTP, permission/ACL, viewfs, HA, protobuf bridge, HTTP filter-package docs, and a large portion of `org.apache.hadoop.io`, ending inside the `Text.clear()` method documentation. Later chunks must complete the `Text` API and the rest of the file.

## API Inventory

### `org.apache.hadoop.fs` tail

- The chunk begins with the `Syncable` `hsync()`-style contract: flush client-buffered data through the OS to the disk device, with disk cache caveats, and throw `IOException` on error. `Syncable` is the flush/sync capability interface used by Hadoop streams.
- `Trash` extends `Configured` and wraps a configured `TrashPolicy`. Constructors accept a `Configuration` or an explicit `FileSystem` plus `Configuration`. `moveToAppropriateTrash(FileSystem, Path, Configuration)` handles symlinks and mount points by resolving the target volume and moving the deleted path to that volume's trash. Instance APIs expose `isEnabled()`, `moveToTrash(Path)`, `checkpoint()`, `expunge()`, and `getEmptier()`.
- `TrashPolicy` is the abstract pluggable policy base. Implementations must `initialize(Configuration, FileSystem, Path)`, report `isEnabled()`, move paths into trash, create/delete checkpoints, expose `getCurrentTrashDir()`, and provide a superuser emptier `Runnable`. The static `getInstance` factory uses `fs.trash.classname`. Protected state includes `fs`, `trash`, and `deletionInterval`.
- `UnsupportedFileSystemException` is an `IOException` raised when a filesystem scheme/name is unsupported.
- `XAttrCodec` is an enum API for xattr value string conversion. `decodeValue(String)` recognizes `0x`/`0X` hexadecimal, `0s`/`0S` base64, double-quoted text, or bare text. `encodeValue(byte[], XAttrCodec)` emits text, hex, or base64 string forms.
- `XAttrSetFlag` is an enum with static `validate(String xAttrName, boolean xAttrExists, EnumSet flag)` to enforce create/replace semantics and throw `IOException` for invalid extended-attribute writes.
- `org.apache.hadoop.fs.crypto` is present as an empty package in this chunk.

### `org.apache.hadoop.fs.ftp`

- `FTPException` is a runtime wrapper around message/cause variants.
- `FTPFileSystem` extends `FileSystem` and exposes the `ftp` scheme. It initializes from a `URI` and `Configuration`, supports `open`, `create`, `delete`, `listStatus`, `getFileStatus`, `mkdirs`, `rename`, working/home directory accessors, and `setWorkingDirectory`.
- FTP constants include `DEFAULT_BUFFER_SIZE`, `DEFAULT_BLOCK_SIZE`, `FS_FTP_USER_PREFIX`, `FS_FTP_HOST`, `FS_FTP_HOST_PORT`, `FS_FTP_PASSWORD_PREFIX`, and `E_SAME_DIRECTORY_ONLY`. The class also exposes a Commons Logging `LOG`.
- `create` warns that the returned stream must be closed before calling other APIs or later invocations can block. `append` is documented as unsupported.

### `org.apache.hadoop.fs.permission`

- `AccessControlException` extends `IOException` for filesystem permission denial and supports empty, message, and cause constructors.
- `AclEntry` is an immutable ACL entry with type, optional name, `FsAction` permission, and scope. It exposes accessors, `equals`, `hashCode`, `toString`, `parseAclSpec(String, boolean)`, `parseAclEntry(String, boolean)`, and `aclSpecToString(List)`. Parsing supports full set-ACL specs with permissions and remove-ACL specs without permissions.
- `AclEntryScope` and `AclEntryType` are enum APIs for ACL scope and ACL principal/type.
- `AclStatus` is an immutable ACL status value containing owner, group, sticky bit, ordered entries, and base `FsPermission`. It computes effective permissions for an `AclEntry`, including an overload that accepts a permission argument for compatibility with older NameNodes and can throw `IllegalArgumentException` when required permission data is missing.
- `FsAction` is an enum for read/write/execute combinations. APIs include `implies`, `and`, `or`, `not`, `getFsAction(String)`, and public `SYMBOL` text.
- `FsPermission` is a `Writable` representation of Unix-style Hadoop permissions. Constructors accept user/group/other `FsAction` triples, sticky-bit variants, a short mode, another permission, or an octal/symbolic string. APIs cover immutable creation, per-class action access, `fromShort`, `write/readFields/read`, `toShort`, `toExtendedShort`, equality/hash/string conversion, `applyUMask`, `getUMask`, sticky/ACL/encrypted bits, `setUMask`, default directory/file/cache-pool permissions, and symbolic `valueOf`.
- Permission constants include `MAX_PERMISSION_LENGTH`, `DEPRECATED_UMASK_LABEL`, `UMASK_LABEL`, and `DEFAULT_UMASK`. The `getDefault()` Javadoc notes the historical executable-bit behavior for files and points callers to `getDirDefault()` and `getFileDefault()`.

### `org.apache.hadoop.fs.viewfs`

- `org.apache.hadoop.fs.shell.find` is an empty package marker here.
- `NotInMountpointException` extends `UnsupportedOperationException` for paths not mounted through viewfs. It supports path/method and string constructors plus `getMessage()`.
- `ViewFileSystem` extends `FileSystem` and implements the classic `FileSystem` API over a client-side mount table. It supports `viewfs` scheme initialization, URI and path resolution, trash-location lookup, home/working directory handling, append/create/createNonRecursive/delete, block locations, checksum, file status, access checks, listing, mkdirs, open, rename, truncate, ownership, permissions, replication, times, ACL operations, xattr operations, checksum toggles, default block size/replication/server defaults, content summary, child filesystem enumeration, and mount-point listing.
- `ViewFs` extends `AbstractFileSystem` and provides the newer FileContext/AbstractFileSystem surface for the same client-side mount table model. It exposes server defaults, default port, home directory, `resolvePath`, internal create/delete/status/access/open/truncate/rename APIs, symlink support, owner/permission/replication/time updates, checksum toggles, delegation tokens, name validation, ACL operations, xattr operations, and mount-point listing.
- The `ViewFs` package documentation describes mount-table configuration under `fs.viewfs.mounttable.*`, default vs authority-named mount tables, and merge-mount configuration syntax, while noting merge mounts are not implemented yet.

### `org.apache.hadoop.ha`

- `BadFencingConfigurationException` and `FailoverFailedException` describe invalid fencing configuration and failed failover, respectively.
- `FenceMethod` is the operator/plugin contract for fencing an HA service. `checkArgs(String)` validates configured arguments at startup. `tryFence(HAServiceTarget, String)` attempts to prevent a target from making progress and returns success/failure/indeterminate as a boolean, with runtime configuration validation via `BadFencingConfigurationException`.
- `HAServiceProtocol` is the RPC-facing HA primitive contract. It declares `monitorHealth()`, `transitionToActive(StateChangeRequestInfo)`, `transitionToStandby(StateChangeRequestInfo)`, and `getServiceStatus()`. It throws `HealthCheckFailedException`, `ServiceFailedException`, `AccessControlException`, and `IOException` as appropriate, and exposes `versionID`.
- `HAServiceProtocolHelper` wraps HA protocol RPC calls and unwraps `RemoteException` into specific checked exceptions for health and state transitions.
- `HAServiceTarget` models a client-side HA administration target. Subclasses provide the IPC address, ZKFC address, `NodeFencer`, and fencing preflight validation. The base class creates HA and ZKFC protocol proxies, exposes final fencing parameters, lets subclasses add fencer environment/script parameters, and reports whether automatic failover is enabled.
- `HealthCheckFailedException` and `ServiceFailedException` are `IOException` subclasses for unhealthy services and failed state-changing operations.

### `org.apache.hadoop.ha.protocolPB` and `org.apache.hadoop.http.lib`

- `HAServiceProtocolPB` and `ZKFCProtocolPB` are protobuf RPC bridge interfaces. Each implements the generated protobuf blocking service interface plus `VersionedProtocol`.
- `org.apache.hadoop.http.lib` has package-level docs for user-selectable web UI filter initializers configured through `hadoop.http.filter.initializers`, including `StaticUserWebFilter`.

### `org.apache.hadoop.io` maps, arrays, bytes, and simple writables

- `AbstractMapWritable` is the shared `Writable`/`Configurable` base for `MapWritable` and `SortedMapWritable`. It maps runtime classes to byte IDs per instance rather than through static tables, supports synchronized class registration/copy, ID/class lookup, configuration access, and `write/readFields`. The class-ID range is documented as 1-127.
- `ArrayFile` extends `MapFile` as a dense integer-to-value file mapping.
- `ArrayPrimitiveWritable` wraps primitive arrays without per-element objects and without copying the underlying array. It exposes declared/actual component type, setter/getter, and `Writable` serialization.
- `ArrayWritable` wraps homogeneous `Writable[]` values with a value class, string-array constructor, `toStrings`, `toArray`, `set/get`, and `write/readFields`. Docs warn reducers often need typed subclasses.
- `BinaryComparable` is the byte-oriented comparable base used by byte-backed writable comparables. Subclasses provide `getLength()` and `getBytes()`, while the base implements byte-wise comparisons, equality, and hashing via `WritableComparator` semantics.
- `BloomMapFile` adds a dynamic Bloom filter to `MapFile` for faster sparse key membership tests. It exposes static `delete(FileSystem, String)` plus `BLOOM_FILE_NAME` and `HASH_COUNT`.
- `BooleanWritable`, `ByteWritable`, `DoubleWritable`, `FloatWritable`, `IntWritable`, `LongWritable`, and `ShortWritable` are scalar `WritableComparable` wrappers. Their common contract is default/value constructors, `set`, `get`, `readFields`, `write`, `equals`, `hashCode`, `compareTo`, and `toString`.
- `BytesWritable` is a resizable byte sequence usable as a key or value. It distinguishes logical length from backing capacity, exposes copy/raw byte access, deprecated `get()`/`getSize()` aliases, size/capacity mutation, range setters, serialization, memcmp-style equality/order semantics, and hex-pair `toString()`.
- `ByteBufferPool` is the buffer leasing interface with `getBuffer(boolean direct, int length)` and `putBuffer(ByteBuffer)`.
- `ElasticByteBufferPool` is a synchronized, unbounded caching `ByteBufferPool` that returns the smallest cached buffer with sufficient capacity, creating buffers as needed.
- `Closeable` is a deprecated Hadoop alias for `java.io.Closeable`.

### `org.apache.hadoop.io` serialization helpers and containers

- `CompressedWritable` is an abstract `Writable` base for lazily inflated compressed data. Public `readFields` and `write` are final; subclasses implement `readFieldsCompressed` and `writeCompressed`, and must call `ensureInflated()` before field access.
- `DataOutputOutputStream` adapts `DataOutput` to `OutputStream`, returning the original object if it already is an `OutputStream`.
- `DefaultStringifier<T>` implements `Stringifier<T>` by serializing through Hadoop `SerializationFactory` and base64-encoding the result. It can stringify/fromString instances, close underlying resources, and store/load single objects or arrays from `Configuration` keys.
- `EnumSetWritable<E>` wraps `EnumSet` for `Writable` serialization and is also `Configurable`. Empty/null enum sets require an explicit element type. It implements collection iteration, size, add, reset, equality/hash/string, element-type access, and configuration access.
- `GenericWritable` is an efficient polymorphic wrapper for a fixed set of writable classes declared by subclass `getTypes()`. It avoids writing a class name for every value and passes configuration into wrapped `Configurable` instances before deserialization.
- `MapWritable` extends `AbstractMapWritable` and implements `Map<Writable, Writable>` operations with serialization of dynamic key/value classes.
- `SortedMapWritable` extends `AbstractMapWritable` and implements `SortedMap<WritableComparable, Writable>` operations including `firstKey`, `lastKey`, `headMap`, `subMap`, and `tailMap`.
- `ObjectWritable` is a polymorphic `Writable` that records the declared class name and handles writables, strings, primitive types, and arrays. Static `writeObject` has an `allowCompactArrays` flag intended for RPC/internal usage while preserving older persisted-file compatibility when disabled. Static `readObject` overloads reconstruct objects, and `loadClass` consults `Configuration`.
- `Stringifier<T>` is the closeable interface for converting objects to and from string representations.

### `org.apache.hadoop.io` IO utilities, hashes, files, comparators, and sequence files

- `IOUtils` provides stream/channel utilities: multiple `copyBytes` overloads with buffer size, configuration, count, and close behavior; `wrappedReadForCompressedData`; `readFully`; `skipFully`; cleanup/close helpers for streams and sockets; `writeFully` for `ByteBuffer` to `WritableByteChannel` or `FileChannel` at offset; and `listDirectory(FileSystem, Path)` excluding CRC files.
- `MapFile` is a file-backed sorted key/value map stored as a directory containing `data` and `index` files. Static utilities rename, delete, and `fix` corrupt maps by recreating the index, with a `main` entry point. Public constants name the index and data files.
- `MD5Hash` is a 16-byte `WritableComparable` digest wrapper. It can be built from empty state, hex string, or bytes; read/write from data streams; copy another digest; expose digest bytes; compute digests from byte arrays, ranges, input streams, strings, and deprecated `UTF8`; provide thread-local digesters; derive half/quarter digest values; compare, hash, stringify, and set from hex.
- `MultipleIOException` wraps a list of `IOException` values and offers `createIOException(List)` for convenient aggregation.
- `NullWritable` is a singleton zero-data writable comparable whose read/write are no-ops and whose comparison/equality treat all instances as equivalent.
- `RawComparator<T>` extends `Comparator<T>` with direct byte-array comparison for serialized object representations.
- `SequenceFile` APIs in this chunk cover default compression configuration and a large set of static `createWriter` overloads. The preferred modern form is `createWriter(Configuration, Writer.Option...)`; many older overloads taking `FileSystem`, `FileContext`, paths, key/value classes, buffer/replication/block size, compression type, codec, progress, metadata, create flags, and create options are documented as deprecated in favor of the option-based writer.
- `SequenceFile.SYNC_INTERVAL` is the sync-marker interval. The class documentation describes the binary file format: header with version, key/value class names, compression flags and codec, metadata, and sync marker; uncompressed records; record-compressed records; block-compressed records with separate compressed key-length, key, value-length, and value blocks; and sync markers.
- `SetFile` extends `MapFile` as a file-backed set of keys.
- `Text` begins in this chunk. It extends `BinaryComparable` and implements `WritableComparable`. Constructors accept empty, `String`, another `Text`, or a byte array. Covered methods include `copyBytes`, raw `getBytes`, `getLength`, UTF-8 scalar `charAt`, byte-position `find` overloads, `set` from string/byte array/other text/range, `append`, and the start of `clear()` documentation.

## Control Flow and State

The XML only exposes control flow through API contracts and Javadocs. Filesystem delete-to-trash flow is delegated from `Trash` to a configured `TrashPolicy`; `moveToAppropriateTrash` adds resolution through symlinks and mount points so the trash location is on the actual target volume. Checkpoint and expunge operations imply periodic lifecycle behavior through `getEmptier()`.

Viewfs operations flow through a client-side mount table. `ViewFileSystem` and `ViewFs` resolve incoming viewfs paths to mounted target filesystems, then delegate filesystem operations while preserving the appropriate `FileSystem` or `AbstractFileSystem` API shape. Operations that require target metadata expose checked exceptions for access denial, missing files, unresolved links, and IO failures.

HA control flow is explicit: monitoring checks health, transition calls request active/standby state changes, failover/fencing code uses `HAServiceTarget` to build proxies and fencing parameters, and configured `FenceMethod` implementations are attempted by the HA framework. Fencing methods return boolean success rather than throwing for normal failed attempts, reserving `BadFencingConfigurationException` for invalid configuration.

Hadoop IO classes split into mutable value wrappers, file formats, and serialization helpers. Writables are stateful objects whose fields are replaced by `readFields` and emitted by `write`. `CompressedWritable` specifically delays inflation until access. `AbstractMapWritable` maintains per-instance type-ID mappings as part of map state, while `MapFile` and `SequenceFile` define durable on-disk record layouts.

## State and Persistence

Persistent contracts are concentrated in `Writable` implementations and file-format helpers. `FsPermission`, scalar writables, byte/array/map writables, `MD5Hash`, `NullWritable`, `ObjectWritable`, `GenericWritable`, `CompressedWritable`, `EnumSetWritable`, and related classes all expose `write(DataOutput)` and `readFields(DataInput)`.

`MapFile` and `SequenceFile` define durable filesystem artifacts. `MapFile` persists sorted data and an in-memory-loaded index file; `SequenceFile` persists typed key/value streams with optional record or block compression and sync markers. `BloomMapFile` adds a Bloom-filter side file for membership acceleration.

Configuration-backed persistence appears in `DefaultStringifier.store/load` and `FsPermission.getUMask/setUMask`. Runtime-only state appears in `TrashPolicy` fields, `ViewFs` mount tables, HA proxies/fencing parameter maps, and FTP working-directory/connection state. The XML does not prove internal field layouts beyond fields that are part of the public/protected API.

## Dependencies and Integration Points

- Filesystem APIs depend on `Configuration`, `Configured`, `FileSystem`, `AbstractFileSystem`, `FileContext`, `Path`, `FileStatus`, `BlockLocation`, `FileChecksum`, `FsServerDefaults`, `ContentSummary`, `RemoteIterator`, `PathFilter`, `Options.CreateOpts`, `CreateFlag`, `Progressable`, and Java IO exceptions.
- Trash integrates with configurable policy class loading through `fs.trash.classname`, target filesystem resolution, home directories, and superuser emptier scheduling.
- FTP integrates with Apache Commons Logging, FTP host/user/password/port configuration keys, Hadoop stream wrappers, and the `FileSystem` contract.
- ACL and permission APIs integrate with NameNode/file-status metadata, shell parsing of ACL specs, old-NameNode compatibility for effective permissions, and umask configuration.
- Viewfs integrates with mount-table configuration under `fs.viewfs.mounttable.*`, delegated child filesystems, delegation-token collection, ACL/xattr support, symlink handling, and both `FileSystem` and `AbstractFileSystem` client APIs.
- HA APIs integrate with Hadoop RPC/protobuf, `VersionedProtocol`, ZKFC protocols, `NodeFencer`, `HAServiceStatus`, security `AccessControlException`, and service-specific implementations such as HDFS NameNode HA.
- IO APIs integrate with Hadoop serialization, compression codecs, Java `DataInput/DataOutput`, NIO channels and buffers, `MessageDigest`, `Configuration`, `FileSystem`, and `WritableComparator`/`RawComparator` sort paths.

## Risks and Edge Cases

- This is generated JDiff XML; it is authoritative for the generated compatibility snapshot, but it does not show implementation branches, validation details, synchronization beyond method flags, or private fields.
- Trash behavior is path-resolution sensitive. Incorrectly resolving symlinks or mount points can move deleted data into the wrong volume's trash or skip trash when users expect recoverability.
- FTP streams can block later API calls if callers do not close a stream returned by `create`. `append` is advertised but unsupported, so clients must handle `IOException` or unsupported-operation behavior.
- XAttr decoding has multiple string syntaxes; callers must distinguish text from hex/base64 prefixes and quoted strings. Invalid flag combinations in `XAttrSetFlag.validate` are expected to fail early.
- ACL parsing has two modes: specs with permissions and removal specs without permissions. Mixing these can produce incorrect ACL entries or validation failures.
- `FsPermission.toExtendedShort()` can encode values outside the historical `00000-01777` range because ACL/encryption bits may be included; code assuming plain POSIX mode ranges can misinterpret metadata.
- Viewfs is entirely client-side. Mount-table misconfiguration, authority mismatch, incomplete ACL/xattr support on target filesystems, and cross-filesystem rename/delete semantics are key integration risks.
- Fencing methods are operator supplied and may perform destructive external actions. `tryFence` returning false includes indeterminate results, so failover orchestration must treat false conservatively.
- `AbstractMapWritable` allows only 127 distinct classes per map instance. Dynamic or user-controlled map contents can exhaust that ID space.
- `BytesWritable.getBytes()` and `Text.getBytes()` expose backing arrays where only `getLength()` bytes are valid. Using capacity rather than length leaks stale bytes into comparisons, hashes, or output.
- `ArrayPrimitiveWritable` does not copy the wrapped primitive array, so external mutation after wrapping changes serialized state.
- `ObjectWritable` class-name persistence is flexible but expensive and can be compatibility sensitive. Compact array serialization is explicitly not for inter-cluster or persisted-file interchange.
- `SequenceFile` has many deprecated writer overloads; new call sites should prefer `Writer.Option...` to avoid overload ambiguity and compatibility churn. Block-compressed records have a more complex layout and require codec compatibility.
- The chunk ends mid-`Text`; consumers must merge with the next chunk before treating `Text` coverage as complete.

## Test Signals

- API compatibility checks should assert every class, interface, method, constructor, field, visibility, inheritance relationship, implemented interface, deprecation marker, and checked exception recorded in lines 11916-17986.
- Trash tests should cover disabled trash, paths already in trash, symlink and mount-point deletion, checkpoint creation, expunge deletion, and emptier scheduling behavior.
- XAttr tests should cover text, quoted text, hex, base64, invalid encodings, and create/replace flag validation for existing and missing attributes.
- FTP filesystem tests should cover initialization from URI/config, default port, configured credentials, open/create/close ordering, unsupported append, recursive/non-recursive delete, same-directory rename constraints, list/status behavior, and working-directory resolution.
- Permission and ACL tests should cover ACL spec parsing for set vs remove modes, effective permission with and without old-NameNode permission arguments, symbolic/octal permissions, extended short bits, umask parsing including deprecated decimal config, default directory/file/cache-pool permissions, and `Writable` round trips.
- Viewfs tests should cover mount-table initialization, default and named authorities, path resolution, trash locations, delegation to child filesystems, access/list/status/open/create/delete/rename/truncate, ACL/xattr forwarding, symlink support, delegation-token aggregation, and cross-mount edge cases.
- HA tests should cover fencing argument validation, false/true fencing results, fencing parameter maps, proxy creation, health-monitor exceptions, active/standby transition exceptions, `RemoteException` unwrapping by `HAServiceProtocolHelper`, protobuf bridge compatibility, and auto-failover flags.
- IO serialization tests should cover scalar writable round trips and comparisons, `BytesWritable` length vs capacity, `Text` UTF-8 scalar/index behavior for the methods present here, `ArrayPrimitiveWritable` primitive array types, `ArrayWritable` typed subclass usage, map writable dynamic class registration and 127-class limit, `EnumSetWritable` empty/null set element types, `GenericWritable` type whitelist enforcement, `ObjectWritable` primitive/array/writable cases with compact arrays on/off, `MD5Hash` known digests, `IOUtils` copy/skip/read/write boundary conditions, `MapFile.fix` dry-run and repair modes, and `SequenceFile` writer overload compatibility plus uncompressed/record-compressed/block-compressed layout round trips.
