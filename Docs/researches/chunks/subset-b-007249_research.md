# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop-core_0.21.0.xml lines 5865-12049

## Scope

This chunk is a JDiff API snapshot for Hadoop Core 0.21.0. It starts inside `org.apache.hadoop.fs.FileUtil`, covers a large portion of the public `org.apache.hadoop.fs` API, the legacy FTP/KFS/S3/S3Native filesystem adapters, filesystem permissions, and much of `org.apache.hadoop.io`, then ends at the first visible `SequenceFile.getCompressionType` method entry.

The source is generated API metadata rather than implementation code. The research surface is therefore the compatibility contract: public/protected classes and interfaces, inheritance, implemented interfaces, constructors, methods, parameters, exceptions, fields, visibility/static/final/abstract/synchronized flags, deprecation markers, and embedded Javadocs.

## Purpose

The filesystem portion documents Hadoop's common filesystem facade and several concrete or wrapper implementations. It includes local file utilities, filter/wrapper filesystems, seekable/positioned stream wrappers, filesystem status/default records, path parsing and qualification, local filesystem implementations, trash handling, protocol-specific adapters for FTP, Kosmos File System, block-based S3, and native S3.

The permission portion documents the 0.21-era `FsPermission` value object and a deprecated package-local `AccessControlException` kept for compatibility with older callers while pointing users to `org.apache.hadoop.security.AccessControlException`.

The `org.apache.hadoop.io` portion documents Hadoop's Writable serialization ecosystem: class-id based map writables, array/map/bloom-map files, mutable primitive Writables, binary comparables, compressed lazy writables, stringification through Hadoop serialization, enum-set wrappers, MapFile indexed storage, MD5 hashes, null and object writables, raw comparators, and the beginning of `SequenceFile`.

## Important APIs, Types, and Functions

### File Utilities and Core Filesystem Wrappers

- The opening range continues `FileUtil` static helpers: local-to-filesystem and filesystem-to-local `copy(...)`, shell path conversion, local directory disk usage, `unZip`, `unTar`, local symlink creation, `chmod` with optional recursion, local temp file creation, and atomic-ish `replaceFile`.
- `FileUtil.HardLink` exposes `createHardLink(File, File)` and `getLinkCount(File)` for Unix/Cygwin/Windows XP hardlink operations.
- `FilterFileSystem` extends `FileSystem` and wraps another `FileSystem` in its public `fs` field. It forwards initialization, URI/path checks, block locations, `open`, `append`, `create`, replication, rename, delete, `deleteOnExit`, listing, working/home directories, status, mkdirs, local copy staging, usage/defaults, file status/checksum, checksum verification, owner/time/permission setters, and primitive create/mkdir hooks.
- `FsConstants` exposes `LOCAL_FS_URI` and `FTP_SCHEME`.
- `FSDataInputStream` wraps an `InputStream` as `DataInputStream` while implementing `Seekable` and `PositionedReadable`: `seek`, `getPos`, positioned `read`, two `readFully` overloads, and `seekToNewSource`.
- `FSDataOutputStream` wraps an `OutputStream` as `DataOutputStream` and implements `Syncable`: constructors with optional `FileSystem.Statistics` and start position, `getPos`, `close`, `getWrappedStream`, `sync`, `hflush`, and `hsync`.
- `FSError` is an `Error` for unexpected filesystem failures presumed to reflect disk errors.
- `FsServerDefaults` and `FsStatus` are `Writable` records for server defaults and capacity/used/remaining filesystem status.

### Paths, Local Filesystems, and Generic FS Options

