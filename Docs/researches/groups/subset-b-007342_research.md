# Research Report: subset-b-007342

This grouped report covers the requested Hadoop `org.apache.hadoop.fs` source files. Each section is wrapped with the reconciliation markers for its original source path.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CommonPathCapabilities.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CommonPathCapabilities.java

Purpose: `CommonPathCapabilities` is a final constants-only catalog of capability probe names used by `FileSystem.hasPathCapability(Path, String)` and related filesystem integrations. It centralizes string keys for ACLs, append, checksums, concat, corrupt block listing, path handles, permissions, read-only connectors, snapshots, storage policies, symlinks, truncate, xattrs, batch listing, multipart upload, abortable streams, etags, lease recovery, inconsistent directory listings, bulk delete, and virtual block locations.

Important APIs and types: the class has a private constructor and exports only `public static final String` constants. `FS_EXPERIMENTAL_BATCH_LISTING` is explicitly marked `InterfaceStability.Unstable`. Several constants reference optional interfaces such as `BatchListingOperations`, `Abortable`, `EtagSource`, and `LeaseRecoverable`.

Control flow, state, and persistence: there is no runtime control flow, mutable state, serialization, or persistence. The behavior comes entirely from callers using these exact strings to advertise and query path-scoped behavior.

Dependencies and integration: this file integrates the common filesystem API with concrete stores including HDFS, object stores, and connectors. The constants are consumed by capability policies, stream capability checks, and application code deciding whether to invoke optional operations.

Risks and test signals: risk is mostly compatibility drift. String changes break ecosystem probes, and over-advertising capabilities can cause callers to depend on unsupported semantics. Tests should assert exact constant values, provider responses from `hasPathCapability`, and behavior-gated paths such as etag, abort, bulk delete, and inconsistent listing handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CommonPathCapabilities.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CompositeCrcFileChecksum.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CompositeCrcFileChecksum.java

Purpose: `CompositeCrcFileChecksum` is a HDFS-limited, unstable `FileChecksum` implementation for a four-byte composite CRC. It records the CRC integer, the `DataChecksum.Type`, and bytes-per-CRC metadata so callers can identify both the checksum value and the data checksum parameters that produced it.

Important APIs and types: `LENGTH` is fixed at four bytes. `getAlgorithmName()` returns `"COMPOSITE-" + crcType.name()`, `getLength()` returns `LENGTH`, `getBytes()` serializes the int through `CrcUtil.intToBytes`, and `getChecksumOpt()` returns `Options.ChecksumOpt`. Writable methods `readFields` and `write` persist only the CRC integer.

Control flow, state, and persistence: construction initializes all fields. The wire format is intentionally minimal: only `crc` is read/written, so callers must preserve `crcType` and `bytesPerCrc` through construction or surrounding protocol context. `toString()` renders the algorithm name and a zero-padded hex CRC.

Dependencies and integration: it extends the abstract `FileChecksum` equality/hash contract and uses Hadoop utility classes `CrcUtil` and `DataChecksum`. HDFS checksum paths can return this type where composite CRCs are computed over block-level data.

Risks and test signals: the main risk is incomplete Writable reconstruction because `crcType` and `bytesPerCrc` are not serialized here. Tests should cover algorithm naming, byte order, `ChecksumOpt`, equality inherited from `FileChecksum`, and round trips in the actual protocol that supplies the missing metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CompositeCrcFileChecksum.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ContentSummary.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ContentSummary.java

Purpose: `ContentSummary` is a public, evolving summary object for file or directory content. It extends `QuotaUsage` and adds length, file count, directory count, snapshot-specific counters, snapshot space consumption, and erasure coding policy display support.

Important APIs and types: the nested `Builder` extends `QuotaUsage.Builder` and provides fluent setters for content, snapshot, quota, and storage-type quota fields. Public getters expose all summary fields. `write` and `readFields` implement legacy `Writable` serialization for length, file count, directory count, quota, space consumed, and space quota. Static header helpers and `toString` overloads produce CLI-style fixed-width summaries, quota summaries, storage-type quota summaries, erasure coding policy columns, and snapshot columns.

Control flow, state, and persistence: `Builder.build()` sets inherited file-and-directory count before constructing the object. Formatting chooses storage-type quota output when `tOption` is true, quota prefix when `qOption` is true, and optionally subtracts snapshot counts when `xOption` is true. Serialization intentionally omits snapshot fields and erasure coding policy, preserving older wire compatibility but losing newer state on a raw Writable round trip.

