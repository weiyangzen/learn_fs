# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop-core_0.21.0.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007248`: lines 1-5864, `Docs/researches/chunks/subset-b-007248_research.md`
- `subset-b-007249`: lines 5865-12049, `Docs/researches/chunks/subset-b-007249_research.md`
- `subset-b-007250`: lines 12050-18346, `Docs/researches/chunks/subset-b-007250_research.md`
- `subset-b-007251`: lines 18347-24705, `Docs/researches/chunks/subset-b-007251_research.md`
- `subset-b-007252`: lines 24706-25944, `Docs/researches/chunks/subset-b-007252_research.md`

## Chunk Research

### subset-b-007248: lines 1-5864

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop-core_0.21.0.xml lines 1-5864

## Purpose and scope

This chunk is the opening portion of the generated JDiff API snapshot for `hadoop-core 0.21.0`. The file is XML produced by the JDiff Javadoc doclet, using `api.xsd`, and records public/protected Java API surface, type hierarchy, signatures, visibility, deprecation text, exceptions, fields, and Javadoc bodies. It is not executable Hadoop code; its purpose is API compatibility research and release comparison for Hadoop Common/Core.

The chunk covers the API header and these packages/classes:

- `org.apache.hadoop`: `HadoopIllegalArgumentException`.
- `org.apache.hadoop.classification`: audience and stability annotation marker types.
- `org.apache.hadoop.conf`: `Configurable`, `Configuration`, `Configuration.IntegerRanges`, `Configured`, and `ConfServlet.BadFormatException`.
- `org.apache.hadoop.fs`: starts at `AbstractFileSystem` and runs through `FileSystem`, `FileSystem.Statistics`, and the beginning of `FileUtil.copyMerge`. The chunk ends inside the `FileUtil.copyMerge` documentation block, so later `FileUtil` API is unresolved in this chunk.

## Important APIs and types

### Common and classification

`HadoopIllegalArgumentException` is a public Hadoop-specific subclass of `IllegalArgumentException`, used to distinguish invalid argument failures thrown by Hadoop implementation from JDK-originated `IllegalArgumentException`.

`InterfaceAudience` and `InterfaceStability` define annotation classes that document intended consumers and compatibility expectations. Audience values include `Public`, `LimitedPrivate`, and `Private`; stability values include `Stable`, `Evolving`, and `Unstable`. These markers are important for API consumers and for tooling such as the ExcludePrivateAnnotations JDiff doclet that generated this file.

### Configuration APIs

`Configurable` is the small contract for types that accept and expose a `Configuration` through `setConf(Configuration)` and `getConf()`. `Configured` is the base implementation holding a `Configuration`.

`Configuration` is a central mutable property container and implements `Iterable` plus Hadoop `Writable`. The API exposes:

- Construction with defaults enabled, defaults disabled, or cloned from another `Configuration`.
- Static deprecation-map management through synchronized `addDeprecation(...)`, plus synchronized `addDefaultResource(String)`.
- Resource loading from classpath names, URLs, `Path`, and `InputStream`.
- Lazy reloading via synchronized `reloadConfiguration()`, which clears resource-loaded values and final-parameter state while preserving explicitly set overlays.
- Typed getters/setters for strings, ints, longs, floats, booleans, enums, regex patterns, integer ranges, comma-delimited string collections, class names, class arrays, and instantiated implementation lists.
- Class loading and interface-constrained class validation through `getClassByName`, `getClass`, `getClasses`, `getInstances`, and `setClass`.
- Local path/file selection from configured directory lists, choosing a directory based on path hash and creating it if needed.
- Resource accessors returning `URL`, `InputStream`, or `Reader`.
- Serialization and diagnostics through `readFields`, `write`, `writeXml(OutputStream)`, synchronized `writeXml(Writer)`, static `dumpConfiguration(Configuration, Writer)`, `iterator()`, `size()`, `clear()`, `main(String[])`, and quiet-mode controls.

The `Configuration` class documentation defines the key control rules: resources are loaded in order; later resources override earlier ones unless a value was marked final; default resources are `core-default.xml` and `core-site.xml` unless disabled; values undergo variable expansion against other configuration keys and then Java system properties. Deprecated keys map to replacement keys for both read and write paths.

`Configuration.IntegerRanges` parses strings such as `2-3,5,7-` into positive integer ranges and exposes `isIncluded(int)` plus `toString()`.

### File-system abstraction layer

`AbstractFileSystem` is the lower-level protected API behind `FileContext`. It is abstract and validates URI scheme/authority/path ownership, tracks filesystem statistics, and declares filesystem operations using fully qualified `Path` values and already-applied permissions. Key contracts include `create`/`createInternal`, `mkdir`, `delete`, `open`, `setReplication`, `rename`/`renameInternal`, symlink methods, permission/owner/time mutation, checksum/status/block-location queries, filesystem status, listing, and checksum verification toggles. Many methods mirror `FileContext` but explicitly state that paths must belong to this filesystem and permissions are absolute after umask application.

`AvroFSInput` adapts Hadoop file inputs to Avro-style input semantics. It can be constructed from an `FSDataInputStream` plus length, or from `FileContext` and `Path`, and exposes `length`, byte-range `read`, `seek`, `tell`, and `close`.

`BlockLocation` is a writable metadata object for block hostnames, storage names, topology paths, offset, and length. It supports getters/setters, `write(DataOutput)`, `readFields(DataInput)`, and `toString()`.

`ChecksumException` is an `IOException` with a position accessor, used to report checksum failures at a specific file offset.

`ChecksumFileSystem` is a `FilterFileSystem` that layers client-side checksum files over a raw filesystem. It exposes checksum filename detection and sizing, raw filesystem access, checksum byte sizing, verified `open`, append/create wrappers, checksum-aware rename/delete/listing/copy/local-output behavior, and `reportChecksumFailure(...)`. Its documentation states that it creates one checksum file per raw file and generates/verifies checksums on the client side.

`ContentSummary` is a `Writable` for directory/file aggregate metadata: length, directory count, file count, namespace quota, space consumed, and space quota. It serializes with `write/readFields` and renders quota-aware or non-quota output via `getHeader(boolean)` and `toString(boolean)`.

`CreateFlag` is an enum representing file creation semantics: create, append, overwrite, and valid combinations. The docs describe `CREATE + APPEND` as create-if-missing or append-if-present, and `OVERWRITE` combined with either create or append as overwrite behavior.

`FileAlreadyExistsException` is an `IOException` used when a target exists and overwrite is not configured.

`FileChecksum` is an abstract `Writable` describing checksum algorithm name, byte length, and checksum bytes, with equality/hash based on algorithm and value.

### FileContext APIs

`FileContext` is a final application-facing filesystem context. Static factories create contexts from default configuration, local filesystem, explicit URI, explicit `Configuration`, or an `AbstractFileSystem`. The class tracks default filesystem, working directory, and umask, and resolves three path forms: fully qualified URI, slash-relative path against the default filesystem, and working-directory-relative path. Relative paths with a scheme are documented as illegal.

The main operations include:

- Path qualification with `makeQualified`.
- File creation with `EnumSet<CreateFlag>` and `Options.CreateOpts`.
- Directory creation with permissions and `createParent`.
- Delete, open, replication, rename, permission, owner, time, checksum, status, link-target, block-location, filesystem-status, symlink, listing, delete-on-exit, and path resolution methods.
- Access to `FileContext.Util`, which provides utility operations layered on the base operations.

The FileContext documentation makes a clear state split: FileContext keeps namespace context and umask, while individual filesystem instances supply server-side defaults such as home directory, initial working directory, replication, block size, buffer size, and bytes-per-checksum.

`FileContext.FSLinkResolver<T>` is a helper for operations that may cross symlinks and filesystems. Subclasses implement `next(AbstractFileSystem, Path)`, while `resolve(FileContext, Path)` repeatedly invokes it until symlinks are resolved.

`FileContext.Util` provides non-atomic library operations over `FileContext`: existence checks, content summaries, list-status overloads with filters and path arrays, glob-status overloads with the same Hadoop glob grammar as `FileSystem`, and copy operations with delete-source/overwrite flags. Its docs explicitly warn that these library functions are not atomic and may partially complete when other threads modify the same namespace.

### File status and classic FileSystem APIs

`FileStatus` is a `Writable` and `Comparable` carrying client-side metadata: length, file/directory/symlink classification, block size, replication, modification/access time, permission, owner, group, path, and optional symlink target. It serializes via `write/readFields`. `compareTo`, `equals`, and `hashCode` are path-based. The old `isDir()` API is deprecated in favor of `isFile()`, `isDirectory()`, and `isSymlink()`.

`FileSystem` is the classic abstract, configured filesystem base class and implements `Closeable`. Its static factory and cache surface includes `get(...)`, `newInstance(...)`, `newInstanceLocal(...)`, `getLocal(...)`, `getDefaultUri`, `setDefaultUri`, `closeAll`, and deprecated `getNamed`. The scheme-to-implementation lookup is through the `fs.<scheme>.class` configuration key, and `initialize(URI, Configuration)` receives the full URI.

`FileSystem` defines extensive data-path operations:

