# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.4.xml lines 12060-18114

## Scope And Purpose

This chunk is a JDiff API snapshot for Apache Hadoop Common 3.3.4. It is metadata rather than executable Java source: the XML records public/protected API signatures, inheritance, implemented interfaces, field visibility, exceptions, deprecation status, and Javadoc text. The range starts at the tail of `org.apache.hadoop.fs.FileSystem`, covers a large portion of `org.apache.hadoop.fs`, then enters `org.apache.hadoop.fs.audit`, `org.apache.hadoop.fs.ftp`, and the beginning of `org.apache.hadoop.fs.statistics`.

The source range is not a standalone XML document. It begins after many `FileSystem` members have already been listed and ends inside the `IOStatistics` interface after `meanStatistics` starts. The merge lane must combine this with adjacent chunks to reconstruct the full file and the full API surface.

The dominant purpose of this chunk is to describe Hadoop's filesystem abstraction layer: utility helpers, filesystem wrappers, stream contracts, path and handle types, local/FTP filesystem implementations, quotas, storage statistics, trash policy integration, stream capability probing, audit context propagation, multipart upload handles, and duration/statistics reporting APIs.

## API Surface In This Chunk

The range starts with final fields and class documentation for `FileSystem`. The tail includes API-sensitive constants such as `SHUTDOWN_HOOK_PRIORITY`, `TRASH_PREFIX`, `USER_HOME_PREFIX`, and protected `statistics`. The class documentation is important because it states that `FileSystem` is the generic filesystem API for local, HDFS, object-store, and third-party implementations, and warns developers to update forwarding/filtering subclasses such as `FilterFileSystem` and `ChecksumFileSystem` when adding public or protected methods.

`FileUtil` is a static helper collection for local file and Hadoop filesystem operations. It converts `FileStatus[]` to `Path[]`, recursively deletes local files/directories, handles symlink targets, copies between `FileSystem` instances and local files, prepares shell-safe paths, computes local disk usage, unzips/untars archives, creates symlinks, runs permission/ownership changes, wraps `File.list*()` null behavior as exceptions, creates temp files, replaces files, builds classpath jars, finds jars in directories, compares filesystems, and writes bytes/text to a `FileSystem` or `FileContext`. Its `fullyDelete(FileSystem, Path)` overload is deprecated in favor of `FileSystem.delete(Path, boolean)`.

`FilterFileSystem` is a forwarding wrapper around another `FileSystem`. It exposes `getRawFileSystem()`, forwards URI/path qualification, open/create/append/concat/rename/delete/list/status, checksum, permission, ACL, xattr, storage policy, snapshot, builder, and path capability APIs, and stores the wrapped `fs` plus optional `swapScheme`. This class is a central integration point for subclasses that decorate or adapt another filesystem implementation.

`FSBuilder<S, B>` defines the generic builder contract used by filesystem and file-context builders. It has typed `opt()` and `must()` overloads for optional and mandatory options, plus `build()`. The contract says optional unknown options may be ignored, while unsupported mandatory options should fail, normally through `IllegalArgumentException`.

`FSDataInputStream`, `FSDataOutputStream`, `FSInputStream`, `Seekable`, `PositionedReadable`, `Syncable`, `StreamCapabilities`, and `StreamCapabilitiesPolicy` define the stream layer. Input streams support seek, positioned reads, byte-buffer reads, readahead/drop-behind, unbuffering, path capabilities, and IO statistics when the nested stream exposes `IOStatisticsSource`. Output streams expose position, close, hflush/hsync, drop-behind, capability probing, IO statistics, and abort when the wrapped stream is `Abortable`. `PositionedReadable` explicitly requires thread-safe positional reads, but its Javadoc warns that not all implementations satisfy this requirement.

`FSDataOutputStreamBuilder` is the create/append builder for output streams. It captures permission, buffer size, replication, block size, recursive parent creation, progress callbacks, create/overwrite/append flags, checksum options, and generic `opt`/`must` options inherited from `FSBuilder`. Its documentation explicitly discourages `instanceof` checks for filesystem-specific behavior and recommends namespaced builder options instead.

`FsConstants`, `FsServerDefaults`, and `FsStatus` describe shared filesystem constants and serializable server/status defaults. `FsServerDefaults` is a `Writable` carrier for block size, bytes-per-checksum, packet size, replication, file buffer size, encryption flag, trash interval, checksum type, key provider URI, and default storage policy ID. `FsStatus` is a `Writable` view of capacity, used, and remaining bytes.