Dependencies and integration: this class is returned by filesystem content-summary operations and feeds command output such as quota and count reports. It depends on `QuotaUsage`, `StorageType`, `Writable`, and `StringUtils.TraditionalBinaryPrefix`.

Risks and test signals: `equals`, `hashCode`, and `toErasureCodingPolicy` dereference `erasureCodingPolicy`, so null policies can fail unless callers set a value. Tests should cover builder defaults, deprecated constructors, Writable compatibility, human-readable formatting, snapshot exclusion math, storage-type output, and null/replicated EC policy behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ContentSummary.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CreateFlag.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CreateFlag.java

Purpose: `CreateFlag` defines public create and append semantics for Hadoop filesystem writes. It models POSIX-like create, overwrite, append, sync, lazy persist, new block append, locality placement hints, and replication enforcement.

Important APIs and types: enum values carry a short mode used by lower layers. Core validation methods are `validate(EnumSet<CreateFlag>)`, `validate(Object, boolean, EnumSet<CreateFlag>)`, and `validateForAppend(EnumSet<CreateFlag>)`. Public flags include `CREATE`, `OVERWRITE`, `APPEND`, `SYNC_BLOCK`, `LAZY_PERSIST`, `NEW_BLOCK`, `NO_LOCAL_WRITE`, `SHOULD_REPLICATE`, `IGNORE_CLIENT_LOCALITY`, and `NO_LOCAL_RACK`.

Control flow, state, and persistence: validation rejects null or empty flag sets and rejects `APPEND` with `OVERWRITE`. Path-aware validation enforces that existing paths require append or overwrite and non-existing paths require create. Append validation additionally requires `APPEND`. The enum itself is static process state; no persistence is implemented here.

Dependencies and integration: create builders, `FileSystem` implementations, and HDFS clients use these flags to select create or append behavior. Exceptions integrate with `HadoopIllegalArgumentException`, `FileAlreadyExistsException`, and `FileNotFoundException`.

Risks and test signals: flag combinations are a compatibility surface. The `NO_LOCAL_RACK` mode value overlaps the `IGNORE_CLIENT_LOCALITY` bit plus `NEW_BLOCK` rather than a single new bit, which tests should preserve or flag deliberately. Tests should cover all valid combinations, invalid append/overwrite combinations, path existence branches, and builder integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CreateFlag.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DF.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DF.java

Purpose: `DF` provides filesystem disk-space statistics for a local path. It uses Java `File` APIs for capacity, used, and available bytes, and the platform `df` command on Unix-like systems to identify filesystem and mount point.

Important APIs and types: constructors accept `File` plus either `Configuration` or refresh interval. Accessors include `getDirPath`, `getFilesystem`, `getCapacity`, `getUsed`, `getAvailable`, `getPercentUsed`, and `getMount`. It extends `Shell`, overrides `getExecString` and `parseExecResult`, and exposes `parseOutput` for tests.

Control flow, state, and persistence: construction stores the canonical path and initializes an output buffer. `getFilesystem` and `getMount` use Windows drive-letter logic on Windows and otherwise run `df -k -P`, verify exit code, and parse output. `parseOutput` handles long filesystem names split across lines. State is cached in fields but refreshed by `Shell.run()` according to the interval; no durable persistence exists.

Dependencies and integration: HDFS and MapReduce disk accounting use this class, and `DFCachingGetSpaceUsed` wraps it for cached usage estimates. It depends on `Shell`, `Configuration`, `CommonConfigurationKeys`, and `java.io.File`.

Risks and test signals: parsing is sensitive to locale/output shape, command availability, paths containing shell-sensitive characters, and zero-capacity percent math. Tests should cover Windows branches, missing paths, long filesystem lines, nonzero exit codes, malformed numeric fields, and consistency between Java `File` usage values and parsed mount identity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DF.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DFCachingGetSpaceUsed.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DFCachingGetSpaceUsed.java

Purpose: `DFCachingGetSpaceUsed` is a fast but approximate `CachingGetSpaceUsed` implementation. It assumes the whole mount belongs to HDFS and that no two HDFS data directories share the same disk, then reports used space from `DF`.

Important APIs and types: the constructor accepts a `CachingGetSpaceUsed.Builder`, initializes the superclass, and creates a `DF` with the builder path and interval. The only behavior override is `refresh()`, which assigns `used` from `df.getUsed()`.