- Qualification and path validation: `makeQualified`, protected `checkPath`.
- Block and server defaults: `getFileBlockLocations`, `getServerDefaults`, `getDefaultBlockSize`, `getDefaultReplication`.
- Stream APIs: abstract `open(Path,int)`, many `create` overloads, abstract permission-aware `create`, protected `primitiveCreate`, and append overloads.
- Directory APIs: static permission-exact `mkdirs(FileSystem, Path, FsPermission)`, abstract `mkdirs(Path, FsPermission)`, protected `primitiveMkdir` variants, and default-permission `mkdirs(Path)`.
- Mutation APIs: `rename`, protected transition `rename(Path,Path,Options.Rename...)`, `delete`, `deleteOnExit`, `processDeleteOnExit`, `setReplication`, `setPermission`, `setOwner`, `setTimes`, and `setVerifyChecksum`.
- Query APIs: `exists`, `isDirectory`, `isFile`, deprecated `getLength`/`getBlockSize`/`getReplication`, `getContentSummary`, `listStatus` overloads, `globStatus` overloads, `getHomeDirectory`, working-directory APIs, `getFileStatus`, `getFileChecksum`, `getStatus`.
- Local transfer helpers: copy/move from local, copy/move to local, start/complete local output.
- Lifecycle and accounting: `close`, `getUsed`, static statistics accessors, `clearStatistics`, and `printStatistics`.

`FileSystem.Statistics` tracks bytes read and bytes written per URI scheme. It exposes increment, readback, reset, `toString`, and `getScheme`. `FileSystem` and `AbstractFileSystem` both share statistics concepts.

`FileUtil` begins in this chunk. Covered APIs include `stat2Paths`, `fullyDelete`, `fullyDeleteContents`, deprecated filesystem recursive `fullyDelete`, `copy` overloads between `FileSystem` instances, and the signature start of `copyMerge`. The `copyMerge` documentation is cut off by the chunk boundary.

## Control flow and behavior encoded by the API

The XML has no method bodies, but the documented contracts imply control flow:

- `Configuration` loads resources lazily and in order, applies final-parameter restrictions, maps deprecated keys to replacements, expands variables on read, and overlays explicit `set*` values over resource-loaded values. `reloadConfiguration()` resets loaded resource state so subsequent access re-reads resources.
- `FileContext` resolves incoming paths against its default filesystem and working directory before dispatching operations to `AbstractFileSystem`. It applies umask before calling lower-level operations documented as receiving absolute permissions.
- `AbstractFileSystem` operations assume fully qualified, ownership-checked paths; many methods mirror `FileContext` but are protected provider-facing hooks.
- `FileSystem` uses configuration-driven implementation lookup and cached or new instances depending on `get` versus `newInstance`. It delegates core operations to abstract provider methods while convenience overloads supply defaults, convert legacy signatures, or add transition support for `FileContext`.
- Symlink-aware `FileContext` operations can route through `FSLinkResolver`, repeatedly resolving unresolved links and potentially crossing filesystem boundaries.
- Utility copy/list/glob/delete operations are layered workflows, not atomic primitives. `FileContext.Util` and `FileUtil` both carry partial-completion risk in their docs.

## State and persistence behavior

Persistent or serialized state is visible through Hadoop `Writable` contracts on `Configuration`, `BlockLocation`, `ContentSummary`, `FileChecksum`, and `FileStatus`. These APIs must remain compatible with Hadoop serialization expectations because the JDiff file is a compatibility baseline.

Runtime state includes:

- `Configuration` resource lists, final-parameter markers, deprecation mappings, explicit key/value overlays, classloader, and quiet-mode setting.
- `FileContext` default filesystem, working directory, and umask.
- `FileSystem` cached instances, delete-on-exit paths, working directory for implementations that still expose it, static default URI configuration keys, and global per-scheme/class statistics.
- `ChecksumFileSystem` checksum policy/state over a raw filesystem, including bytes-per-checksum and checksum-file naming.
- Metadata values in `FileStatus`, `BlockLocation`, and `ContentSummary`, plus `FileSystem.Statistics` counters.

The XML itself is a generated persisted artifact. Its header captures generation time, doclet, classpath, sourcepath, API name, and JDiff version. That makes it sensitive to build environment, doclet filters, annotations, classpath contents, and line ordering.

## Dependencies and integration points

The generated header shows integration with `org.apache.hadoop.classification.tools.ExcludePrivateAnnotationsJDiffDoclet`, JDiff `1.0.9`, Ant/Ivy-era dependency resolution, Hadoop Common build classes, and `api.xsd`.

The API surface integrates with:

- Java core types: `URI`, `URL`, `IOException`, `FileNotFoundException`, `URISyntaxException`, `Closeable`, `Iterable`, `Comparable`, `ClassLoader`, `Pattern`, `EnumSet`, `DataInput`, `DataOutput`, `InputStream`, `Reader`, `Writer`, `OutputStream`, and Java annotation interfaces.
- Hadoop Common: `Path`, `FileStatus`, `FileSystem`, `AbstractFileSystem`, `FileContext`, `FsServerDefaults`, `FsStatus`, `Options`, `CreateFlag`, `PathFilter`, `FSDataInputStream`, `FSDataOutputStream`, `FsPermission`, `Progressable`, `Writable`, and Hadoop security exceptions such as `AccessControlException`.
- Avro: `AvroFSInput` adapts Hadoop file streams to Avro input patterns.
- Commons Logging: `FileContext.LOG` and `FileSystem.LOG` fields are part of the public/protected API snapshot.

## Risks and compatibility concerns

- Because this is a JDiff baseline, changing any documented signature, visibility, exception declaration, field, deprecation marker, or doclet filtering rule can appear as an API compatibility change even if implementation behavior is unchanged.
- The chunk includes numerous transition APIs between `FileSystem` and `FileContext`, including protected `primitiveCreate`, `primitiveMkdir`, and protected rename with options. These are explicitly temporary/transition-oriented in documentation, which increases compatibility risk for downstream subclasses.
- Filesystem semantics have implementation-dependent edge cases: rename atomicity, symlink support, checksum support, block locations, status capacity, default server settings, and permissions may differ by filesystem provider.
- `FileContext.Util` and `FileUtil` utility operations are documented as non-atomic and partially completing on concurrent namespace mutation; tests should not assume all-or-nothing behavior.
- Several methods are deprecated but still present: `FileStatus.isDir`, `FileSystem.getName`, `getNamed`, one-argument `delete`, old replication/block-size/length getters, and `getStatistics()` returning a map. Removing or changing them would break API compatibility for 0.21 consumers.
- `Configuration` has subtle compatibility risks around deprecated key forwarding, final parameters, variable expansion, resource ordering, and synchronized static mutation after resource loading. These are core behaviors for Hadoop deployments.
- The chunk ends mid-`FileUtil.copyMerge`; any whole-file analysis must merge this with the following chunk to avoid truncating `FileUtil` coverage.

## Test signals

Useful validation signals for this chunk are mostly API and behavior compatibility tests:

- JDiff or equivalent API-diff checks comparing this XML against regenerated output for the same source tree should be stable except for intentionally changed API/doc content.
- Unit tests for `Configuration` should cover resource ordering, `final` properties, deprecated key mapping, typed getter default behavior, variable expansion, reload semantics, XML/Writable serialization, class loading, and quiet mode.
- Filesystem contract tests should exercise both `FileSystem` and `FileContext` path qualification, working-directory behavior, umask application, create flags, mkdir parent semantics, rename overwrite behavior, delete recursion, symlink resolution, status/list/glob operations, checksum toggling, and exception mapping.
- Serialization tests should round-trip `BlockLocation`, `ContentSummary`, `FileStatus`, `FileChecksum` subclasses, and `Configuration` through `Writable` APIs.
- Utility tests should check partial-completion and overwrite/delete-source semantics for `FileContext.Util.copy`, `FileUtil.copy`, and recursive delete helpers, using both local and non-local/mock filesystem implementations.
- Statistics tests should verify per-scheme/class `FileSystem.Statistics` counters, reset behavior, global clear/print paths, and byte increments from stream operations.

## Cross-chunk notes

This chunk starts the file and is complete through most of the foundational configuration and filesystem API surface, but it stops inside the `FileUtil.copyMerge` method documentation. The merge lane should combine this with the next chunk before producing the final per-file report so the remaining `FileUtil` APIs and later packages are not omitted.

### subset-b-007249: lines 5865-12049

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

### subset-b-007250: lines 12050-18346

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop-core_0.21.0.xml lines 12050-18346

## Research scope

This chunk is generated JDiff XML for the Hadoop Core 0.21.0 public API, not implementation source. The range starts inside `org.apache.hadoop.io.SequenceFile` at its compression and writer factory methods, covers the rest of the `org.apache.hadoop.io` package in this slice, the full visible `org.apache.hadoop.io.compress` package, and most of `org.apache.hadoop.io.file.tfile` through the beginning of `Utils.upperBound`. Conclusions are based on class/interface declarations, inheritance, implemented interfaces, visibility, deprecation metadata, method signatures, declared exceptions, fields, and embedded Javadocs.

The chunk is line-bounded. It begins after the opening of `SequenceFile` and ends before the closing text for `org.apache.hadoop.io.file.tfile.Utils`, so whole-class conclusions for those two types require adjacent chunks.

## Purpose

The covered API surface defines Hadoop's legacy binary data containers, serialization primitives, compression abstraction layer, and TFile block container. `SequenceFile`, `SetFile`, `SortedMapWritable`, `Text`, `Writable`, `WritableComparable`, `WritableComparator`, `WritableFactories`, and `WritableUtils` are foundational serialization and comparison APIs for MapReduce-era data exchange. The compression package abstracts stream codecs, reusable compressor/decompressor instances, split-aware compressed input, and default/gzip/bzip2 codecs. The TFile package exposes a sorted or unsorted byte-key/value container with block compression, named metadata blocks, range scanners, and utility encodings.

## Important APIs and types

`SequenceFile` exposes compression configuration helpers, many `createWriter` overloads, and the `SYNC_INTERVAL` constant. The documented file format has a common header containing the `SEQ` magic/version, key/value class names, compression booleans, optional codec class, metadata, and sync marker. Data can be uncompressed, record-compressed, or block-compressed; block compression separately stores compressed key lengths, keys, value lengths, and values.