`FutureDataInputStreamBuilder` is the asynchronous open-builder API. Its `build()` returns `CompletableFuture<FSDataInputStream>` and may accept a `FileStatus` hint through `withFileStatus()`. Like output builders, it uses `opt` and `must` parameters for implementation-specific options.

`GlobalStorageStatistics` and `StorageStatistics` provide process-wide and per-instance statistics plumbing. `GlobalStorageStatistics` has synchronized `get`, `put`, `reset`, and `iterator` operations around named statistics providers. `StorageStatistics` is an abstract named statistics object with optional scheme association, long-statistic iteration, key lookup, tracking checks, and reset.

`GlobFilter`, `PathFilter`, `Path`, `InvalidPathException`, and `InvalidPathHandleException` cover path parsing/filtering. `Path` is serializable and comparable, can be built from parent/child pairs, strings, URIs, and components, and supports URI conversion, filesystem resolution, qualification, absolute/root/name/parent/suffix/depth checks, Windows absolute-path detection, merge/removal of scheme and authority, and deserialization validation against malicious object streams.

`LocalFileSystem` and `RawLocalFileSystem` adapt the abstract `FileSystem` contract to the host filesystem. `LocalFileSystem` extends `ChecksumFileSystem`, exposes the raw filesystem, maps paths to `java.io.File`, handles local copy operations, reports checksum failures, and supports symlink operations. `RawLocalFileSystem` implements local open/create/append/rename/truncate/delete/list/mkdir/status/working-directory operations directly, uses `chmod`/`chown` style behavior for permissions and ownership, supports path handles, symlinks, and path capability checks.

`LocatedFileStatus`, `PartialListing`, `QuotaUsage`, `StorageType`, `ReadOption`, `PathHandle`, `PartHandle`, `UploadHandle`, and `MultipartUploader` carry filesystem metadata and handles. `LocatedFileStatus` adds block locations to `FileStatus`. `PartialListing` behaves like a future-like partial directory listing that may throw on `get()`. `QuotaUsage` stores namespace, space, and storage-type quota/consumption values and produces shell-style formatted output. `StorageType` models media classes, movability, transient storage, and quota support. `MultipartUploader` is an async, closeable upload API with `startUpload`, `putPart`, `complete`, `abort`, and best-effort `abortUploadsUnderPath`.

`Trash` and `TrashPolicy` provide pluggable trash behavior. `Trash` delegates to configured policies and includes `moveToAppropriateTrash()` for symlinks and mount points, where deletion should move to the trash directory on the resolved target volume. `TrashPolicy` defines initialization, enablement, move/checkpoint/delete operations, current trash directory lookup, emptier creation, and factories controlled by `fs.trash.classname`. Older APIs that require a home directory are deprecated because encryption zones require path-specific trash resolution.

`UnsupportedFileSystemException`, `UnsupportedMultipartUploaderException`, `ParentNotDirectoryException`, `FSError`, and `FTPException` define error types around unsupported schemes, unsupported multipart uploaders, invalid parents, presumed native filesystem errors, and FTP runtime exception wrapping.

`XAttrCodec` and `XAttrSetFlag` expose extended-attribute value conversion and set validation. `XAttrCodec` decodes text, hex-prefixed `0x`/`0X`, base64-prefixed `0s`/`0S`, and quoted string representations into byte arrays, and encodes byte arrays back to shell/API-friendly strings. `XAttrSetFlag.validate()` checks xattr create/replace semantics against whether the xattr already exists.

`CommonAuditContext` is a final audit-context container shared across filesystem audit spans. It supports per-thread context entries, dynamically evaluated suppliers, reset/remove/get/contains operations, thread ID reporting, evaluated-entry maps, global key/value context, process ID, and entry-point recording through `noteEntryPoint()`. The Javadoc states that audit spans retain a reference to the current thread context even when spans move across threads.

`FTPFileSystem` is a `FileSystem` backed by Apache Commons Net. It exposes the `ftp` scheme, default port, initialization, open/create/delete/list/status/mkdir/rename/working-directory operations, and configuration constants for user, host, port, password, data connection mode, transfer mode, same-directory rename behavior, and timeout. Its create-stream Javadoc warns that the stream must be closed before using other APIs on the class or calls may block. `append()` is explicitly unsupported.