- `InvalidPathException`, `ParentNotDirectoryException`, and `UnsupportedFileSystemException` define typed path and filesystem resolution failures.
- `LocalFileSystem` extends `ChecksumFileSystem`, exposes the raw filesystem, converts `Path` to `File`, overrides local copy operations, and reports checksum failures.
- `Options.CreateOpts` is a varargs-style create option framework with static factories for block size, buffer size, replication, bytes per checksum, permissions, progress callback, and create-parent choice. Nested value classes expose typed `getValue()` accessors. `getOpt` and `setOpt` retrieve or replace options by type.
- `Options.Rename` is an enum-style rename option with `value()` plus `values()` and `valueOf(...)`.
- `Path` is Hadoop's URI-like path abstraction. Constructors cover string parent/child, `Path` parent/child, raw string, `URI`, and scheme/authority/path components. Methods expose URI conversion, filesystem lookup from `Configuration`, URI-path absolute checks, filesystem absolute checks, final name, parent, suffix, string/equality/hash/order behavior, depth, and qualification against filesystem/default URI and working directory. Constants include `SEPARATOR`, `SEPARATOR_CHAR`, and `CUR_DIR`.
- `PathFilter.accept(Path)` is the single-method filtering contract.
- `PositionedReadable`, `Seekable`, and `Syncable` define the read-at-position, seek/get-position, and sync/hflush/hsync contracts used by stream wrappers and filesystem implementations.
- `RawLocalFileSystem` extends `FileSystem` directly and maps Hadoop paths to host files. It exposes path-to-file conversion, URI/init, open/append/create/primitive create, rename, delete, listing, mkdirs/primitive mkdir, home/working directory, status, local-output staging, close, string rendering, file status, owner, and permission setters.
- `Trash` wraps configured trash behavior: construction from configuration or filesystem plus configuration, `moveToTrash`, checkpointing, expunge, emptier creation, and CLI `main`.

### FTP, KFS, S3, and S3Native Filesystems

- `org.apache.hadoop.fs.ftp.FTPException` is a runtime exception with message, cause, and message+cause constructors.
- `FTPFileSystem` extends `FileSystem` with initialize, open, create, append, delete, URI, listing, file status, mkdirs, rename, working/home directory, and working-directory setter. Public constants include `LOG`, `DEFAULT_BUFFER_SIZE`, and `DEFAULT_BLOCK_SIZE`.
- `KosmosFileSystem` extends `FileSystem` for KFS. It exposes URI/init, working directory, mkdirs, directory/file tests, listing/status, append/create/open, rename/delete, replication defaults and setter, block size, explicit `lock`/`release`, KFS block locations, local copy operations, and local output staging. The package docs describe `fs.kfs.impl`, `fs.default.name`, `fs.kfs.metaServerHost`, `fs.kfs.metaServerPort`, a required KFS jar, and JNI/native library loading through `LD_LIBRARY_PATH`.
- `S3FileSystem` is the older block-based S3 implementation. It can be constructed with a `FileSystemStore`, initializes from URI/configuration, manages working directory, mkdirs, file tests, listing, create/open/rename/delete/status, and default block size. Javadocs say append is unsupported and permissions are currently ignored for mkdir/create.
- `MigrationTool` is a `Configured` `Tool` for rewriting block metadata to migrate old S3 filesystem layouts without touching data files.
- `S3Exception`, `S3FileSystemException`, and `VersionMismatchException` capture S3 communication, fatal S3 filesystem, and stored-version mismatch failures.
- `NativeS3FileSystem` is the object-native S3 implementation, optionally constructed with a `NativeFileSystemStore`. It supports initialize, create/open/delete/status/list/mkdirs/rename, working directory, URI, default block size, and logging. Its docs define directory-marker behavior with `_$folder$`, slash markers, prefix existence, and the rule that a file masks a directory marker.

### Permissions

- `org.apache.hadoop.fs.permission.AccessControlException` extends `IOException`, has no-arg, message, and throwable constructors, and is deprecated in favor of `org.apache.hadoop.security.AccessControlException`.
- `FsPermission` implements `Writable` for user/group/other `FsAction` bits plus sticky bit. It supports construction from actions, actions+sticky bit, short mode, another permission, or octal/symbolic string; immutable creation; action getters; `fromShort`; `write`/`readFields` and static `read`; `toShort`; equality/hash/string rendering; umask application and configuration access; sticky-bit query; default permission; Unix symbolic `valueOf`; and public umask constants including the deprecated umask key.

### Writable Values, Comparators, and Utilities