`SequenceFile.CompressionType` is the enum for uncompressed, record-compressed, and block-compressed behavior. `SequenceFile.Metadata` is a `Writable` wrapper around `Text` name/value attributes with `get`, `set`, `getMetadata`, serialization, equality, hash, and string conversion.

`SequenceFile.Reader` is a synchronized closeable reader over filesystem paths or `FSDataInputStream` ranges. It reports key/value class names and classes, compression flags, codec, metadata, current position, and sync markers. It supports object/Writable reads, raw key/value reads through `DataOutputBuffer` and `ValueBytes`, `seek(long)` to writer-returned positions, and `sync(long)` to advance to the next sync marker from arbitrary offsets.

`SequenceFile.Sorter` provides external sort and merge operations for SequenceFiles. Constructors accept key/value classes or a `RawComparator`; runtime knobs include merge factor, memory budget, and `Progressable`. It can sort input paths to output paths, return a `RawKeyValueIterator`, merge `SegmentDescriptor` lists or path arrays, clone file attributes into a new writer, and write iterator records to a writer. `RawKeyValueIterator` exposes current raw key/value, progress, advancement, and close. `SegmentDescriptor` represents merge segments with offset, length, path, sync behavior, input preservation, raw key/value iteration, and cleanup that may close and delete temporary input.

`SequenceFile.ValueBytes` abstracts raw value payloads and can write uncompressed bytes, write already-compressed bytes without compressing uncompressed values, and report stored size. `SequenceFile.Writer` is a closeable writer with filesystem constructors, metadata/progress variants, class/codec getters, sync point creation, synchronized append overloads for `Writable` and object serializers, raw append, and synchronized `getLength()` values that are safe for later `Reader.seek`.

`SetFile` is a `MapFile`-backed file set. Its reader can seek, read next keys, and return a matching key or null. Its writer appends strictly increasing keys and has constructors keyed by class or comparator plus `SequenceFile.CompressionType`; the old no-configuration constructor is deprecated.

`SortedMapWritable` extends `AbstractMapWritable` and implements `SortedMap` for `WritableComparable` keys and `Writable` values. It exposes standard sorted-map views and mutations plus `Writable` serialization. `Stringifier<T>` is a closeable object/string round-trip interface.

`Text` is Hadoop's mutable UTF-8 `WritableComparable` string type. It exposes raw backing bytes and byte length, byte-position character lookup, byte-level find, string/byte/text setters, append, clear, UTF-8 read/write, equality/hash, static encode/decode helpers, static string read/write, UTF-8 validation, byte-to-codepoint conversion, and UTF-8 length calculation. `Text.Comparator` and `UTF8.Comparator` are raw `WritableComparator` implementations for byte-level comparison.

`TwoDArrayWritable`, `VIntWritable`, `VLongWritable`, `VersionedWritable`, and `VersionMismatchException` are small serialization helpers. `TwoDArrayWritable` serializes typed two-dimensional `Writable` arrays. `VIntWritable` and `VLongWritable` wrap variable-length integer encodings with setters, getters, `readFields`, `write`, equality, hash, compare, and string conversion. `VersionedWritable` prefixes serialized state with a version byte and throws `VersionMismatchException` on incompatible reads.

`Writable` and `WritableComparable` define Hadoop's core `write(DataOutput)` and `readFields(DataInput)` contract, with `WritableComparable` adding `Comparable`. `WritableComparator` centralizes raw byte and object comparison for `WritableComparable` keys, comparator registration, key instantiation, byte hashing, primitive reads from byte arrays, and variable-length integer decoding. `WritableFactories` and `WritableFactory` provide pluggable no-argument construction for `Writable` implementations. `WritableUtils` contains compressed byte/string helpers, array helpers, clone-by-serialization, deprecated `cloneInto`, vint/vlong encoding and decoding, enum serialization, exact skip, `Writable[]` to bytes, and bounded `readStringSafely`.

`BlockCompressorStream` and `BlockDecompressorStream` adapt streaming compressor interfaces to length-prefixed block formats. The compressor stream writes uncompressed block length followed by one or more length-prefixed compressed chunks; the decompressor stream reads block framing and supports `resetState`.

`CompressionCodec`, `Compressor`, and `Decompressor` are the main compression contracts. Codecs create compression/decompression streams, report compressor/decompressor classes, create codec instances, and expose default file extensions. Compressors and decompressors follow the `Deflater`/`Inflater` model: set input and dictionaries, report input/dictionary/finish states, transform buffers, expose byte counters where applicable, reset, release native resources with `end`, and for compressors reinitialize from `Configuration`.

`CompressionInputStream` and `CompressionOutputStream` are base classes for compressed streams with reset-state hooks; input streams also expose seek-like operations and position/source switching where subclasses support them. `CompressorStream` and `DecompressorStream` hold protected codec state, buffers, EOF/closed flags, and handle write/read, finish, reset, close, skip, available, mark, and reset behavior around concrete compressor/decompressor implementations.

`DefaultCodec`, `GzipCodec`, and `BZip2Codec` are concrete codec APIs. `DefaultCodec` is configurable and supplies the default compressor/decompressor implementations. `GzipCodec` specializes default behavior and has protected nested `GzipInputStream`/`GzipOutputStream` bridges around inflater/deflater streams. `BZip2Codec` implements `SplittableCompressionCodec`, supports `.bz2`, split-aware input ranges, and documents that direct `Compressor`/`Decompressor` methods are not implemented and may throw `UnsupportedOperationException`.

`CodecPool` is a global compressor/decompressor pool. It returns reusable instances for a codec, optionally reinitializing compressors with a `Configuration`, and accepts instances back through `returnCompressor` and `returnDecompressor`.

`SplitCompressionInputStream`, `SplittableCompressionCodec`, and `SplittableCompressionCodec.READ_MODE` describe compressed input that can align arbitrary requested byte ranges to codec-specific split boundaries. The read mode distinguishes continuous reading from block-boundary-aware reading, which matters for parallel processing of compressed files.

`org.apache.hadoop.io.file.tfile` defines `MetaBlockAlreadyExists`, `MetaBlockDoesNotExist`, `RawComparable`, `TFile`, `TFile.Reader`, `TFile.Reader.Scanner`, `TFile.Reader.Scanner.Entry`, `TFile.Writer`, and `Utils`. `TFile` is a byte-key/value container with optional sorting, block compression, metadata blocks, and seek by key or file offset. It exposes comparator construction, supported compression names (`none`, `lzo`, `gz`), command-line dump entry point, compression/comparator constants, and extensive tuning documentation for chunk size, filesystem buffers, block size, memory footprint, and compression choice.

`TFile.Reader` opens an `FSDataInputStream` and file length, reports comparator metadata, sorted status, entry count, first/last keys, comparators, metadata streams, nearby record/key by offset, and scanners by whole file, byte range, key range, or record-number range. Deprecated scanner overloads point callers to `createScannerByKey`.

`TFile.Reader.Scanner` is a closeable cursor over a whole file or bounded range. It supports `seekTo`, `rewind`, `seekToEnd`, `lowerBound`, `upperBound`, `advance`, `atEnd`, `entry`, and `getRecordNum`. Each move invalidates the previously returned `Entry`.

`TFile.Reader.Scanner.Entry` provides access to the current key/value. It can copy keys/values into `BytesWritable` or caller buffers, stream keys and values, write directly to an `OutputStream`, compare the entry key to byte buffers or `RawComparable`, and report equality/hash based on the pointed key/value. Value reads are single-use for a cursor position unless the cursor moves; `isValueLengthKnown()` must be checked before `getValueLength()`.

`TFile.Writer` writes an `FSDataOutputStream` positioned at zero with minimum block size, compression name, comparator name, and `Configuration`. It appends byte-array key/value pairs, supports stream-based key and value append with exact or unknown lengths, writes metadata blocks with explicit or default compression, prevents new key/value insertion after metadata block creation, releases resources on close without closing the underlying stream, and documents that an append exception leaves the TFile inconsistent except for close.

`org.apache.hadoop.io.file.tfile.Utils` provides TFile-specific variable-length integer/string encoding and generic `lowerBound`/`upperBound` binary search helpers, with comparator and natural-order overloads. The chunk ends inside the final `upperBound` Javadoc.

## Control flow and behavior

SequenceFile write flow is factory-driven. Callers choose key/value classes, filesystem path or raw `FSDataOutputStream`, compression type, optional codec, progress callback, metadata, and sometimes buffer/replication/block sizes. The writer emits the common header and then appends records according to compression mode. `sync()` inserts seekable markers; `getLength()` returns positions that a reader can later seek to safely, although block compression may position reads at the first key in the current block rather than exactly at the last appended key.

SequenceFile read flow is cursor-based. `next(key)` can skip values, `next(key, val)` materializes both, `getCurrentValue` reads the value for the last key, and raw methods separate key and value consumption for sort/merge paths. `seek(long)` requires a writer-synchronized position; `sync(long)` is the API for arbitrary offsets. `syncSeen()` tells callers whether the previous `next` crossed a sync mark.

SequenceFile sorting is an external sort/merge workflow. Inputs are read into sorted segments subject to memory limits, segment descriptors feed merge queues, merge factor controls fan-in, and temp directories hold intermediate files. `deleteInput`/`preserveInput` flags govern cleanup side effects, so callers need to understand when source or intermediate files may be removed.

Writable serialization flow is caller-managed and in-place. `readFields` implementations must fully overwrite object state from the stream; `WritableComparator` can avoid object allocation by comparing serialized byte ranges directly. `WritableFactories` provides construction hooks for deserialization frameworks that need instances before invoking `readFields`.

