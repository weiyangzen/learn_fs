# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.5.0.xml lines 18114-24626

## Scope

This chunk is part of the Hadoop Common 3.5.0 JDiff API snapshot. It is XML metadata for public and protected Java API surface, not executable implementation code. The range starts inside `org.apache.hadoop.fs.Path` and continues through multiple `org.apache.hadoop.fs.*` packages, ending in the opening constructor documentation for `org.apache.hadoop.fs.viewfs.ViewFileSystem`. The merge lane should treat `Path` and `ViewFileSystem` as cross-chunk continuations.

## Purpose

The chunk documents Hadoop filesystem API contracts around paths, positioned reads, quota reporting, local and FTP filesystem implementations, stream capability probing, trash policy abstraction, ACL/permission modeling, IO statistics, object-store metric names, and initial ViewFS mountpoint support. It is primarily a compatibility contract: downstream users and filesystem implementations rely on these declarations to know method signatures, checked exceptions, deprecation status, stable string formats, and behavioral notes.

## Important APIs And Types

`org.apache.hadoop.fs.Path` appears at the chunk boundary with `makeQualified(URI, Path)`, deprecated `makeQualified(FileSystem)`, `validateObject()`, and separator/current-directory constants. The documented contract is path qualification against a default URI and working directory, plus deserialization validation to reject malicious object streams without a URI.

`PathFilter`, `PathHandle`, `UploadHandle`, `Seekable`, and `PositionedReadable` define small but central extension points. `PathFilter.accept(Path)` is the path-list inclusion predicate. `PathHandle` and `UploadHandle` are opaque serializable references backed by `ByteBuffer`/byte arrays and equality semantics. `Seekable` exposes `seek`, `getPos`, and `seekToNewSource`. `PositionedReadable` defines thread-safe positional reads, `readFully` variants, vectored read defaults, and vector tuning hooks `minSeekForVectorReads()` and `maxReadSizeForVectorReads()`.

`QuotaUsage` models directory quota state: file/directory count, namespace quota, space consumed, space quota, per-`StorageType` quotas and consumption, output header/string formatting, equality, and protected setters/building hooks. `StorageType` enumerates storage media behavior with helpers for transient/RAM/movable/quota-support classification, parsing from strings/ints, same-disk tiering policy, and configuration-key lookup.

`RawLocalFileSystem` is the public local filesystem implementation over `java.io.File`. The chunk lists URI initialization, `pathToFile`, `open` by path and path handle, `append`, multiple `create`/`createNonRecursive` overloads, output-stream creation hooks, `concat`, `rename`, Windows empty-destination-directory handling, `truncate`, `delete`, `listStatus`, `exists`, directory creation helpers, working/home directory methods, local-output staging, status, ownership/permission/time mutation, path-handle creation, symlink methods, and `hasPathCapability`.

Read/write capability and durability APIs include `ReadOption`, nested `Options.Rename`, `SafeModeAction`, `StreamCapabilities`, `StreamCapabilitiesPolicy`, nested `StreamCapability`, and `Syncable`. Capability strings cover `hflush`, `hsync`, readahead, drop-behind, unbuffer, ByteBuffer reads, positioned ByteBuffer reads, IOStatistics, vectored IO, sliced vectored buffers, abortable streams, and thread-level IOStatistics context.

`Trash` and abstract `TrashPolicy` define delete-to-trash behavior. `Trash` is a configured facade with constructors from `Configuration` or `FileSystem`, static `moveToAppropriateTrash`, `moveToTrash`, checkpointing, expunge operations, immediate expunge, current trash directory lookup, and an emptier runnable. `TrashPolicy` supplies initialization, enablement, move/checkpoint/delete operations, emptier creation, current-trash-dir lookup, factory methods, and protected state fields `fs`, `trash`, and `deletionInterval`. Older home-directory initialization and factory overloads are deprecated.

`XAttrCodec` and `XAttrSetFlag` cover extended attribute shell/API value encoding and flag validation. `XAttrCodec.decodeValue` accepts hex (`0x`/`0X`), base64 (`0s`/`0S`), quoted text, or plain text; `encodeValue` returns text/hex/base64 string forms. `XAttrSetFlag.validate` checks create/replace flag compatibility against existing xattrs.

`org.apache.hadoop.fs.audit.CommonAuditContext` provides thread-local and global audit metadata. It supports static current context lookup, process/thread identifiers, entry-point recording, global context put/get/remove/iteration, per-thread put/remove/get/reset/contains, and delayed `Supplier<String>` values. The docs explicitly warn that long-lived suppliers must not retain large object graphs.

`org.apache.hadoop.fs.ftp.FTPFileSystem` is a `FileSystem` backed by Apache Commons Net. It exposes `ftp` scheme/default port, URI initialization, open/create/delete/list/status/mkdirs/rename/working-directory/home-directory APIs, and public FTP configuration constants for host, port, user, password, data connection mode, transfer mode, timeout, buffer/block size, and same-directory rename restrictions. `FTPException` wraps checked or unchecked causes as a runtime exception.