- `AbstractMapWritable` is a `Writable`/`Configurable` base for map-like Writables with per-instance class-to-byte-ID and byte-ID-to-class tables. It synchronizes class registration and copying, exposes protected class/ID lookup, and serializes the class table.
- `ArrayWritable` wraps homogeneous `Writable[]` values and exposes value-class access, string conversion, object-array conversion, set/get, and `Writable` read/write.
- `BinaryComparable` is an abstract comparable over byte sequences from `getBytes()` and `getLength()`, with byte-array comparison, equality, and hash code based on `WritableComparator`.
- Primitive Writables in this chunk include `BooleanWritable`, `ByteWritable`, `DoubleWritable`, `FloatWritable`, `IntWritable`, and `LongWritable`, each with default/value constructors, set/get, `readFields`, `write`, equality, hash, comparison, and string rendering. Their nested comparators extend `WritableComparator`; `LongWritable.DecreasingComparator` reverses sort order.
- `BytesWritable` extends `BinaryComparable` and implements `WritableComparable` for mutable byte arrays. It has default and byte-array constructors, backing array access through `getBytes()` and deprecated `get()`, logical length/size access, capacity management, two `set` forms, read/write, equality/hash, string rendering, and an optimized comparator.
- `CompressedWritable` is an abstract lazy compressed `Writable`: final `readFields` stores compressed data, `ensureInflated` inflates before subclass field access, subclasses implement `readFieldsCompressed` and `writeCompressed`, and final `write` emits compressed data.
- `DefaultStringifier<T>` implements `Stringifier<T>` using Hadoop serialization and Base64-like string storage. It converts objects to/from strings, closes resources, and stores/loads single objects or arrays in `Configuration`.
- `EnumSetWritable<E extends Enum<E>>` wraps `EnumSet` with optional explicit element type, implements `Writable` and `Configurable`, and exposes collection operations, set/get, read/write, equality/hash/string rendering, element type, and configuration access.
- `GenericWritable` wraps one `Writable` chosen from a subclass-provided `getTypes()` whitelist. It exposes set/get, toString, read/write, and configuration propagation.
- `IOUtils` provides stream helpers: four `copyBytes` overloads with buffer-size and close-control variants, `readFully`, `skipFully`, `cleanup(Log, Closeable...)`, `closeStream`, and `closeSocket`. `IOUtils.NullOutputStream` discards byte and byte-array writes.
- `MultipleIOException` aggregates a list of `IOException`s and has `createIOException(List)` as a convenience factory.
- `NullWritable` is a singleton zero-byte `WritableComparable` with optimized comparator.
- `ObjectWritable` is a polymorphic `Writable`/`Configurable` that records declared class and instance. It handles `Writable`, `String`, primitive types, and arrays; exposes static `writeObject`, two `readObject` overloads, and `loadClass(Configuration, String)`.
- `RawComparator<T>` extends `Comparator<T>` with direct serialized-byte comparison.

### ArrayFile, BloomMapFile, MapFile, MD5, and SequenceFile Boundary

- `ArrayFile` extends `MapFile` as a dense integer-to-value file. `ArrayFile.Reader` supports synchronized seek by ordinal, next value, current key, and random get. `ArrayFile.Writer` appends values with `LongWritable`-style sequential keys.
- `BloomMapFile` augments `MapFile` with a dynamic Bloom filter. It exposes `BLOOM_FILE_NAME`, `HASH_COUNT`, static delete, a reader with `probablyHasKey`, fast Bloom-gated `get`, and `getBloomFilter`, and a writer that updates the Bloom filter during synchronized append and persists it during close.
- `MapFile` defines directory-based indexed key/value storage with `DATA_FILE_NAME` and `INDEX_FILE_NAME`, static rename/delete/fix helpers, and CLI `main`. Its docs state that map files store all entries in a `data` SequenceFile plus a sampled in-memory `index`, and must be written in sorted key order.
- `MapFile.Reader` opens data/index files, exposes key/value classes, synchronized reset/midKey/finalKey/seek/next/get/getClosest/close, and a protected hook for specialized `SequenceFile.Reader` creation.
- `MapFile.Writer` has constructors for key/value classes or comparators, compression type, codec, and progress callbacks. It exposes index interval getters/setters, synchronized close, and synchronized append requiring keys to be greater than or equal to the previous key.
- `MapWritable` extends `AbstractMapWritable` and implements `Map`, forwarding clear, contains, entrySet, get, isEmpty, keySet, put, putAll, remove, size, values, and Writable serialization.
- `MD5Hash` is a `WritableComparable` for 16-byte MD5 values. It can be constructed empty, from hex string, or bytes; read and write itself; copy another hash; expose digest bytes; compute digest from byte arrays, input streams, strings, and `UTF8`; produce half/quarter digests; compare/equal/hash/stringify; and parse hex with `setDigest`. `MD5Hash.Comparator` compares serialized hash bytes.
- The chunk ends at the beginning of `SequenceFile`, with only `getCompressionType(Path, Configuration)` visible in this range.

## Control Flow

The XML does not include method bodies, but the API contracts imply several execution paths.

File utility flow is mostly procedural: copy and merge helpers move bytes among local files and `FileSystem` paths, optional delete-source flags remove inputs after success, archive helpers expand zip/tar content into local directories, and shell/permission/link helpers delegate to OS-level behavior.