Control flow, state, and persistence: all caching, threading, interval, jitter, and `used` state are inherited from `CachingGetSpaceUsed`. This class only refreshes the inherited atomic usage value. It does not persist usage estimates.

Dependencies and integration: it is selected through `fs.getspaceused.classname` configuration and integrates local disk accounting with HDFS/MapReduce callers that prefer a cheap mount-wide estimate over recursive `du`.

Risks and test signals: the core risk is semantic inaccuracy when other data shares the volume or multiple data dirs share a disk. Tests should use mocked or temporary `DF` behavior where possible and verify that builder interval/path are honored, refresh updates inherited state, and the class behaves acceptably when `DF` construction or access fails in the environment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DFCachingGetSpaceUsed.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DU.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DU.java

Purpose: `DU` is a `CachingGetSpaceUsed` implementation backed by the Unix `du -sk` command. It reports recursive disk usage for a configured path and logs refresh failures instead of surfacing them to periodic callers.

Important APIs and types: the visible-for-testing constructor accepts path, interval, jitter, and initial usage. The public builder constructor extracts those values from `CachingGetSpaceUsed.Builder`. `refresh()` invokes the nested `DUShell`, whose `getExecString()` returns `du -sk <dir>` and whose parser reads the first tab-separated size field.

Control flow, state, and persistence: `CachingGetSpaceUsed` owns cached usage state and scheduling. `DU.refresh()` runs the shell command and sets usage to kilobytes times 1024. Parser errors or command failures are logged as warnings and leave prior cached state intact. There is no durable persistence.

Dependencies and integration: this is the more precise alternative to `DFCachingGetSpaceUsed` for HDFS data directories. It depends on `Shell`, `Configuration`, and the inherited cache machinery.

Risks and test signals: risks include platform dependence, inaccessible paths, `du` output shape, tabs vs spaces, huge values, and stale cached usage after failures. Tests should cover parser behavior, failure logging without state corruption, initial usage, builder wiring, and the `main` path through `GetSpaceUsed.Builder`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DU.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DUHelper.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DUHelper.java

Purpose: `DUHelper` is a simple recursive Java helper for computing folder byte usage and file counts without shelling out. It appears as a standalone utility rather than part of the `CachingGetSpaceUsed` hierarchy.

Important APIs and types: `getFolderUsage(String)` creates a helper and returns `calculateFolderSize`. `check(String)` computes folder size, file count, and disk usage ratio. Accessors expose `getFileCount()` and `getUsage()`. The private recursive `getFileSize(File)` walks directories and sums file lengths.

Control flow, state, and persistence: each helper instance maintains mutable counters `folderCount`, `fileCount`, `usage`, and `folderSize`. Recursion increments `folderCount`, returns `folder.length()` for direct files, returns zero if `listFiles()` is null, and adds child directory/file sizes. No state is persisted beyond the object.

Dependencies and integration: it uses `java.io.File` and `Shell.WINDOWS` only for the demo `main` output label. It is independent from `DU` and `DF`.

Risks and test signals: recursive walking can be slow, can follow filesystem structures with permission failures as zero-sized directories, and can overflow or recurse deeply on large trees. `check` can divide by zero if `getTotalSpace()` is zero. Tests should cover null input, files vs directories, inaccessible directories, nested counts, empty folders, and usage ratio behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DUHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DelegateToFileSystem.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DelegateToFileSystem.java

Purpose: `DelegateToFileSystem` adapts an old `FileSystem` implementation to the newer `AbstractFileSystem` API used by `FileContext`. It forwards most filesystem operations after applying `AbstractFileSystem` path checks and initialization.

Important APIs and types: the constructor initializes the delegate, passes scheme/authority/default-port data to `AbstractFileSystem`, and shares statistics. Delegated operations include create, delete, block locations, checksums, status, listing, mkdir, open, truncate, rename, ownership/permission/times, symlinks, server defaults, delegation tokens, async open with options, and path capability checks.

Control flow, state, and persistence: `getDefaultPortIfDefined` converts `FileSystem.getDefaultPort() == 0` into `-1` to match `URI.getPort()` semantics. `createInternal` has meaningful local logic: when `createParent` is false, it verifies a present parent path, existing status, and directory type before calling `primitiveCreate`. `getFileLinkStatus` rewrites symlink targets from qualified to plain. No state is persisted beyond the delegate reference and shared statistics.