Compression stream flow follows Java zlib-like push/pull semantics. Output streams receive uncompressed bytes, feed a `Compressor`, write compressed bytes to the underlying stream, and require `finish()`/`close()` to flush codec state. Input streams pull compressed bytes, feed a `Decompressor`, and return uncompressed bytes until EOF. `resetState()` is the standard hook for stream reuse or boundary transitions.

Codec pooling is explicit. Callers borrow compressors/decompressors from `CodecPool`, use them with codec-created streams, and must return them when done. Failure to return pooled objects can leak native resources or reduce reuse; returning dirty state requires `reset`/`reinit` behavior to be correct.

Split compression flow lets a codec adjust requested `(start, end)` byte ranges to safe compressed-block boundaries. Clients ask for a split stream and then inspect `getAdjustedStart()` and `getAdjustedEnd()` to determine the actual covered compressed range.

TFile write flow enforces ordering and phase constraints. For sorted files, keys must obey the selected comparator. `append` writes complete key/value pairs in one call; `prepareAppendKey` and `prepareAppendValue` expose staged streams that must be closed in order and must write exactly the advertised lengths when lengths are not `-1`. Adding a metadata block ends key/value insertion. Closing finalizes internal indexes and metadata but deliberately leaves the caller-owned `FSDataOutputStream` open.

TFile read flow is scanner-based. A reader creates scanners over file, byte, key, or record ranges. Scanners maintain a cursor and invalidate previous `Entry` handles after movement. Entries allow copying or streaming current key/value data, but values are not cached and can only be consumed once per cursor position through the value-copy or value-stream APIs.

## State and persistence behavior

The XML itself persists API metadata for compatibility comparison. Runtime persistence comes from the documented file formats and `Writable` contracts.

SequenceFiles persist key/value class names, compression metadata, codec class names, user metadata, sync markers, and serialized records. This makes class names, serializer behavior, compression selection, sync interval, and metadata serialization part of the compatibility surface. `SequenceFile.Metadata`, `SortedMapWritable`, `Text`, primitive writable wrappers, array writables, and other `Writable` types persist their state to `DataOutput`/`DataInput`.

`WritableComparator`, `WritableFactories`, and `CodecPool` maintain process-local registries or pools. These are not filesystem-persistent, but they affect deserialization, comparison, and native codec reuse for the lifetime of a JVM.

Compression streams keep transient buffers, closed/EOF flags, codec state, optional native resources, byte counters, and stream positions. `Compressor.end()` and `Decompressor.end()` release resources. `CompressionInputStream.seek`/`seekToNewSource` only make sense when the wrapped stream and codec implementation can honor them.

TFile persists data blocks, meta blocks, block indexes, comparator names, compression algorithm names, and chunked values. Configuration keys such as `tfile.io.chunk.size`, `tfile.fs.output.buffer.size`, and `tfile.fs.input.buffer.size` influence memory use and value-length observability but must still produce readable files under the documented format. TFile reader/scanner state is cursor-local and invalidates entries on movement or close.

`SetFile` and `SequenceFile.Sorter` can create, merge, delete, or preserve filesystem paths. Sorter cleanup and SetFile append ordering are observable filesystem side effects rather than mere in-memory behavior.

## Dependencies and integration points