Filesystem calls generally enter through `FileSystem`, `FilterFileSystem`, or a concrete adapter. `FilterFileSystem` validates and qualifies paths, then delegates to its wrapped `fs`. `LocalFileSystem` layers checksum behavior over a raw local implementation. `RawLocalFileSystem` maps Hadoop operations to host filesystem calls. FTP, KFS, S3, and NativeS3 translate the same abstract operations into protocol or store-specific requests.

Stream flow separates stateful and positional reads. `FSDataInputStream` forwards `seek/getPos/seekToNewSource` and positioned reads to wrapped streams that implement `Seekable` and `PositionedReadable`. `FSDataOutputStream` tracks position through the wrapped output stream/statistics and forwards sync durability requests.

Path flow starts with URI-like constructors and normalization, then proceeds through `toUri`, absolute-path checks, parent/name/suffix/depth inspection, and `makeQualified` to attach scheme, authority, and working-directory context before filesystem resolution.

Trash flow is policy/configuration driven: construct `Trash`, call `moveToTrash` for deletes that should be recoverable, periodically create checkpoints and expunge old checkpoints, and optionally run an emptier `Runnable`.

Object-store filesystem flow differs from POSIX/HDFS flow. Block-based `S3FileSystem` stores inode metadata and block objects; seek/open can use metadata to locate blocks and S3 range reads. Native S3 stores each file as a native object and infers directories from marker objects or prefixes. Rename in both cases is not native to S3 and is implemented as object metadata/object copy and delete style behavior.

Writable flow follows the standard Hadoop pattern: `write(DataOutput)` emits a stable binary representation, and `readFields(DataInput)` mutates an existing instance from that representation. Primitive wrappers write primitive values directly. `ObjectWritable` writes class metadata before polymorphic payloads. `AbstractMapWritable` writes per-instance class-ID tables so nested heterogeneous maps can deserialize their contents. `CompressedWritable` defers decompression until `ensureInflated`.

MapFile flow is sorted and index-backed. Writers append key/value pairs in nondecreasing key order, sampling keys into an index at the configured interval while storing all entries in a SequenceFile data file. Readers load the index, seek near the target key, then scan data records to return exact or closest matches. BloomMapFile adds a pre-check path that skips expensive MapFile lookup when the Bloom filter says a key is definitely absent.

## State and Persistence Behavior

This JDiff file persists a public API snapshot for compatibility comparison. Hadoop runtime persistence is described by the APIs, not implemented here.

`Path`, `FsPermission`, `FsServerDefaults`, `FsStatus`, primitive Writables, `BytesWritable`, `ArrayWritable`, `EnumSetWritable`, `GenericWritable`, `MapWritable`, `ObjectWritable`, `MD5Hash`, `CompressedWritable`, MapFile, ArrayFile, and BloomMapFile all have explicit or implied serialized forms. Field order, class names, comparator identity, length/capacity interpretation, class-ID mapping, compression behavior, and permission bit encoding are compatibility-sensitive.

`RawLocalFileSystem` and `LocalFileSystem` persist changes to the host filesystem: files, directories, permissions, timestamps, ownership, local staging files, and checksum side files. Behavior depends on host OS semantics and available shell/native commands.

`FTPFileSystem` persists state on a remote FTP server; metadata fidelity, rename behavior, append support, and failure atomicity are constrained by FTP server capabilities.

`KosmosFileSystem` persists data in a KFS cluster and depends on external KFS configuration, client jars, and native JNI libraries. It also exposes explicit file lock/release operations and block-location queries.

`S3FileSystem` persists a Hadoop-specific block/inode layout in S3. File data is split into block objects, while directory and file metadata are stored as inode records keyed by URL-encoded paths. `MigrationTool` persists metadata rewrites for layout changes.

`NativeS3FileSystem` persists files as normal S3 objects and directories as inferred prefixes or marker objects. Directory existence and masking rules are part of the persistent namespace contract.

`MapFile` and derivatives persist a directory containing `data` and `index` files; `BloomMapFile` adds a Bloom metadata file. The index is read entirely into memory, so persisted index interval and key size influence runtime memory footprint.

`DefaultStringifier` persists serialized objects into `Configuration` string values. Loading depends on the same serialization framework and compatible classes being available later.

`Trash` persists recoverable deletes as moved files under trash directories and manages checkpoint directories during checkpoint/expunge cycles.

## Dependencies and Integration Points