`DurationStatisticSummary` and the opening of `IOStatistics` start the `org.apache.hadoop.fs.statistics` section. `DurationStatisticSummary` is serializable, records key, success/failure selection, count, max, min, and mean, and can fetch success/failure summaries from an `IOStatistics` source. `IOStatistics` begins with maps for counters, gauges, minimums, maximums, and then continues beyond this chunk.

## Control Flow And State Behavior

Because this is JDiff XML, direct control flow is limited to API contracts. The runtime control flow implied by the documented APIs is:

1. Client code resolves `Path` objects through `FileSystem` or `FileContext`, then uses generic `FileSystem` operations instead of implementation-specific classes.
2. Wrapper filesystems such as `FilterFileSystem` forward calls to an underlying `FileSystem`; new base APIs must be audited so wrappers do not accidentally drop or incorrectly advertise behavior.
3. Stream creation is either immediate through `open/create/append` or declarative through builders. Builder options split into optional keys that can be ignored and mandatory keys that must be honored or rejected.
4. Input streams maintain mutable seek position, while positional reads are intended not to change that position. The API warns that thread safety is a contract but not universally achieved.
5. Output streams track position and may flush to readers through `hflush()` or to storage through `hsync()`. Abort support is capability-dependent and must be probed or handled through exceptions.
6. Trash operations resolve the appropriate filesystem/trash root, especially across symlinks, mount points, and HDFS encryption zones, then move paths, checkpoint trash, or expunge old checkpoints.
7. Multipart uploads follow a future-returning lifecycle: start an upload, upload one or more numbered parts, complete with a non-empty map of part handles to obtain a `PathHandle`, or abort the upload.
8. Audit context flows from per-thread maps and global entries into filesystem audit spans. Dynamic supplier values are evaluated when `getEvaluatedEntries()` is called, which may happen in a different thread from where the supplier was registered.
9. Statistics flow from implementations into `StorageStatistics`, `GlobalStorageStatistics`, `IOStatisticsSource`, and duration summaries for reporting and testing.

State and persistence behavior is mostly delegated to implementations. Persistent filesystem state is affected by create, append, delete, rename, truncate, mkdir, permission/owner/time changes, ACL/xattr operations, storage policy changes, snapshots, trash movement/checkpoint deletion, local raw-file operations, and FTP operations. In-memory state includes working directories, stream positions, builder options, per-stream/per-filesystem statistics, global statistics registry entries, audit context maps, and trash policy fields (`fs`, `trash`, `deletionInterval`).

## Dependencies And Integration Points

The XML describes APIs that integrate across Hadoop Common and external filesystems:

- Core Hadoop types: `Configuration`, `FileSystem`, `FileContext`, `Path`, `FileStatus`, `BlockLocation`, `FsPermission`, ACL/xattr/storage-policy types, `RemoteIterator`, `Progressable`, `DataChecksum.Type`, `Writable`, and Hadoop security exceptions.
- Java platform types: `URI`, `File`, `InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `ByteBuffer`, `CompletableFuture`, collections, `Serializable`, `Closeable`, and object deserialization validation.
- Local OS integration through shell path conversion, chmod/chown/symlink operations, Windows-specific permission and path behavior, and Java file APIs.
- Apache Commons Net for `FTPFileSystem`.
- Filesystem-spec integration through documented semantics for `FileSystem`, `Syncable`, stream capabilities, path capabilities, and IO statistics.
- Compatibility integration with downstream projects called out in `FileSystem` documentation, including Hive shims and HBase/HBoss references.

The most sensitive integration point is API evolution. The `FileSystem` class documentation explicitly instructs developers adding public/protected methods to review forwarding subclasses such as `FilterFileSystem`, checksum behavior in `ChecksumFileSystem`, and test interfaces such as `TestFilterFileSystem.MustNotImplement` and `TestHarFileSystem.MustNotImplement`. Capability probing through `hasPathCapability(Path, String)` also requires wrappers to avoid over-reporting support.

## Risks And Edge Cases

- This chunk starts and ends mid-structure; chunk-local XML parsing will fail and any class-level interpretation must be reconciled with adjacent chunks.
- `FileUtil.fullyDelete()` can return false after partial deletion, and `fullyDeleteContents()` follows symlinks to directories when deleting contents. Callers need to understand whether a symlink itself or its target contents are affected.
- Shell/permission helpers have platform-specific behavior. Windows symlink creation may fail with `SYMLINK_NO_PRIVILEGE`, and Windows permission semantics differ from Unix, especially execute permission on directories.
- Archive extraction helpers (`unZip`, `unTar`) are filesystem-writing utilities; callers need path traversal and overwrite behavior covered by implementation tests even though this XML only records signatures and Javadoc.
- `FilterFileSystem` can create compatibility bugs if a new `FileSystem` method is not forwarded, is forwarded with the wrong default, or incorrectly reports capabilities.
- Builder options intentionally allow unknown optional keys to be ignored. Misspelled mandatory options should fail, while misspelled optional options may silently have no effect.
- `PositionedReadable` promises thread-safe positioned reads but warns that not all filesystems meet it. Consumers such as HBase can be sensitive to this mismatch.
- `FSDataInputStream.getIOStatistics()` may return null when the nested stream is not an `IOStatisticsSource`, while `FSDataOutputStream.getIOStatistics()` documents an empty-statistics fallback. Callers should not treat the input and output contracts as identical.
- `Path.validateObject()` exists to defend deserialization; any custom serialized path handling should preserve this validation.
- Trash path selection must account for encryption zones, symlinks, and mount points. Deprecated home-directory-based trash APIs can place data in the wrong trash location for encrypted paths.
- `FTPFileSystem.create()` blocks later API use until the returned stream is closed; `append()` is unsupported. FTP rename also has a same-directory constraint constant, so behavior may differ from HDFS/local filesystems.
- Multipart upload cleanup is best effort. `abortUploadsUnderPath()` may be unsupported or miss uploads because of eventually consistent listings.
- Audit context suppliers may be evaluated in different threads, so supplier implementations must be thread-safe and should not assume caller-thread state.
- `XAttrCodec` accepts multiple textual encodings; invalid prefixes, quoting, and byte conversion errors need explicit tests to avoid shell/API compatibility regressions.

## Test Signals

Useful validation around this chunk includes:

- JDiff/API compatibility tests that compare this XML against neighboring Hadoop Common versions and flag public/protected signature changes in the listed classes.
- Unit tests for every `FileSystem` API addition to ensure `FilterFileSystem`, `ChecksumFileSystem`, HAR, and local/raw local filesystems either forward, implement, or deliberately reject the method.
- Local filesystem tests for recursive deletion, symlink deletion versus target deletion, Windows permission behavior, chmod/chown wrappers, temp-file creation, file replacement, and `PathHandle` support.
- Stream tests for seek/getPos, positioned reads that do not alter stream offset, `readFully()` EOF behavior, ByteBuffer reads, unbuffer policy, drop-behind/readahead capability probing, hflush/hsync semantics, abort support, and IO statistics fallback behavior.
- Builder tests for optional versus mandatory options, overwrite/create/append flag combinations, recursive parent creation, invalid parameter rejection, checksum options, and asynchronous open futures.
- Path tests for URI construction, Windows absolute paths, parent/child resolution, scheme/authority removal, path merging, equality/hash/compare behavior, root/depth calculations, and deserialization validation.
- Trash tests for disabled trash, already-in-trash paths, symlink and mount-point resolution, encryption-zone-specific trash directories, checkpoint creation/deletion, immediate expunge, and policy factory configuration via `fs.trash.classname`.
- Multipart uploader tests for start/put/complete/abort ordering, parallel part uploads, input stream closure after `putPart`, empty handle-map rejection, unsupported abort-under-path behavior, and `PathHandle`/`PartHandle`/`UploadHandle` serialization equality.
- Audit tests for thread-local context isolation, global entry visibility, `PROCESS_ID`, `noteEntryPoint()` idempotence, supplier evaluation timing, reset behavior, and cross-thread span propagation.
- FTP filesystem integration tests for open/create stream lifecycle, append unsupported behavior, working directory handling, recursive delete/mkdir/list/status, timeout/config key handling, and rename restrictions.
- Statistics tests for `GlobalStorageStatistics` synchronized registry behavior, reset/iterator semantics, `StorageStatistics` tracking, `DurationStatisticSummary` success/failure extraction, and `IOStatistics` map presence after the adjacent chunk completes the interface.