The `org.apache.hadoop.io` APIs integrate with `org.apache.hadoop.fs.FileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `Path`, `Configuration`, `Progressable`, `Progress`, `RawComparator`, `DataInput`, `DataOutput`, `DataOutputBuffer`, Java collections, `Closeable`, `Comparable`, and Hadoop serializer APIs.

Compression APIs integrate with `Configuration`, Java `InputStream`/`OutputStream`, `java.util.zip`-style compressor semantics, optional native codec implementations, filesystem split processing, and file extensions used by input format detection.

TFile integrates with `FSDataInputStream`, `FSDataOutputStream`, `Configuration`, `BytesWritable`, `RawComparable`, `RawComparator`, `WritableComparator`, and Java collection binary-search patterns. Comparator names bridge language-independent byte comparison (`memcmp`) and Java class comparators (`jclass:<RawComparator class>`).

JDiff consumers depend on exact signatures, visibility, deprecation strings, exceptions, and fields in this XML. Even documentation-only API contracts such as single-use TFile values, SequenceFile seek requirements, and BZip2 unsupported compressor paths are important compatibility signals for downstream code and tests.

## Risks and edge cases

SequenceFile compatibility is sensitive to file headers, class names, serializer choice, codec availability, sync marker placement, and raw-read ordering. `Reader.seek` must only use positions returned by `Writer.getLength`; arbitrary offsets require `sync`, or readers can land inside records or compressed blocks.

SequenceFile sorting can delete inputs or temporary segments. Incorrect `deleteInput`, `preserveInput`, or cleanup handling can cause data loss or orphaned temporary files. Sort performance depends heavily on efficient key `readFields` implementations with low allocation.

`ValueBytes.writeCompressedBytes` does not compress uncompressed bytes. Callers that assume it always produces compressed output can create malformed or inefficient files.

Writable implementations must reset all mutable state in `readFields`; stale fields, mismatched vint/vlong encodings, missing factories, or incompatible comparator byte logic can break RPC, MapReduce shuffle, SequenceFile sorting, and persisted data reads.

`Text` APIs use byte offsets, not Java `char` indexes, for several operations. Invalid UTF-8, trailing-byte positions, raw backing arrays beyond `getLength()`, and oversized string reads are recurring boundary risks.

Compression APIs are resource-sensitive. Streams often need `finish()` before close, codecs may hold native state, pooled compressors must be returned, and `resetState`/`reset` must clear all prior input. BZip2 advertises split support but not direct compressor/decompressor object support in this version.

Splittable compression may adjust requested ranges. Input formats must use adjusted start/end values and handle block-boundary semantics; otherwise parallel readers can duplicate or skip data.

TFile has strict ordering and lifecycle constraints. Sorted writers require comparator-consistent key order, active key/value append streams must be closed before the next phase, value/key advertised lengths must be exact, adding metadata blocks forbids further data entries, and append exceptions leave only `close()` as a legitimate follow-up. Reader entries and scanner positions are invalidated by movement or close, and values are single-use at a cursor position.

TFile memory and performance tradeoffs are explicit: small blocks increase index memory and flush overhead, large blocks hurt random access, gzip costs more CPU than LZO, and concurrent scanners over one reader may serialize I/O because of `seek()+read()` use.

## Test signals

Useful validation for this chunk should include:

- JDiff/XML checks that class and interface boundaries, visibility, deprecation strings, declared exceptions, field names, and method signatures remain stable for the covered line range, while accounting for partial `SequenceFile` and `Utils` boundaries.
- SequenceFile tests for all compression types, metadata round trips, codec selection, raw and Writable read paths, `getLength`/`seek` interoperability, arbitrary-offset `sync`, `syncSeen`, raw value handling, and object serializer append paths.
- SequenceFile sorter tests for comparator ordering, memory/factor settings, progress callbacks, sorted output, merge fan-in, `RawKeyValueIterator` lifecycle, segment cleanup, and delete-input/preserve-input behavior.
- Writable tests for `Text` UTF-8 validation and byte-offset APIs, variable-length integer boundaries, `WritableComparator` raw primitive reads and byte comparison, `WritableFactories` construction, `SortedMapWritable` ordering/serialization, and clone-by-serialization correctness.
- Compression tests for compressor/decompressor state transitions, `finish`/`reset`/`end`, stream close behavior, block framing, partial reads/writes, codec file extensions, `CodecPool` borrow/return/reinit behavior, BZip2 unsupported compressor methods, and split input adjusted offsets.
- TFile tests for sorted and unsorted writes, key-size limits, block compression choices, metadata block creation and duplicate/missing exceptions, stream-based key/value append ordering, exact advertised lengths, append failure handling, close without closing the underlying `FSDataOutputStream`, scanner ranges by byte/key/record number, lower/upper bound behavior, single-use value reads, entry invalidation, comparator names, and utility vint/string/binary-search helpers.

### subset-b-007251: lines 18347-24705

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop-core_0.21.0.xml lines 18347-24705

## Scope and artifact type

This chunk is part of the Hadoop 0.21.0 `hadoop-core` JDiff XML API snapshot. It records public packages, classes, interfaces, constructors, fields, method signatures, throws clauses, deprecation metadata, and Javadoc text. It is not implementation source, so control-flow and persistence notes below are limited to behavior documented by the API contracts and package descriptions.

The chunk starts at the tail of `org.apache.hadoop.io.file.tfile.Utils`, covers `Utils.Version`, serialization packages, log-level tooling, metrics implementations and SPI, network socket/topology helpers, the deprecated Hadoop Record I/O runtime, its compiler, Ant task, generated parser support, record metadata types, and ends at the beginning of `org.apache.hadoop.security.SaslRpcServer.AuthMethod`.

## Purpose

The main themes in this API section are:

- Hadoop serialization integration points: generic `Serialization` implementations for Java `Serializable`, Hadoop `Writable`, and Avro reflect/specific classes.
- Runtime observability: the original `org.apache.hadoop.metrics` API, file and Ganglia sinks, plus SPI types for buffering, periodic callbacks, record emission, composite contexts, and null/no-emit contexts.
- Network integration helpers: DNS/IP-to-rack mapping, cached and script-backed topology resolution, and standard/SOCKS socket factories.
- Deprecated Hadoop Record I/O: a pre-Avro IDL, runtime readers/writers for binary/CSV/XML encodings, record buffers, comparators, compiler model types, an Ant task, JavaCC parser support, and runtime type metadata.
- Storage/version compatibility utility: `org.apache.hadoop.io.file.tfile.Utils.Version`, intended for TFile meta-block versioning.

## Important APIs, types, and functions

### TFile utility versioning

- `org.apache.hadoop.io.file.tfile.Utils.Version` is a public static final comparable value object for major/minor versions.
- It can be constructed from `DataInput` or from explicit `short major, short minor` values.
- `write(DataOutput)` serializes major then minor as big-endian shorts.
- `getMajor()`, `getMinor()`, `size()`, `toString()`, `compatibleWith(Version)`, `compareTo(Version)`, `equals(Object)`, and `hashCode()` define comparison and persistence contracts.
- Compatibility is documented as equal major version numbers; minor version changes are expected to be backward-compatible format evolution.

### `org.apache.hadoop.io.serializer`

- `JavaSerialization` implements `Serialization` for Java `Serializable` classes. It exposes `accept(Class)`, `getDeserializer(Class)`, and `getSerializer(Class)`.
- `JavaSerializationComparator<T>` extends `DeserializerComparator` and compares deserialized Java-serialized objects through their `Comparable` interface.
- `WritableSerialization` extends `Configured` and implements `Serialization`; it accepts Hadoop `Writable` classes and delegates persistence to `Writable.write(DataOutput)` and `Writable.readFields(DataInput)`.
- Package-level configuration is via the `io.serializations` property, a list of `Serialization` implementation class names.

### `org.apache.hadoop.io.serializer.avro`

- `AvroSerialization<T>` extends `Configured` and implements `Serialization`. It supplies generic serializer/deserializer creation and requires subclasses to implement `getSchema(T)`, `getWriter(Class)`, and `getReader(Class)`.
- `AVRO_SCHEMA_KEY` is the schema-related public constant exposed by the base class.
- `AvroSpecificSerialization` handles Avro `SpecificRecord` classes generated by Avro's specific compiler.
- `AvroReflectSerialization` handles reflect-based Avro classes. Acceptance is synchronized and based on either implementation of marker interface `AvroReflectSerializable` or package membership configured by `AVRO_REFLECT_PACKAGES` / `avro.reflect.pkgs`.
- Dependencies are Apache Avro `Schema`, `DatumReader`, `DatumWriter`, and Avro specific records.

### Runtime log-level tool

- `org.apache.hadoop.log.LogLevel` exposes a command-line `main(String[])` and `USAGES` constant.
- Its stated purpose is changing log levels at runtime.

### Metrics API and implementations

- The `org.apache.hadoop.metrics` package describes an abstract metrics API backed by configurable implementations selected through `ContextFactory` attributes, typically read from `hadoop-metrics.properties`.
- Metrics records have a context name, record name, optional tags, and metric values. `MetricsRecord.update()` buffers rows rather than emitting immediately.
- `org.apache.hadoop.metrics.file.FileContext` extends `AbstractMetricsContext` and writes records to a configured file in append mode or to stdout. Important members include `init`, `getFileName`, `startMonitoring`, `stopMonitoring`, `emitRecord`, `flush`, `FILE_NAME_PROPERTY`, and `PERIOD_PROPERTY`.
- `org.apache.hadoop.metrics.ganglia.GangliaContext` extends `AbstractMetricsContext` and emits records over UDP to configured Ganglia servers. Package docs list `servers`, `period`, `units`, `slope`, `tmax`, and `dmax` attributes.
- `org.apache.hadoop.metrics.spi.AbstractMetricsContext` is the core SPI base. It implements `MetricsContext`, owns the internal metric-data table and timer, initializes from `ContextFactory`, starts/stops monitoring, creates records, registers/unregisters `Updater` callbacks, exposes `getAllRecords()`, updates/removes rows, parses period attributes, and requires subclasses to implement `emitRecord`.
- `CompositeContext` fans metrics operations out to subcontexts and reports monitoring true only when all subcontexts monitor.
- `MetricsRecordImpl` implements `MetricsRecord`, holds a back-pointer to its `AbstractMetricsContext`, supports typed tag setters (`String`, `int`, `long`, `short`, `byte`), typed metric setters/incrementers (`int`, `long`, `short`, `byte`, `float`), and delegates `update()` / `remove()` to the context.
- `MetricValue` wraps a `Number` as either absolute or incremental using `ABSOLUTE` / `INCREMENT`.
- `NoEmitMetricsContext` stores records for retrieval but does not emit them, useful for polling systems such as a metrics servlet.
- `NullContext` ignores start, emit, update, and remove operations and is the no-configuration default.
- `NullContextWithUpdateThread` keeps periodic updater invocation without external emission, suitable for polling integrations such as JMX.
- `OutputRecord` provides read access to emitted tag names/values and metric names/values plus defensive copies.
- `Util.parse(String specs, int defaultPort)` parses comma/space-separated `host` or `host:port` strings into `InetSocketAddress` objects, defaulting null specs to localhost.

### Network package

- `DNSToSwitchMapping` resolves a list of hostnames/IPs to one-to-one network location paths such as `/switch/rack`; hostnames are not part of the returned path.
- `CachedDNSToSwitchMapping` wraps a raw `DNSToSwitchMapping` and caches resolved network locations for subsequent calls.
- `ScriptBasedMapping` is a final cached mapping that implements `Configurable` and uses the `net.topology.script.file.name` configuration to resolve topology.
- `SocksSocketFactory` extends `javax.net.SocketFactory`, implements `Configurable`, can be constructed with a `Proxy`, and provides all standard `createSocket` overloads plus equality/hash configuration behavior.
- `StandardSocketFactory` extends `SocketFactory` and provides standard socket creation overloads plus equality/hash behavior. The Javadoc text says SOCKS, but the type name and lack of `Configurable` distinguish it from `SocksSocketFactory`.

### Deprecated `org.apache.hadoop.record` runtime

All classes in this package section are marked deprecated in favor of Avro. They still expose the old Hadoop Record I/O runtime:

- `BinaryRecordInput` / `BinaryRecordOutput` implement `RecordInput` / `RecordOutput` for dense binary encoding. They can wrap `InputStream`/`DataInput` or `OutputStream`/`DataOutput`; the static `get(DataInput)` / `get(DataOutput)` methods return thread-local instances for supplied data streams.
- `CsvRecordInput` / `CsvRecordOutput` implement the CSV-like record encoding, including explicit delimiters for structs, vectors, maps, strings, and buffers.
- `XmlRecordInput` / `XmlRecordOutput` implement an XML-RPC-inspired encoding.
- `RecordInput` and `RecordOutput` define the primitive and composite read/write interfaces: byte, boolean, int, long, float, double, string, buffer, record boundaries, vector boundaries, and map boundaries.
- `Index` models iteration over vector/map entries through `done()` and `incr()`.
- `Record` is the abstract base for generated record types. It supports `serialize(RecordOutput, String)`, `deserialize(RecordInput, String)`, `compareTo(Object)`, archive-format string overloads, and Hadoop `Writable` integration via `write(DataOutput)` / `readFields(DataInput)`.
- `RecordComparator` is a raw comparator hook for generated records and can be registered with `define(Class, RecordComparator)`.
- `Buffer` is a mutable byte sequence with constructors from empty, byte array, or byte slice; it supports `set`, `copy`, `get`, `getCount`, `getCapacity`, `setCapacity`, `reset`, `truncate`, `append`, comparison, equality, string conversion with optional charset, and cloning.
- `Utils` provides primitive binary helper methods for float/double, zero-compressed variable-length int/long reads and writes, VInt sizing, and byte-array comparison.

The package documentation provides the main Record I/O behavior:

- The IDL/DDL supports primitive types (`boolean`, `byte`, `int`, `long`, `float`, `double`, `ustring`, `buffer`), records/classes, vectors, maps, includes, and modules.
- The compiler can generate C++ and Java record classes. C++ generation is per `.jr` file into `.cc` and `.hh`; Java generation is per record type into package directories derived from module names.
- Binary encoding serializes composite types as concatenated serialized members, vectors/maps with counts, integral values using zero-compressed variable-length forms, floats/doubles in IEEE 754 network byte order, strings as UTF-8 with compressed length, and buffers as raw bytes with compressed length.
- CSV encoding uses typed markers such as single quote for strings, `#` for buffers, and `s{`, `v{`, `m{` for composite values.
- XML encoding follows XML-RPC-style `<value>` wrappers with extended primitive tags and needs DDL context for complete type interpretation.

### Deprecated record compiler

- `org.apache.hadoop.record.compiler.CodeBuffer` wraps `StringBuffer` and manages indentation.
- `Consts` exposes compiler string constants such as `RIO_PREFIX`, runtime type-info variables/filters, record input/output names, and tag names.
- `JType` is the abstract base for compiler model types.
- Primitive/compiler type classes include `JBoolean`, `JByte`, `JInt`, `JLong`, `JFloat`, `JDouble`.
- Composite/compiler type classes include `JBuffer`, `JString`, `JVector`, `JMap`, `JRecord`, and `JField`.
- `JFile` represents a DDL file with filename, included files, and records; `genCode(language, destDir, options)` generates code for a lower-case language name and may throw `IOException`.
- Package docs identify `CppGenerator` and `JavaGenerator` as the parser entry points, though their class entries are outside this chunk.

### Ant integration

- `org.apache.hadoop.record.compiler.ant.RccTask` extends Ant `Task`.
- It accepts `language`, a single `file`, `failonerror`, destination directory, and one or more `FileSet`s.
- `execute()` invokes the Hadoop record compiler for the configured record definition files and throws `BuildException` on configured failures.

### Generated JavaCC parser support

All classes in `org.apache.hadoop.record.compiler.generated` are deprecated with the Record I/O compiler:

- `ParseException` carries parse error state: `currentToken`, expected token sequences, token images, line separator, plus constructors and `getMessage()`.
- `Rcc` implements `RccConstants` and is the parser/driver. It has constructors over `InputStream`, `InputStream` with encoding, `Reader`, and `RccTokenManager`; command methods `main`, `usage`, and `driver`; grammar productions `Input`, `Include`, `Module`, `ModuleName`, `RecordList`, `Record`, `Field`, `Type`, `Map`, and `Vector`; parser reinitialization methods; token access methods; parse exception generation; and tracing toggles.
- `RccConstants` defines token IDs for EOF, module/record/include keywords, primitive types, vector/map, braces/angle brackets, semicolon/comma/dot, string/identifier tokens, lexical states, and `tokenImage`.
- `RccTokenManager` tokenizes `SimpleCharStream`, supports debug streams, reinitialization, lexical-state switching, token filling, and exposes generated literal images and lexical-state metadata.
- `SimpleCharStream` is the generated character stream with reader/input-stream constructors, optional encodings, buffer expansion/fill, token begin/read/backup operations, line/column accessors, reinitialization overloads, image/suffix extraction, cleanup, and begin-line/column adjustment.
- `Token` records token kind, source location, image, next token, and preceding special tokens; `newToken(int)` is the factory extension point.
- `TokenMgrError` represents lexical failures and includes escape/message helpers.

### Deprecated `org.apache.hadoop.record.meta`

- `FieldTypeInfo` pairs field ID/name with `TypeID`, with equality/hash behavior.
- `TypeID` represents primitive type IDs and exposes shared constants for bool, buffer, byte, double, float, int, long, and string; `typeVal` stores the ID value.
- `TypeID.RIOType` defines byte constants for the supported IDL types, including primitive, map, struct, and vector.
- `MapTypeID`, `VectorTypeID`, and `StructTypeID` model compound type IDs and compare equality by contained type info.
- `RecordTypeInfo` extends `Record`, stores record name and field type metadata, can add fields, return field metadata, find one-level nested struct type info, serialize/deserialize type information through `RecordOutput`/`RecordInput`, and has a non-useful `compareTo` contract because it exists for de/serialization rather than ordering.
- `org.apache.hadoop.record.meta.Utils.skip(RecordInput, String, TypeID)` skips bytes from a record stream based on type metadata.

### Security boundary

The chunk ends immediately after starting `org.apache.hadoop.security.SaslRpcServer.AuthMethod` and listing its `values()` method signature. The enum values and remaining methods are outside this work item.

## Control flow

The JDiff XML does not include method bodies, but the public contracts establish these flows:

- Serialization selection flow: Hadoop reads `io.serializations`, asks each `Serialization.accept(Class)`, then obtains a `Serializer` or `Deserializer`. Java serialization delegates to Java object streams, Writable serialization delegates to `Writable.write/readFields`, and Avro serialization delegates to subclass-provided schema, reader, and writer factories.
- Avro reflect acceptance flow: `AvroReflectSerialization.accept(Class)` is synchronized and accepts classes either in configured reflect packages or implementing `AvroReflectSerializable`; subsequent serializer/deserializer creation uses Avro reflect readers/writers.
- Metrics update flow: application code obtains a context and record, mutates tags/metrics on `MetricsRecordImpl`, and calls `update()`. The record delegates to `AbstractMetricsContext.update`, which creates or updates an internal row keyed by record/tags. Periodic monitoring invokes registered `Updater`s just before emission, calls subclass `emitRecord` for each `OutputRecord`, then calls `flush()`.
- Metrics removal flow: `MetricsRecordImpl.remove()` delegates to context removal. The documented match removes rows with matching tag names and values, even if the stored row has additional tags.
- Metrics lifecycle flow: `startMonitoring()` starts or restarts periodic emission; `stopMonitoring()` stops emission without freeing buffered data; `close()` stops and returns the context to initial state.
- File metrics sink flow: `FileContext.startMonitoring()` opens the configured file in append mode or selects stdout; `emitRecord()` writes formatted data; `flush()` forces output to disk/stream; `stopMonitoring()` closes file resources.
- Ganglia metrics sink flow: `GangliaContext.init()` reads server and metric metadata attributes; `emitRecord()` sends UDP messages to parsed server endpoints.
- Network topology flow: clients call `DNSToSwitchMapping.resolve(List)`. `CachedDNSToSwitchMapping` returns cached locations for already-seen names and delegates misses to its raw mapping. `ScriptBasedMapping` resolves via the configured script.
- Socket factory flow: callers obtain sockets through standard `SocketFactory.createSocket` overloads. `SocksSocketFactory` routes creation through a configured or supplied SOCKS proxy; `StandardSocketFactory` creates ordinary sockets.
- Record I/O flow: generated `Record` classes call `startRecord`, write/read fields through primitive and composite operations, iterate vectors/maps with `Index`, then call end methods. `Record.write/readFields` bridges this model to Hadoop `Writable`.
- Record compiler flow: the generated `Rcc` parser reads tokens from `RccTokenManager` and `SimpleCharStream`, builds compiler model objects (`JFile`, `JRecord`, `JField`, `JType` variants), then `JFile.genCode` emits Java or C++ output. `RccTask` wraps this for Ant builds.

## State and persistence behavior

- `Utils.Version` persists exactly two shorts, major followed by minor; compatibility is major-version equality.
- Serialization implementations persist user objects through their underlying framework: Java object serialization, Hadoop Writable binary contracts, or Avro schema-driven encodings.
- Metrics contexts maintain an in-memory buffered table of records. Updates are not emitted immediately. `stopMonitoring()` preserves buffered data; `close()` frees it. `getAllRecords()` exposes current buffered records for polling integrations.
- Metrics sinks persist or transmit periodically. `FileContext` appends to a configured file or stdout and flushes explicitly. `GangliaContext` sends UDP metrics to configured endpoints, so delivery is external and best-effort by transport.
- `CachedDNSToSwitchMapping` stores name-to-network-location cache state around an underlying resolver.
- `SocksSocketFactory` and `ScriptBasedMapping` carry `Configuration` state; SOCKS also carries proxy state.
- Record I/O readers/writers persist data to streams in binary, CSV, or XML encodings. The binary format includes variable-length integer compression and explicit lengths for strings, buffers, vectors, and maps.
- `Buffer` owns mutable byte-array content, count, and capacity.
- Parser classes maintain parse/tokenizer state: current token, next token, token manager, lexical state, char buffers, stream positions, line/column counters, and special token chains.
- Record metadata types persist schema/type information through `RecordTypeInfo.serialize/deserialize` and type IDs.

## Dependencies and integration points

- Hadoop configuration: `Configured`, `Configurable`, `Configuration`, `ContextFactory`, and properties such as `io.serializations`, `hadoop-metrics.properties`, `<context>.class`, `<context>.period`, `<context>.fileName`, `<context>.servers`, and `net.topology.script.file.name`.
- Hadoop IO: `Writable`, `RawComparator`, `DataInput`, `DataOutput`, `RecordInput`, `RecordOutput`, and old `Record`/`Buffer` APIs.
- Apache Avro: `Schema`, `DatumReader`, `DatumWriter`, `SpecificRecord`, and reflect serialization.
- Metrics extension points: subclass `AbstractMetricsContext`, override `emitRecord` and optionally `flush`/`newRecord`, register `Updater`s, or compose contexts with `CompositeContext`.
- External systems: local files/stdout for `FileContext`, Ganglia over UDP for `GangliaContext`, JMX/servlets or other polling systems via `getAllRecords()`, topology scripts for rack awareness, and SOCKS proxies for networking.
- Build tooling: Ant `Task`, Ant `FileSet`, and JavaCC-generated parser/token classes.
- Migration point: most `org.apache.hadoop.record*` classes are deprecated and explicitly replaced by Avro, which is also present in this chunk as a supported serialization package.

## Risks and sharp edges

- This file is an API snapshot. Any body-level behavior not described in Javadocs must be verified against implementation source before modifying production behavior.
- The old Record I/O runtime and compiler are deprecated. New work should prefer Avro unless compatibility with legacy `.jr` definitions or generated classes is required.
- Multiple record encodings create compatibility risk. Binary, CSV, and XML have different escaping, typing, and length rules; cross-language tests must cover all configured formats.
- Metrics updates are buffered. Tests or callers that expect immediate sink output after `MetricsRecord.update()` will be wrong unless monitoring/flush behavior is driven.
- `stopMonitoring()` preserves buffered metrics while `close()` clears them; confusing these can leak stale metrics or lose expected polling state.
- `NullContext` silently drops updates and is the default when configuration is absent, which can hide metrics misconfiguration.
- `NoEmitMetricsContext` preserves records without emission; memory growth depends on record/tag cardinality.
- Ganglia emission relies on UDP and configured per-metric metadata; invalid host specs or metric attributes can cause missing or malformed external metrics.
- `CachedDNSToSwitchMapping` can return stale topology if the underlying mapping changes and the cache is not invalidated by implementation code outside this XML.
- `ScriptBasedMapping` depends on external script path/configuration and must preserve one-to-one output cardinality with input names.
- `SocksSocketFactory` equality/hash behavior matters if socket factories are cached or compared in configuration-sensitive code.
- Java serialization comparators deserialize before comparing, so they are slower and risk class/serialization failures compared with raw byte comparators.
- `RecordTypeInfo.compareTo` has contradictory wording: it says the class does not implement meaningful comparison and "always returns 0" for another `RecordTypeInfo`, while also mentioning an exception. Callers should not use it for ordering.
- Generated parser classes expose mutable public fields (`token`, `jj_nt`, `debugStream`, token locations/images), so parser/token objects are not robust encapsulated state.
- XML docs include escaped or malformed-looking snippets due to XML/Javadoc escaping in the JDiff artifact; verify actual source or generated docs before copying examples.