Dependencies and integration: this class is the bridge between `FileSystem`, `AbstractFileSystem`, `FileContext`, `Options.ChecksumOpt`, token APIs, permissions, and `OpenFileParameters`.

Risks and test signals: risks are behavioral mismatches between `FileSystem` and `AbstractFileSystem`, especially symlink qualification, default-port handling, parent creation semantics, and token list handling when `addDelegationTokens` returns null or empty arrays. Tests should exercise delegated path checks, create-parent branches, symlink targets, rename semantics, and capability forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DelegateToFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DelegationTokenRenewer.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DelegationTokenRenewer.java

Purpose: `DelegationTokenRenewer` is a singleton daemon thread that periodically renews or replaces delegation tokens for filesystems implementing both `FileSystem` and the nested `Renewable` interface.

Important APIs and types: `Renewable` exposes `getRenewToken()` and `setDelegationToken(Token<T>)`. `RenewAction<T>` implements `Delayed`, stores a weak filesystem reference, the current token, renewal time, and validity flag. Public renewer methods include `getInstance`, testing `reset`, `addRenewAction`, and `removeRenewAction`.

Control flow, state, and persistence: the singleton starts lazily on first add. Actions are ordered in a `DelayQueue`; renewal time is scheduled at 90 percent of the provided delay. `renew()` tries `token.renew(conf)`, updates next renewal from the returned expiry, and on failure tries `addDelegationTokens`; if replacement succeeds it updates the filesystem token, otherwise marks the action invalid and throws. Weak references allow filesystem objects to disappear without preventing garbage collection. State is in-memory only.

Dependencies and integration: it uses Hadoop security `Token`, `TokenIdentifier`, `Time`, `SubjectInheritingThread`, and `FileSystem.LOG`. It integrates with filesystems that own renewable delegation credentials.

Risks and test signals: risks include singleton lifecycle races, token equality/hash behavior while queued, replacement failures, cancellation interruptions, and action removal constructing a new action around the current token. Tests should cover lazy start, delay ordering, weak-reference expiry, renew success, replacement success/failure, cancellation, reset, and queue length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DelegationTokenRenewer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DirectoryListingStartAfterNotFoundException.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DirectoryListingStartAfterNotFoundException.java

Purpose: `DirectoryListingStartAfterNotFoundException` is an HDFS-limited stable exception thrown when a paged directory listing cannot find the requested `startAfter` marker.

Important APIs and types: it extends `IOException`, declares `serialVersionUID = 1L`, and provides default and message constructors.

Control flow, state, and persistence: the class has no custom control flow or mutable state. Its serialized form follows normal `IOException` behavior plus the declared serial id.

Dependencies and integration: directory listing implementations can throw this to distinguish missing pagination anchors from generic listing failures. Callers can catch it separately to retry from a different marker, surface a precise error, or handle object-store consistency behaviors.

Risks and test signals: risk is low but compatibility matters because exception type is part of HDFS listing contracts. Tests should assert constructors, message preservation, catchability as `IOException`, and correct use in listing paths where `startAfter` is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DirectoryListingStartAfterNotFoundException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/EmptyStorageStatistics.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/EmptyStorageStatistics.java

Purpose: `EmptyStorageStatistics` is a package-private no-op `StorageStatistics` implementation for filesystems or components that need a statistics object but have no counters to report.

Important APIs and types: the constructor passes a name to `StorageStatistics`. `getLongStatistics()` returns an empty iterator, `getLong(String)` returns null, `isTracked(String)` returns false, and `reset()` is a no-op.

Control flow, state, and persistence: after construction, behavior is fixed and stateless apart from the inherited name. No counters are allocated, reset does nothing, and no data is persisted.

Dependencies and integration: it depends on `StorageStatistics` and `Collections.emptyIterator()`. It is useful as a null-object implementation in filesystem statistics wiring, avoiding null checks for statistics containers.

Risks and test signals: risks are mostly caller assumptions. Code expecting non-null `Long` values or a tracked key can misinterpret this empty implementation. Tests should verify empty iteration, null value lookup, false tracking for arbitrary keys, idempotent reset, and inherited name behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/EmptyStorageStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/EtagSource.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/EtagSource.java

Purpose: `EtagSource` is an optional interface for `FileStatus` subclasses that can expose an object or file etag. It lets clients retrieve identity/version markers when a filesystem supports them.