The APIs depend heavily on Java platform types: `File`, `InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `URI`, `IOException`, `RuntimeException`, `Error`, `Closeable`, `Socket`, arrays, collections, enums, and reflection `Class`.

Key Hadoop integration points include:

- `org.apache.hadoop.conf.Configuration`, `Configured`, and `Configurable` for filesystem initialization, umask settings, stringifier storage, and Writable configuration propagation.
- `org.apache.hadoop.fs.FileSystem`, `ChecksumFileSystem`, `FileStatus`, `BlockLocation`, `FileChecksum`, `Path`, `FsStatus`, `FsServerDefaults`, `FSDataInputStream`, and `FSDataOutputStream`.
- `org.apache.hadoop.fs.permission.FsAction` and `FsPermission` for permission-bearing create/mkdir/status behavior.
- `org.apache.hadoop.util.Progressable`, `Tool`, and `org.apache.hadoop.util.bloom.Filter`.
- `org.apache.hadoop.io.Writable`, `WritableComparable`, `WritableComparator`, `SequenceFile`, `Stringifier`, and Hadoop serialization classes.
- Apache Commons Logging for filesystem and utility diagnostics.
- External service/client dependencies: FTP servers, KFS client jar/native library/JNI, Amazon S3 stores, S3 block metadata stores, and native S3 object stores.

Package-level documentation in the KFS and S3 sections is operationally important because it describes required configuration keys, filesystem implementation registration, native library path setup, S3 block layout, and native S3 directory-marker interop rules.

## Risks and Edge Cases

- The chunk starts inside `FileUtil` and ends inside `SequenceFile`; adjacent chunks are required for complete reports of those two classes.
- JDiff metadata omits method bodies. Exact validation, exception ordering, atomicity, retry behavior, checksum handling, protocol commands, and serialization byte layouts require implementation-source review.
- `FilterFileSystem` exposes its wrapped `fs` as a public field. Callers can bypass wrapper invariants or mutate the delegate unexpectedly.
- `deleteOnExit` depends on `FileSystem.close()` or JVM shutdown. Long-lived processes and cached filesystems can delay or skip deletion.
- `FSDataInputStream` assumes the wrapped stream supports `Seekable` and `PositionedReadable`; wrappers around plain streams can fail at runtime.
- `readFully` and positioned reads must handle short reads, EOF, negative offsets, and concurrent stateful seeks correctly.
- `sync`, `hflush`, and `hsync` have durability semantics that vary by filesystem. Implementations that silently weaken them can cause data-loss surprises.
- `Path` URI parsing and absolute-path rules are compatibility-sensitive, especially for relative paths, authorities, suffixes, and platform-specific path syntax.
- `RawLocalFileSystem` behavior varies across Unix and Windows for permissions, ownership, rename semantics, hard links, symlinks, and shell commands.
- `FileUtil.unZip` and `unTar` are archive extraction surfaces. Implementation review should check path traversal, overwrite behavior, permissions, and error cleanup.
- FTP operations have weak metadata and atomicity semantics. Append may be unsupported or fragile; rename/list/status behavior can vary by server.
- KFS integration depends on old external jars and native libraries. Missing or mismatched JNI libraries can fail at runtime after Hadoop is otherwise configured correctly.
- S3 permissions are documented as ignored for some operations. Callers expecting POSIX-style permission persistence will get misleading results.
- S3 rename is not native. Delete-plus-put or copy-plus-delete behavior can expose partial failure, eventual consistency, and non-atomic directory moves.
- Native S3 directory inference can conflict with real objects. The file-masks-directory rule must be tested because it affects listing/status correctness.
- `FsPermission` has short, symbolic, sticky-bit, and umask representations. Losing sticky bits or mishandling deprecated/current umask keys can alter security behavior.
- `AbstractMapWritable` supports at most 127 distinct classes per instance because class IDs occupy positive bytes. Heterogeneous nested maps can hit this limit.
- Exposing backing arrays in `BytesWritable.getBytes()` and deprecated `get()` lets callers read stale capacity bytes unless they respect `getLength()`.
- `CompressedWritable` subclasses must call `ensureInflated` before field access; otherwise they can observe uninitialized or stale decompressed state.
- `DefaultStringifier` stores class-dependent serialized bytes as strings. Configuration values can become unreadable after class renames or serialization changes.
- `EnumSetWritable` must preserve element type for null or empty enum sets; otherwise deserialization cannot reconstruct type.
- `GenericWritable` trusts subclass `getTypes()` ordering/contents. Changing that whitelist can break persisted polymorphic data.
- `ObjectWritable.loadClass` depends on `Configuration` class loading and can expose compatibility or security problems when reading untrusted class names.
- `MapFile.Writer.append` requires sorted keys. Out-of-order appends can corrupt lookup behavior even if the underlying SequenceFile write succeeds.
- `MapFile.Reader` loads the index entirely into memory. Large keys or small index intervals can cause high memory use.
- Bloom filters can produce false positives. `BloomMapFile.Reader.get` must still verify through the underlying MapFile; callers must not treat `probablyHasKey` true as existence.
- `MD5Hash.hashCode` uses only the first four bytes by design. It is efficient but collision-prone relative to full digest comparison.

## Test Signals

Useful validation for this chunk should include:

- API compatibility checks for every public/protected class, interface, field, constructor, method, parameter, exception, visibility flag, synchronization flag, and deprecation marker in lines 5865-12049.
- `FileUtil` tests for local/remote copy variants, delete-source behavior, merge behavior from the prior chunk boundary, shell path conversion, recursive `chmod`, symlink/hardlink creation, link-count retrieval, temp-file creation, replace semantics, and zip/tar extraction safety.
- `FilterFileSystem` delegation tests that verify every forwarded operation calls the wrapped filesystem with qualified/checked paths and propagates return values/exceptions.
- `FSDataInputStream` tests for `seek/getPos`, positioned reads, `readFully` short-read loops, EOF handling, and `seekToNewSource`.
- `FSDataOutputStream` tests for position tracking, close propagation, wrapped stream access, and `sync`/`hflush`/`hsync` behavior.
- Writable round-trip tests for `FsServerDefaults`, `FsStatus`, `FsPermission`, primitive Writables, `BytesWritable`, `ArrayWritable`, `EnumSetWritable`, `GenericWritable`, `MapWritable`, `ObjectWritable`, `MD5Hash`, and `CompressedWritable`.
- `Path` tests for all constructors, URI conversion, filesystem resolution, name/parent/suffix/depth behavior, equality/hash/compareTo, relative path qualification, and invalid path exceptions.
- `RawLocalFileSystem` and `LocalFileSystem` tests for create/open/append/delete/rename/list/mkdir/status, working directory, local output staging, checksum failure reporting, permission/owner setters, and OS-specific edge cases.
- `Trash` tests for enabled/disabled trash, move-to-trash, checkpoint, expunge, emptier creation, and CLI argument handling.
- FTP integration tests with a controlled server for initialize, open/create/delete/list/status/mkdirs/rename, working directory, append behavior, and connection failure handling.
- KFS compatibility tests or mocks for configuration parsing, URI handling, block locations, lock/release, local copy staging, replication, and missing native-library failure modes.
- S3 block filesystem tests for inode/block layout, migration metadata rewrites, create/open/seek/list/status/delete/rename, unsupported append, ignored permissions, and version mismatch errors.
- Native S3 tests for object-native create/open/delete/list/status/rename, directory marker creation, slash-marker interop, prefix-inferred directories, file-masks-directory behavior, and pagination/list call count expectations.
- `FsPermission` tests for short and symbolic parsing, sticky bit, umask keys including deprecated key, default permission, `valueOf`, equality/hash, and serialization.
- `AbstractMapWritable` tests for class registration, class-ID lookup, copy behavior, nested maps, 127-class limit, configuration propagation, and unknown class IDs.
- `BytesWritable` tests for logical length versus capacity, resizing, backing-array mutation, serialization length, comparator ordering, and string rendering.
- `DefaultStringifier` tests for store/load and storeArray/loadArray through `Configuration`, including close behavior and class compatibility failures.
- `GenericWritable` and `ObjectWritable` tests for allowed type dispatch, primitive/string/array handling, class loading through configuration, null instances, and invalid classes.
- `IOUtils` tests for copy buffer sizes, close/no-close behavior, exact `readFully`, `skipFully`, ignored cleanup exceptions, and socket close.
- `ArrayFile`, `MapFile`, and `BloomMapFile` tests for sorted append enforcement, index interval configuration, reader seek/get/getClosest/midKey/finalKey, repair via `fix`, Bloom false-positive-safe lookup, Bloom metadata persistence, and index memory behavior.
- `MD5Hash` tests for construction from bytes/hex, digest from byte arrays/streams/strings/UTF8, half/quarter digest, comparator ordering, hash collisions versus equality, and invalid hex parsing.