`org.apache.hadoop.fs.impl.AbstractFSBuilderImpl`, `FutureDataInputStreamBuilderImpl`, and `MultipartUploaderBuilderImpl` are implementation-support classes for filesystem builders. They track either a `Path` or a `PathHandle`, mutable option `Configuration`, mandatory and optional key sets, fluent typed `opt`/`must` setters, and rejection of unknown mandatory keys. The future input-stream builder returns `CompletableFuture<FSDataInputStream>` and carries buffer size and optional `FileStatus`; the multipart builder carries permission, buffer size, replication, block size, create/overwrite/append flags, and checksum options.

`org.apache.hadoop.fs.impl.prefetch.Kind`, `State`, and `org.apache.hadoop.fs.store.DestState` expose nested implementation enum values for block operations, buffer state, and data block destination state. Their package docs mark these areas as object-store/internal support with no stability guarantees.

`org.apache.hadoop.fs.permission` provides ACL and permission models. `AclEntry` is immutable with type/name/permission/scope accessors, stable string formatting, ACL spec parsing, single-entry parsing, and list-to-string conversion. `AclEntryScope` and `AclEntryType` are enums with stable string forms. `AclStatus` exposes owner, group, sticky bit, ACL entries, base permission, and effective permission calculations, including a compatibility overload for old NameNodes. `FsAction` supports permission implication and boolean algebra. `FsCreateModes` stores masked and unmasked creation modes. `FsPermission` implements `Writable`, `Serializable`, and `ObjectInputValidation`; it constructs permissions from actions, shorts, ints, strings, or copies, serializes/deserializes with `DataInput/DataOutput`, applies/get/sets umask, exposes default directory/file/cache-pool permissions, parses Unix symbolic strings, and validates deserialized objects. Deprecated ACL/encryption/EC bits are documented as moving to `FileStatus`.

`org.apache.hadoop.fs.statistics` is a public statistics surface. `IOStatistics` exposes counters, gauges, minimums, maximums, and mean statistics maps, plus unset sentinel values. `IOStatisticsAggregator` merges statistics. `IOStatisticsSetters` sets values. `IOStatisticsSnapshot` is synchronized for clear/snapshot/aggregate/map reads/setters, serializable, JSON-friendly, and exposes secure deserialization class lists. `IOStatisticsSupport` retrieves/snapshots stats and returns no-op duration trackers. `IOStatisticsLogging` stringifies and logs statistics robustly and lazily. `DurationStatisticSummary` extracts success/failure duration summaries. `MeanStatistic` tracks samples and sum with synchronized mutation/copy/mean/equality paths. `FileSystemStatisticNames`, `StoreStatisticNames`, and `StreamStatisticNames` declare stable metric keys for filesystem lifecycle, object-store operations, HTTP responses, multipart upload, stream reads/writes/seeks/vectored IO, prefetching, upload queues, and cache behavior.

`org.apache.hadoop.fs.viewfs.NotInMountpointException` and `RegexMountPointInterceptorType` begin the ViewFS section. The exception formats unsupported-operation errors when a path is not mounted through ViewFS. The interceptor enum maps names to configured regex mount-point interceptor types. The chunk ends immediately after the `ViewFileSystem` constructor opens, so the actual ViewFS method surface is outside this chunk.

## Control Flow And Behavioral Contracts

The XML does not contain method bodies, but the API docs describe expected flows. Path qualification borrows scheme/authority from a default URI and resolves relative paths against a working directory. Deserialization validation on `Path` and `FsPermission` is a defensive post-read step.

Positioned reads must not change the stream offset and are intended to be thread-safe, while the docs warn that some filesystems may violate this. `readVectored` defaults to synchronous per-range reading but allows subclasses to optimize. The release-aware overload delegates to the non-release overload by default and should be overridden by implementations that allocate pooled buffers.

Filesystem operations on `RawLocalFileSystem` and `FTPFileSystem` follow the `FileSystem` contract: initialize from URI/configuration, resolve path-to-storage, open/create/append/delete/list/status/rename/mkdir, then optionally mutate metadata. FTP create streams must be closed before other APIs are called or subsequent calls can block.

Builder control flow is option accumulation followed by `build()` in implementations. `opt` keys may be ignored; `must` keys require support and unknown mandatory keys must trigger `IllegalArgumentException`. Builders may be constructed around either a path or a path handle, but the base constructor rejects having both.

Trash flow resolves the correct trash location, moves deleted paths there, periodically checkpoints, and expunges old or all checkpoints. `moveToAppropriateTrash` specifically handles symlink and mount-point cases by resolving the path's volume before moving it.

Permission and ACL parsing converts stable shell-style strings into immutable `AclEntry`/`FsPermission` objects, and string outputs are explicitly compatibility-sensitive. Effective ACL permission calculation may need old NameNode compatibility data when the server does not provide modern effective-permission metadata.

IO statistics flow is source probing through `IOStatisticsSource`, retrieval of a possibly dynamic or immutable `IOStatistics`, optional snapshotting/aggregation, and logging or assertion. The package doc requires fast, nonblocking retrieval, stable key sets, post-close availability, and per-source uniqueness.

## State And Persistence

Most objects in this chunk are value or facade APIs, but several persist or expose state:

- `PathHandle` and `UploadHandle` are serialized opaque byte references and must preserve equality identity semantics.
- `QuotaUsage` persists quota and consumption counters, including per-storage-type arrays/maps.
- `RawLocalFileSystem`, `FTPFileSystem`, and `TrashPolicy` hold configuration-derived filesystem state such as URI, working directory, target filesystem, trash path, and deletion interval.
- `CommonAuditContext` has thread-local context and process-wide global context. Supplier-valued entries are long-lived and can create memory retention risks.
- `FsPermission` and `IOStatisticsSnapshot` are serializable; both include validation or deserialization safety notes. `IOStatisticsSnapshot` uses concrete sorted map structures for cross-framework transport and JSON serialization.
- `MeanStatistic` maintains mutable sample/sum state with synchronized update paths.
- Metric-name classes intentionally persist stable string constants for external dashboards, tests, and log parsing.

## Dependencies And Integration Points

The APIs depend on core Hadoop types including `Configuration`, `FileSystem`, `FileContext`, `FSDataInputStream`, `FSDataOutputStream`, `FileStatus`, `FileRange`, `Path`, `PathHandle`, `Progressable`, `CreateFlag`, `Options.ChecksumOpt`, `Options.HandleOpt`, `FsPermission`, `StorageType`, `JsonSerialization`, and statistics/duration tracker interfaces.

External Java dependencies include `java.net.URI`, `java.io` streams and serialization types, `java.nio.ByteBuffer`, `java.util` collections/enums/optionals, `java.util.concurrent.CompletableFuture`, Java functional interfaces, and SLF4J `Logger`. FTP integration is explicitly backed by Apache Commons Net. Object-store integration is signaled through store/stream statistics, multipart upload builder APIs, prefetch/cache metric names, and package docs for shared object-store internals.

The chunk integrates with HDFS and non-HDFS implementations through shared filesystem interfaces: safe mode action compatibility, ACL/effective permission compatibility with older NameNodes, storage-type quota support, encryption-zone-aware trash lookup, ViewFS mountpoint behavior, and stream/path capability probes that let clients select optional behavior without binding to implementation classes.

## Risks And Edge Cases

Thread-safety is a recurring risk. `PositionedReadable` requires thread-safe positional reads, but the docs explicitly warn that not all filesystems satisfy it. Dynamic `IOStatistics` can be non-atomic across multiple map/value reads, so callers must avoid assuming snapshot consistency unless they create an `IOStatisticsSnapshot`.

Security-sensitive edges include malicious Java object streams for `Path` and `FsPermission`, untrusted deserialization of `IOStatisticsSnapshot`, supplier retention in `CommonAuditContext`, and xattr value decoding of user-provided text/hex/base64 inputs.

Compatibility risks include stable ACL string formats, stable metric names, deprecated `TrashPolicy` initialization/factory overloads, deprecated permission bits moved to `FileStatus`, and `QuotaUsage` output formatting. Changing these can break shell output, serialized data, dashboards, and downstream filesystem implementations.

Filesystem behavior varies by backend. `RawLocalFileSystem.listStatus` is documented as unsorted because it relies on Java `File.list()`. FTP create streams can block other API calls until closed. Rename, symlink, path capability, trash movement, path handles, and vectored IO are backend-sensitive and need careful capability probing.

The chunk boundary truncates `ViewFileSystem`, so no conclusion should be drawn here about its full constructor or methods. The merge lane must combine the following chunk before summarizing ViewFS behavior.

## Test Signals

Relevant tests should assert API contract behavior rather than XML parsing alone:

- Path qualification and deserialization validation reject invalid serialized state and correctly resolve URI/working-directory combinations.
- Positional read implementations preserve or document stream-position behavior, throw `EOFException` for incomplete `readFully`, validate non-overlapping vectored ranges, and release allocated buffers on failure when supported.
- Local and FTP filesystem contract tests cover create/open/append/delete/list/rename/truncate/mkdir/status/metadata operations, unsorted local listings, FTP stream-close blocking behavior, Windows destination-directory rename handling, and capability probes.
- Trash tests cover disabled trash, already-in-trash paths, mountpoint/symlink volume resolution, encryption-zone-aware trash directory selection, checkpoint creation, scheduled expunge, and immediate expunge.
- ACL and permission tests cover stable string round trips, parse failures, masked/unmasked create modes, umask handling, effective permission with and without old-NameNode compatibility data, serialization, and deprecated-bit migration to `FileStatus`.
- XAttr tests cover text, quoted text, hex, base64, invalid encodings, and create/replace flag validation.
- Audit context tests should verify thread-local isolation, global entry visibility, entry-point recording, reset behavior, supplier evaluation, and cleanup to avoid retained large objects.
- Builder tests should verify path-vs-path-handle exclusivity, typed `opt`/`must` storage, unknown mandatory-key rejection, buffer/status propagation, multipart flag transitions, and implementation-specific build failures.
- IOStatistics tests should cover stable key sets, post-close access, snapshot/aggregate/setter synchronization, JSON and Java serialization allowlists, mean-statistic edge cases, lazy logging, and consistency of exported metric names used by object stores and streams.