Important APIs and types: the single API is `String getEtag()`. The contract allows null or empty string to mean no etag.

Control flow, state, and persistence: the interface has no implementation state. Persistence and etag stability are delegated to concrete `FileStatus` and filesystem implementations.

Dependencies and integration: the interface is paired with `CommonPathCapabilities.ETAGS_AVAILABLE` and `ETAGS_PRESERVED_IN_RENAME`. Filesystem listing and status calls can return `FileStatus` instances implementing this interface so applications can perform optimistic consistency checks, cache validation, or rename-preservation checks.

Risks and test signals: risks come from inconsistent capability advertisement, empty-vs-null handling, and rename semantics. Tests should verify that status objects implement `EtagSource` only when meaningful, that capability probes match returned statuses, and that providers claiming rename preservation actually preserve etags across rename operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/EtagSource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSBuilder.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSBuilder.java

Purpose: `FSBuilder<S, B>` is the public base interface for filesystem and file-context builders. It provides optional and mandatory typed key/value setters plus `build()`, while preserving binary compatibility with older overloaded numeric methods.

Important APIs and types: core abstract methods are `opt(String, String)`, `opt(String, String...)`, `must(String, String)`, `must(String, String...)`, and `build()`. Default overloads convert booleans to strings, ints and longs through `optLong`/`mustLong`, and doubles through `optDouble`/`mustDouble`. Deprecated float/double overloads intentionally cast to long for compatibility with previous linkage behavior.

Control flow, state, and persistence: the interface stores no state. Implementations decide how optional and mandatory options are retained and validated. Mandatory options are expected to make `build()` fail with `IllegalArgumentException` if unsupported or unavailable.

Dependencies and integration: `FSDataOutputStreamBuilder` and open/create builders extend or implement this interface. It integrates typed user-facing builder calls with implementation-specific option parsing in `AbstractFSBuilderImpl` and concrete filesystems.

Risks and test signals: overload resolution and numeric conversion are the main risks. Floating-point values passed to deprecated overloads lose precision by design. Tests should compile-call all overloads, assert resulting option strings in implementations, verify mandatory option rejection, and cover source/binary compatibility scenarios referenced by HADOOP-16202 and HADOOP-18724 comments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSDataInputStream.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSDataInputStream.java

Purpose: `FSDataInputStream` wraps an `InputStream` as a data input stream with Hadoop seek, positioned read, byte-buffer read, vector read, unbuffer, stream capability, and IO statistics interfaces.

Important APIs and types: the constructor requires the wrapped stream to implement both `Seekable` and `PositionedReadable`. It delegates `seek`, `getPos`, `read(position, byte[])`, `readFully`, `seekToNewSource`, byte-buffer reads, file descriptor access, readahead/drop-behind, enhanced byte-buffer reads, unbuffer, stream capabilities, IO statistics, and vectored reads.

Control flow, state, and persistence: the only local mutable state is an `IdentityHashStore<ByteBuffer, ByteBufferPool>` tracking fallback enhanced-read buffers. If the wrapped stream lacks `HasEnhancedByteBufferAccess`, `read(ByteBufferPool, int, opts)` uses `ByteBufferUtil.fallbackRead` and records the returned buffer for later release. `releaseBuffer` either delegates or returns fallback buffers to their original pool, rejecting unknown buffers. No stream state is persisted by this wrapper.

Dependencies and integration: this is the standard public read stream returned by Hadoop filesystems. It integrates with optional interfaces, `StoreImplementationUtils`, `ByteBufferPool`, `IOStatisticsSupport`, and `PositionedReadable` vector APIs.

Risks and test signals: risk centers on optional capability casts, buffer lifecycle leaks, and unsupported operation messages. Tests should cover constructor rejection, delegation, fallback buffer release, unknown buffer release, null file descriptors, unbuffer policy, byte-buffer positioned reads, vectored reads, and IO statistics retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSDataInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSDataOutputStream.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSDataOutputStream.java

Purpose: `FSDataOutputStream` wraps an `OutputStream` as a Hadoop data output stream with byte-position tracking, statistics updates, sync/drop-behind/capability delegation, IO statistics, and optional abort support.