## Test signals

Useful tests or checks for code touched near these APIs:

- Version serialization round trip: construct `Utils.Version`, write to `DataOutput`, read from `DataInput`, assert major/minor, `size()`, `compareTo`, equality/hash, and `compatibleWith` on same/different majors.
- Serialization framework selection: configure `io.serializations` with Writable, Java, Avro reflect, and Avro specific implementations; assert `accept` behavior and object round trips for representative classes.
- Avro reflect configuration: verify package-list acceptance, marker-interface acceptance, rejection of unrelated classes, and thread-safe repeated `accept` calls.
- Metrics buffering: set tags/metrics, call `update`, assert `getAllRecords` state before and after `remove`, then verify `stopMonitoring` preserves records and `close` clears them.
- Metrics sinks: for `FileContext`, verify append-mode output, stdout fallback, period parsing, and flush behavior. For Ganglia, use a UDP test server to assert emitted packets and server spec parsing.
- Updater timing: register `Updater`s and assert callbacks run before periodic emission and are not called after unregister/stop.
- Composite metrics: configure multiple subcontexts and assert fan-out for start/stop/register/update/emit/flush and `isMonitoring` all-subcontext semantics.
- DNS topology: assert `resolve` preserves one-to-one list length/order, cache hits avoid raw resolver calls, and script-based mapping handles missing/malformed script output.
- Socket factories: exercise all `createSocket` overloads using local loopback tests, plus SOCKS proxy configuration and equality/hash stability.
- Record runtime: round-trip generated records through binary, CSV, and XML encodings, including edge cases for zero-compressed ints/longs, UTF-8 strings, escaped CSV bytes, XML-forbidden characters, buffers with null/newline/percent bytes, empty vectors/maps, and nested records.
- `Buffer`: test capacity changes, append/copy isolation, truncate/reset behavior, compare/equality/hash, clone independence, and charset conversion.
- Record compiler/parser: parse `.jr` files with includes, modules, primitive/composite fields, maps/vectors, comments, syntax errors, and encoding-specific input streams; verify generated Java/C++ files and Ant `RccTask` fail-on-error behavior.
- Metadata: serialize/deserialize `RecordTypeInfo`, compare `TypeID`/`MapTypeID`/`VectorTypeID`/`StructTypeID`, and test `meta.Utils.skip` on streams containing each supported type.

### subset-b-007252: lines 24706-25944

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop-core_0.21.0.xml lines 24706-25944

## Scope

This chunk is the tail of the Hadoop Core 0.21.0 JDiff public API snapshot. The range begins inside `org.apache.hadoop.security.SaslRpcServer.AuthMethod` and continues through the end of the XML file, covering security/SASL helper APIs, token exception and delegation-token metadata APIs, common utility contracts, command-line tool helpers, and the public Bloom filter classes. Because the source is generated API metadata rather than implementation source, this research records public contracts, signatures, inheritance, stated behavior, serialization surfaces, and compatibility risks inferred from those contracts.

## Purpose

The covered API surface provides:

- RPC authentication and SASL callback contracts for Hadoop IPC.
- Token invalidation/renewal metadata types used by security token managers.
- General utility exceptions and callbacks for disk checks, progress reporting, reflection, shell command execution, binary-prefix parsing, and generic Hadoop CLI tools.
- Probabilistic membership data structures in `org.apache.hadoop.util.bloom`, including standard, counting, dynamic, and retouched Bloom filters.

## Important APIs and Types

### `org.apache.hadoop.security`

- `SaslRpcServer.AuthMethod` is an enum-like public API for RPC authentication methods. This chunk includes `values()`, `valueOf(String)`, `getMechanismName()`, static `read(DataInput)`, instance `write(DataOutput)`, and public final fields `code`, `mechanismName`, and `authenticationMethod`. The read/write methods make the auth method part of Hadoop IPC's binary negotiation protocol.
- `SaslRpcServer.SaslDigestCallbackHandler` is a public static `CallbackHandler` for SASL DIGEST-MD5. Its constructor accepts a `SecretManager` and `org.apache.hadoop.ipc.Server.Connection`, and `handle(Callback[])` may throw `SecretManager.InvalidToken` or `UnsupportedCallbackException`.
- `SaslRpcServer.SaslGssCallbackHandler` is a public static `CallbackHandler` for SASL GSSAPI/Kerberos. Its no-arg constructor and `handle(Callback[])` expose the Kerberos SASL callback path, with `UnsupportedCallbackException` as the declared failure.
- `SaslRpcServer.SaslStatus` is an enum-like public status with `values()`, `valueOf(String)`, and a public final integer `state`. This is likely serialized or compared in SASL RPC handshake state exchange.
- `UserGroupInformation.AuthenticationMethod` is the public enum-like UGI authentication method surface exposed here through `values()` and `valueOf(String)`. It is referenced by `SaslRpcServer.AuthMethod.authenticationMethod`.

### `org.apache.hadoop.security.authorize`

- The package is present but empty in this chunk. Its presence still matters for API baseline tooling: it records that the package existed in the public API snapshot even though no public types are listed in this line range.

### `org.apache.hadoop.security.token`

- `SecretManager.InvalidToken` extends `IOException` and has a public `InvalidToken(String)` constructor. The doc states that the message explains why the token was invalid. It is part of the checked exception flow from token lookup/validation into SASL DIGEST callback handling.

### `org.apache.hadoop.security.token.delegation`

- `AbstractDelegationTokenSecretManager.DelegationTokenInformation` is a public static holder for a delegation token's renew date and password. The constructor accepts `(long renewDate, byte[] password)`, and `getRenewDate()` exposes the renewal timestamp. The password is not directly exposed in this chunk's public API.

### `org.apache.hadoop.util`

- `DiskChecker.DiskErrorException` and `DiskChecker.DiskOutOfSpaceException` both extend `IOException` and expose message constructors. They separate general disk errors from capacity exhaustion in callers that need distinct handling.
- `Progressable` is a public callback interface with `progress()`. The doc makes it a liveness signal: clients and applications call it during long operations so the Hadoop framework does not assume the operation has timed out.
- `ReflectionUtils` is a general public utility class. APIs in this chunk include `setConf(Object, Configuration)`, `newInstance(Class, Configuration)`, `setContentionTracing(boolean)`, `printThreadInfo(PrintWriter, String)`, `logThreadInfo(Log, String, long)`, `getClass(T)`, `copy(Configuration, T src, T dst)`, and `cloneWritableInto(Writable dst, Writable src)`. It integrates object construction/config injection, thread diagnostics, and `Writable` serialization-based cloning/copying.
- `Shell.ExitCodeException` extends `IOException`, adds a constructor `(int exitCode, String message)`, and exposes `getExitCode()`. It is the observable exception type for failed shell commands.
- `Shell.ShellCommandExecutor` extends `Shell` and provides constructors for command string arrays with optional working directory, environment map, and timeout. Public methods include `execute()`, `getExecString()`, protected `parseExecResult(BufferedReader)`, `getOutput()`, and `toString()`. It is intended for commands whose output is small and does not need custom parsing.
- `StringUtils.TraditionalBinaryPrefix` is an enum-like parser/model for binary units kilo through exa. It exposes `values()`, `valueOf(String)`, `valueOf(char)`, `string2long(String)`, and public final fields `value` and `symbol`. The parser trims input and accepts case-insensitive suffixes such as `k` or `g`, converting by powers of 1024.
- `Tool` extends `Configurable` and standardizes Hadoop command-line applications through `run(String[] args)`. The documentation defines the pattern: let `ToolRunner` process generic Hadoop options, then handle application-specific arguments in `run`.
- `ToolRunner` is a public utility with static `run(Configuration, Tool, String[])`, static `run(Tool, String[])`, and `printGenericCommandUsage(PrintStream)`. It parses generic Hadoop CLI options, mutates or supplies the tool `Configuration`, invokes `Tool.run`, and passes application arguments through.

### `org.apache.hadoop.util.bloom`

- `BloomFilter` extends `Filter`. It has a default constructor for `readFields`, a parameterized constructor `(vectorSize, nbHash, hashType)`, mutation and set-operation methods `add(Key)`, `and(Filter)`, `or(Filter)`, `xor(Filter)`, `not()`, query method `membershipTest(Key)`, `toString()`, `getVectorSize()`, and `Writable`-style `write(DataOutput)`/`readFields(DataInput)`. Its documented semantics are the standard Bloom filter tradeoff: no false negatives for inserted keys, possible false positives.
- `CountingBloomFilter` is final and extends `Filter`. It adds `delete(Key)` and `approximateCount(Key)` to the same broad Bloom filter operation set. The count API is approximate and documented as reliable only for small counts; inserting the same key more than 15 times can overflow all associated buckets, and deletes can underflow, increasing error or creating false negatives.
- `DynamicBloomFilter` extends `Filter` and adds a constructor `(vectorSize, nbHash, hashType, nr)` where `nr` is the maximum number of keys per row. It grows by adding Bloom filter rows when no active row has capacity. Membership succeeds when a key's hash positions are set in any row.
- `HashFunction` is final and maps a `Key` to several integer positions. Constructor parameters are `(maxValue, nbHash, hashType)`, `clear()` is explicitly a no-op, and `hash(Key)` returns an `int[]` of hash positions. It depends on `org.apache.hadoop.util.hash.Hash`.
- `RemoveScheme` defines public `short` constants for retouched Bloom filter bit clearing: `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`.
- `RetouchedBloomFilter` is final, extends `BloomFilter`, and implements `RemoveScheme`. It can record known false positives through overloads accepting one `Key`, a `Collection`, a `List`, or a `Key[]`, then `selectiveClearing(Key, short)` removes a false positive according to the selected scheme. It also exposes `write(DataOutput)` and `readFields(DataInput)`.
- `org.apache.hadoop.util.hash` appears as an empty package at the end of this chunk; `HashFunction` references its `Hash` type even though the package's public classes are outside this range or absent from the final tail.