Important APIs and types: the nested `PositionCache` updates an internal position and optional `FileSystem.Statistics` on every write. Public APIs include constructors with optional start position, `getPos`, `getWrappedStream`, `hflush`, `hsync`, `setDropBehind`, `hasCapability`, `getIOStatistics`, and `abort`.

Control flow, state, and persistence: writes go through `PositionCache`, which increments position by written byte count and increments filesystem statistics. `hflush` and `hsync` delegate to `Syncable` streams or fall back to `flush`. Drop-behind and abort require the wrapped stream to implement the corresponding optional interfaces; otherwise they throw `UnsupportedOperationException`. State is in-memory only.

Dependencies and integration: this is the public output stream returned by create/append APIs. It integrates with `Syncable`, `CanSetDropBehind`, `StreamCapabilities`, `Abortable`, `IOStatisticsSupport`, `StoreImplementationUtils`, and `FSExceptionMessages`.

Risks and test signals: risks include position/statistics drift if wrapped streams partially write before throwing, unsupported optional APIs, and closing null or already-closed wrapped streams. Tests should cover single-byte and array writes, start position, statistics increments, sync fallback, capability forwarding, abort success/failure, drop-behind failure, and IO statistics retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSDataOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSDataOutputStreamBuilder.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSDataOutputStreamBuilder.java

Purpose: `FSDataOutputStreamBuilder` is the public evolving abstract builder for creating or appending `FSDataOutputStream` instances through either `FileSystem` or `FileContext` pathways.

Important APIs and types: it extends `AbstractFSBuilderImpl<S, B>` and stores filesystem/default write settings: permission, buffer size, replication, block size, recursive parent creation, create flags, progress callback, and checksum options. Fluent methods include `permission`, `bufferSize`, `replication`, `blockSize`, `recursive`, `progress`, `create`, `overwrite`, `append`, and `checksumOpt`. Concrete subclasses implement `getThisBuilder()` and `build()`.

Control flow, state, and persistence: constructors derive defaults from `FileContext` server defaults or `FileSystem` configuration/default replication/block size. `getPermission()` lazily supplies `FsPermission.getFileDefault()`. `overwrite(false)` removes the overwrite flag; `create()` and `append()` add flags. State is held in the builder until `build()`; no persistence exists.

Dependencies and integration: it bridges public builder calls to `FileSystem` and `AbstractFileSystem` create/append implementations, relying on `CreateFlag`, `Options.ChecksumOpt`, `FsPermission`, `Progressable`, and common IO buffer configuration.

Risks and test signals: risks include inconsistent defaults between FileSystem and FileContext paths, mutable flag set exposure through protected getter, and unsupported mandatory options handled by subclasses. Tests should cover defaults, fluent chaining, recursive flag, overwrite toggling, permission defaulting, checksum option propagation, and subclass build validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSDataOutputStreamBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSError.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSError.java

Purpose: `FSError` is a public stable `Error` subtype used for unexpected filesystem failures presumed to reflect serious native disk errors rather than normal recoverable IOExceptions.

Important APIs and types: it extends `Error`, declares `serialVersionUID = 1L`, and has a package-private constructor accepting a `Throwable` cause.

Control flow, state, and persistence: no custom control flow exists. The only state is the inherited cause chain. The package-private constructor restricts creation to Hadoop filesystem package code.

Dependencies and integration: local/native filesystem implementations can wrap severe lower-level failures in `FSError` to signal unrecoverable conditions. Since it is an `Error`, most application code will not catch it.

Risks and test signals: the main risk is overuse for recoverable IO paths, which would bypass normal retry/error handling. Tests should verify cause preservation and that only intended package-level code paths throw it for serious disk-like failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSError.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSExceptionMessages.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSExceptionMessages.java

Purpose: `FSExceptionMessages` centralizes standard filesystem exception message strings, using HDFS wording as the reference for common stream, seek, EOF, buffer, permission, sticky-bit, and abort unsupported errors.

Important APIs and types: it is a public constants class exporting messages such as `STREAM_IS_CLOSED`, `NEGATIVE_SEEK`, `CANNOT_SEEK_PAST_EOF`, `EOF_IN_READ_FULLY`, `TOO_MANY_BYTES_FOR_DEST_BUFFER`, `PERMISSION_DENIED`, `PERMISSION_DENIED_BY_STICKY_BIT`, and `ABORTABLE_UNSUPPORTED`.

Control flow, state, and persistence: there is no runtime behavior or state. Constants are compile-time shared strings used by other filesystem classes.

Dependencies and integration: `FSInputChecker`, `FSInputStream`, `FSDataOutputStream`, and many filesystem implementations use these strings to keep diagnostics consistent across connectors.

Risks and test signals: risk is compatibility of exact messages in tests, logs, and user diagnostics. Tests should not overfit unnecessarily, but API-level tests may assert these constants where specific wording is part of a documented contract. Static analysis can catch duplicate divergent messages in filesystem code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSExceptionMessages.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSInputChecker.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSInputChecker.java

Purpose: `FSInputChecker` is an abstract `FSInputStream` that verifies checksums before returning data to users. Subclasses provide checksum-aware `readChunk` and chunk-boundary mapping through `getChunkPosition`.

Important APIs and types: constructors configure file identity, retry count, checksum verification, `Checksum`, chunk size, and checksum size. Key methods are `read`, `read(byte[], int, int)`, `readAndDiscard`, `seek`, `skip`, `available`, `getPos`, `set`, `readFully(InputStream, ...)`, and abstract `readChunk`/`getChunkPosition`. It uses `ChecksumException` and standard four-byte checksums.

Control flow, state, and persistence: local state tracks current chunk position, internal data buffer, checksum bytes, checksum int view, buffer position/count, verification flag, and retry count. Reads use buffered small reads or direct user-buffer chunk reads. `readChecksumChunk` invokes the subclass, verifies each chunk with `verifySums`, advances `chunkPos`, and on checksum error retries against a new source via `seekToNewSource`. `seek` can reposition within the current buffer, otherwise resets to a chunk boundary and discards bytes to the requested offset. No durable persistence exists.

Dependencies and integration: HDFS-like input streams subclass this to combine data and checksum streams. It depends on `FSInputStream`, `Checksum`, `ChecksumException`, logging, and `FSExceptionMessages`.

Risks and test signals: risks include checksum-size assumptions, retry off-by-one behavior, seeking past EOF semantics, synchronization bottlenecks, and reading/discarding corrupt intermediate bytes. Tests should cover aligned and unaligned reads, partial chunks, disabled checksums, checksum mismatch retry success/failure, negative seek, buffer-position seeking, skip beyond EOF, mark/reset behavior, and checksum byte order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSInputChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSInputStream.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSInputStream.java

Purpose: `FSInputStream` is the public evolving base class for Hadoop input streams that support seeking and positioned reads in addition to normal `InputStream` reads.

Important APIs and types: subclasses must implement `seek`, `getPos`, and `seekToNewSource`. The class implements default positioned `read(position, buffer, offset, length)`, `readFully` overloads, argument validation, and a `toString` that includes IO statistics when the subclass implements `IOStatisticsSource`.

Control flow, state, and persistence: positioned read validates arguments, synchronizes on the stream, saves the old position, seeks to the requested position, reads, downgrades EOFException to `-1`, and always seeks back to the old position. `readFully` loops until the requested length is filled or throws `EOFException`. The base class stores no mutable stream state itself.

Dependencies and integration: this is the superclass behind `FSDataInputStream` wrappers and filesystem-specific input streams. It uses `Seekable`, `PositionedReadable`, `FSExceptionMessages`, preconditions, logging, and IO statistics formatting.

Risks and test signals: default positioned reads are correct but potentially inefficient and synchronized. Implementations with expensive seek or non-idempotent read behavior may need overrides. Tests should cover negative positions, null buffers, insufficient destination space, zero-length reads, EOF downgrading, restoration of original position after failures, and `readFully` EOF behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSLinkResolver.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSLinkResolver.java

Purpose: `FSLinkResolver<T>` is a generic helper used mainly by `FileContext` to run an operation while resolving symlinks, potentially across multiple `AbstractFileSystem` instances.

Important APIs and types: subclasses implement `next(AbstractFileSystem fs, Path p)`. `resolve(FileContext, Path)` loops through unresolved links until the operation succeeds. Static `qualifySymlinkTarget(URI, Path, Path)` qualifies absolute targets lacking scheme and authority against the current filesystem URI and link parent.

Control flow, state, and persistence: `resolve` starts with `fc.getFSofPath(path)`, calls `next`, and catches `UnresolvedLinkException`. If symlink resolution is disabled in `FileContext` or globally in `FileSystem`, it throws explanatory `IOException`s. It detects likely cycles using `FsConstants.MAX_PATH_LINKS`. Each resolved target may select a different filesystem. No state is persisted.