## Control Flow and State Behavior

- SASL RPC negotiation uses `AuthMethod` as a compact state token: callers can map enum names through `valueOf`, expose the SASL mechanism name through `getMechanismName`, and serialize/deserialize the method through `write(DataOutput)` and `read(DataInput)`. `SaslStatus.state` provides a public integer status code for handshake progress or result signaling.
- SASL callback handling flows through Java's `CallbackHandler.handle(Callback[])` contract. The DIGEST-MD5 handler integrates token validation and connection context; invalid tokens are reported as checked `SecretManager.InvalidToken`. The GSSAPI handler reports unsupported callback shapes through `UnsupportedCallbackException`.
- Token-manager state is represented by `DelegationTokenInformation`: creation stores renew date plus password bytes, while the public accessor in this chunk exposes only the renew date. The actual password lifecycle is intentionally not visible through the listed API.
- `Progressable.progress()` is a callback from long-running user or framework code into the scheduler/framework liveness path. It has no return value, so state change is external to the interface and likely recorded by the caller or framework.
- `ReflectionUtils.newInstance` control flow is constructor invocation followed by optional `Configuration` injection through `setConf`; `copy` and `cloneWritableInto` use writable serialization into a buffer or target object, so the source object's `write` method and destination object's `readFields` method define the effective copy behavior.
- `ShellCommandExecutor.execute()` runs the configured command, captures output for small-result commands, throws `IOException` or `ExitCodeException` on failure, and lets `parseExecResult(BufferedReader)` consume stdout. The timeout constructor parameter marks commands as timed out and kills them after the configured duration.
- `ToolRunner.run` is the CLI control-flow adapter: parse generic Hadoop arguments, set the resulting configuration on the `Tool`, call `run(String[])`, and return its exit code to the application's `main`.
- Bloom filters are mutable in-memory structures. `add` hashes keys and mutates bit/counter/row state; `membershipTest` checks hashed positions; `and`, `or`, `xor`, and `not` mutate or derive filter bit state according to implementation; counting filters decrement on `delete`; dynamic filters append rows as thresholds are exceeded; retouched filters clear selected bits to suppress known false positives at the cost of possible false negatives.

## Persistence and Compatibility Notes

- This XML is a compatibility baseline. Public names, nested class names, signatures, visibility, inheritance, exceptions, fields, and deprecation status are durable facts for downstream source and binary compatibility analysis.
- `AuthMethod.read/write` serializes RPC authentication choices. Changing numeric `code` assignments, mechanism names, or read/write formats would break interoperability between clients and servers using this API baseline.
- `SaslStatus.state` is public and final, so numeric state values are part of the public contract even though enum constants are not shown in this chunk's XML excerpt.
- `DelegationTokenInformation` stores renewal time and password bytes; persistence of token state in actual managers must preserve the relationship between renew date, token password, and token validity windows.
- Bloom filter classes expose `write(DataOutput)` and `readFields(DataInput)`. Serialized compatibility depends on preserving vector size, hash count, hash type, bit vectors, counting vectors, dynamic rows, and retouched false-positive metadata layouts.
- `ReflectionUtils.copy` and `cloneWritableInto` depend on `Writable` binary formats. Any `Writable` implementation copied through these helpers must maintain stable `write/readFields` semantics.
- `ShellCommandExecutor` exposes the command array through `getExecString()` and formats it in `toString()`. Quoting behavior for arguments with spaces is documented and may be asserted by tests or logs.
- `StringUtils.TraditionalBinaryPrefix.string2long` is a public parser. Accepted suffixes, case-insensitivity, trimming, negative values, and overflow handling are observable compatibility points.

## Dependencies and Integration Points

- Security APIs depend on Java SASL callback interfaces, `java.io.DataInput/DataOutput`, `org.apache.hadoop.security.UserGroupInformation.AuthenticationMethod`, `org.apache.hadoop.security.token.SecretManager`, and `org.apache.hadoop.ipc.Server.Connection`.
- Token APIs integrate with Hadoop token secret managers and checked `IOException`-based failure handling.
- Utility APIs depend on `org.apache.hadoop.conf.Configuration`, `org.apache.hadoop.conf.Configurable`, `org.apache.hadoop.io.Writable`, Apache Commons Logging `Log`, `PrintWriter`, `PrintStream`, process execution, environment maps, and Java IO streams/readers.
- `Tool`/`ToolRunner` integrate with Hadoop generic command-line options, `Configured`-style application classes, and MapReduce-era application launch patterns.
- Bloom filter APIs depend on `Filter`, `Key`, `RemoveScheme`, `HashFunction`, and `org.apache.hadoop.util.hash.Hash`, plus `DataInput/DataOutput` serialization.
- Disk-check exceptions integrate with filesystem/storage health checks that must distinguish disk error causes.

## Risks and Edge Cases

- The requested line range begins after the opening metadata for `SaslRpcServer.AuthMethod`, so enum constants and class header details just before line 24706 must be reconciled with adjacent chunks when producing the final per-file report.
- SASL auth compatibility is fragile: mismatched `AuthMethod.code`, mechanism names, or `SaslStatus.state` values can break RPC authentication before higher-level protocol errors are available.
- `SaslDigestCallbackHandler.handle` can surface invalid tokens during authentication. Callers must avoid collapsing token invalidation into a generic unsupported-callback failure, because the remediation and audit signal are different.
- Public final fields such as `AuthMethod.code`, `AuthMethod.mechanismName`, `AuthMethod.authenticationMethod`, `SaslStatus.state`, and `TraditionalBinaryPrefix.value/symbol` make internal encoding choices observable.
- `DelegationTokenInformation` accepts raw `byte[]` password data. If implementation stores the array by reference, callers could mutate token password state after construction; implementation review should verify defensive copying where needed.
- `Progressable` is a liveness API with no enforcement in the interface. Long-running operations that fail to invoke it can still time out even if they are otherwise healthy.
- `ReflectionUtils.copy` destroys or overwrites the destination object through deserialization. Incompatible source/destination writable types, partial reads, or non-idempotent serialization can leave `dst` in a corrupt state.
- Thread diagnostics in `ReflectionUtils.printThreadInfo/logThreadInfo` can be expensive and may expose sensitive stack information in logs.
- `ShellCommandExecutor` is explicitly for small command output. Using it for large output risks memory pressure because output is stored as a string.
- Shell execution is platform-sensitive: command quoting, working directory, environment injection, timeout killing, exit code propagation, and parsing failures all vary by OS and process behavior.
- `TraditionalBinaryPrefix.string2long` can overflow for large numeric prefixes and high suffixes; tests should cover bounds and invalid suffixes.
- `ToolRunner` mutates the tool configuration before calling `run`; tools that cache configuration-derived state before `ToolRunner.run` may observe stale state.
- Standard Bloom filters can return false positives by design. Counting filters can overflow above the documented counter range and underflow after deletes. Retouched Bloom filters intentionally introduce false negatives when clearing bits.
- Bloom filter set operations require compatible filter sizes/hash settings. The API accepts generic `Filter`, so implementations need type and parameter checks to avoid invalid combinations.

## Test Signals

- SASL API tests should round-trip each `AuthMethod` through `write(DataOutput)` and `read(DataInput)`, verify `code` uniqueness, verify mechanism-name mapping, and check `authenticationMethod` mapping into UGI auth methods.
- Callback-handler tests should cover supported and unsupported callback arrays, invalid-token propagation for DIGEST-MD5, Kerberos/GSSAPI callback behavior, and connection-context effects.
- Token tests should validate `InvalidToken` message preservation and `DelegationTokenInformation.getRenewDate()` for boundary timestamps; implementation tests should also check password byte-array ownership if source is available.
- Disk utility tests should distinguish `DiskErrorException` from `DiskOutOfSpaceException` in catch paths.
- `Progressable` tests should verify that long-running framework operations invoke progress callbacks frequently enough to prevent timeout behavior.
- `ReflectionUtils` tests should cover configuration injection, default-constructor instantiation, class return typing, writable copy/clone round trips, IO failure propagation, and thread-info throttling through `logThreadInfo`.
- Shell tests should cover constructor variants, environment and working-directory propagation, timeout handling, nonzero exit code via `ExitCodeException.getExitCode()`, stdout capture, `parseExecResult` behavior, `getExecString()`, and `toString()` quoting for arguments with spaces.
- `TraditionalBinaryPrefix` tests should cover case-insensitive `valueOf(char)`, trimmed values, negative values, each supported suffix, no-suffix numeric strings, invalid suffixes, and overflow/underflow boundaries.
- `ToolRunner` tests should exercise generic option parsing, null or explicit configuration behavior, `Tool.setConf` effects, pass-through of application arguments, returned exit codes, thrown exceptions, and generic usage output.
- Bloom filter tests should verify constructor parameter validation, add/query behavior with no false negatives for standard filters, expected false-positive behavior statistically, bitwise operations on compatible filters, serialization round trips, `CountingBloomFilter.delete` and `approximateCount` including overflow/underflow boundaries, `DynamicBloomFilter` row growth at `nr`, `HashFunction.hash` bounds and determinism, `RemoveScheme` constants, and `RetouchedBloomFilter.selectiveClearing` tradeoffs for each scheme.