Dependencies and integration: it integrates `FileContext`, `AbstractFileSystem`, `FileSystem` symlink settings, `CommonConfigurationKeys`, `Path`, and `UnresolvedLinkException`.

Risks and test signals: risks include cycle detection boundary, target qualification across schemes, disabled symlink behavior, and partial targets that already include scheme or authority. Tests should cover relative/absolute target qualification, cross-filesystem symlinks, disabled resolution, global symlink disabling, loop limits, and operation success after multiple link hops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSLinkResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSOutputSummer.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSOutputSummer.java

Purpose: `FSOutputSummer` is an abstract output stream that generates checksums for data chunks before writing chunks and checksum bytes to an underlying implementation.

Important APIs and types: subclasses implement `writeChunk(byte[], int, int, byte[], int, int)` and `checkClosed()`. Public and protected APIs include `write(int)`, `write(byte[], int, int)`, `flush`, `flushBuffer`, `flushBuffer(keep, flushPartial)`, `getBufferedDataSize`, `getChecksumSize`, `getDataChecksum`, `setChecksumBufSize`, `resetChecksumBufSize`, `convertToByteStream`, and `createWriteTraceScope`.

Control flow, state, and persistence: the class maintains a data checksum, a data buffer sized to nine checksum chunks, a checksum buffer, and a byte count. Large writes bypass copying when the internal buffer is empty and the input length covers the whole buffer. `flush()` writes only complete chunks, while `flushBuffer(..., flushPartial)` controls whether trailing partial chunks are written or kept. `writeChecksumChunks` calculates chunked sums and invokes `writeChunk` per chunk inside an optional tracing scope. No durable persistence exists.

Dependencies and integration: HDFS output streams subclass this to pair data packet writes with checksums. It depends on `DataChecksum`, `TraceScope`, `StreamCapabilities`, and `Checksum`.

Risks and test signals: risks include partial chunk handling, buffer resizing, checksum-size assumptions in `int2byte`, close-state checks only on array writes, and write failures after checksums are computed. Tests should cover single-byte writes, direct large writes, partial flush keep/drop behavior, buffer resize/reset, checksum bytes, tracing scope close, and subclass close enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSOutputSummer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileAlreadyExistsException.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileAlreadyExistsException.java

Purpose: `FileAlreadyExistsException` is a public stable checked exception used when a target file already exists and the requested operation is not configured to overwrite or append.

Important APIs and types: it extends `IOException` and exposes default and message constructors.

Control flow, state, and persistence: there is no custom behavior or mutable state. Normal `IOException` serialization and message handling apply.

Dependencies and integration: create paths, especially `CreateFlag.validate`, throw this exception to distinguish existing-target failures from generic IO failures. Filesystem clients can catch it to retry with overwrite, choose a different path, or report idempotency conflicts.

Risks and test signals: risks are low, but callers rely on this specific type for create semantics. Tests should verify message preservation and use in create validation and filesystem implementations when `CREATE` is used without overwrite/append against an existing path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileAlreadyExistsException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileChecksum.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileChecksum.java

Purpose: `FileChecksum` is the public stable abstract base for file checksum objects returned by Hadoop filesystems. It standardizes algorithm name, byte length, checksum bytes, optional checksum options, and equality/hash behavior.

Important APIs and types: subclasses implement `getAlgorithmName`, `getLength`, `getBytes`, and Writable serialization methods inherited from `Writable`. `getChecksumOpt()` returns null by default and can be overridden by implementations such as `CompositeCrcFileChecksum`. `equals` compares algorithm names and byte arrays; `hashCode` XORs their hashes.

Control flow, state, and persistence: this class stores no state. It defines value semantics over subclass-reported algorithm and bytes. Persistence is delegated to each concrete Writable implementation.

Dependencies and integration: it is returned by `FileSystem.getFileChecksum` and `AbstractFileSystem` checksum paths, and used by applications to compare file content integrity across filesystems. It depends on `Arrays`, `Options.ChecksumOpt`, and `Writable`.

Risks and test signals: risks include subclasses returning mutable arrays, null algorithm names, inconsistent `getLength` vs `getBytes().length`, or incomplete Writable state. Tests should cover equality/hash consistency, algorithm mismatch, byte mismatch, null/default checksum options, and concrete subclass serialization contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileChecksum.java -->
