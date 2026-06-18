# Research: subset-b-007341

Grouped research for Hadoop common `org.apache.hadoop.fs` sources. Each section is bounded by the required reconciliation markers and preserves the original source path in the section title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/AbstractFileSystem.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/AbstractFileSystem.java

Purpose: `AbstractFileSystem` is the stable `FileContext`-side base class for Hadoop filesystem implementations. It defines the URI, path validation, statistics, create/open/rename/list/status, ACL, xattr, snapshot, storage-policy, async-open, path-capability, and multipart-uploader surface that concrete `AbstractFileSystem` implementations must implement or explicitly decline.

Important APIs and types: the class implements `PathCapabilities`; exposes `get(URI, Configuration)` and `createFileSystem()` factories keyed by `fs.AbstractFileSystem.<scheme>.impl`; caches constructors in `CONSTRUCTOR_CACHE`; tracks per-base-URI `FileSystem.Statistics` in `STATISTICS_TABLE`; and defines abstract operations including `createInternal`, `mkdir`, `delete`, `open`, `setReplication`, `renameInternal`, `setPermission`, `setOwner`, `setTimes`, `getFileChecksum`, `getFileStatus`, `getFileBlockLocations`, `getFsStatus`, `listStatus`, and `setVerifyChecksum`.

Control flow: construction normalizes the service URI through `getUri()`, enforcing scheme, authority requirements, and default port behavior. Public create parses `Options.CreateOpts`, rejects duplicate option classes, fills missing values from `FsServerDefaults`, resolves `ChecksumOpt`, validates block/checksum divisibility, then delegates to `createInternal`. Rename converts varargs options into an overwrite flag; the default overwrite path reads source and destination link status, rejects incompatible file/directory replacement and non-empty directory overwrite, deletes a replaceable destination, then delegates to non-overwrite `renameInternal`. Listing defaults adapt array-based `listStatus` into `RemoteIterator`; located listing wraps file statuses and lazily fetches block locations for files. Optional features mostly throw `UnsupportedOperationException` unless subclasses override them.

State and persistence behavior: class state is limited to immutable `myUri` and a shared mutable statistics object. It does not persist metadata itself; concrete filesystems do. Static statistics and constructor caches are JVM-local process state and can be reset only through `clearStatistics()`.

Dependencies and integration points: integrates with `FileContext`, `Path`, `FsServerDefaults`, `Options.CreateOpts`, Hadoop security (`UserGroupInformation`, delegation `Token`, `SecurityUtil`), ACL/xattr types, `BlockStoragePolicySpi`, `AbstractFSBuilderImpl`, `OpenFileParameters`, `LambdaUtils`, and common path capability constants. It is the adapter contract used by `FilterFs`, `ChecksumFs`, HDFS AFS implementations, and any filesystem exposed through `FileContext`.

Risks: the default overwrite rename is explicitly non-atomic and can lose the destination before a later rename failure. URI comparison is strict around scheme/host/port and can reject paths if default-port handling differs from a subclass. The create option parser is sensitive to duplicate option instances and contains a typo in the unknown option error, which can affect diagnostics. Most newer features default to unsupported, so callers must probe capabilities or handle exceptions.

Test signals: exercise scheme/authority/default-port normalization, `checkPath()` rejections, duplicate create option failures, default create option filling, rename overwrite edge cases, iterator behavior for empty and non-empty listings, `hasPathCapability()` for symlink capability, and unsupported optional operations. Concurrency-sensitive tests should cover static statistics and constructor cache reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/AbstractFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/AvroFSInput.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/AvroFSInput.java

Purpose: adapts Hadoop `FSDataInputStream` to Avro's `SeekableInput` interface so Avro readers can consume Hadoop filesystem files with seek and position support.

Important APIs and types: constructors accept either an existing `FSDataInputStream` plus length or a `FileContext` and `Path`; implements Avro `SeekableInput` methods `length`, `read`, `seek`, `tell`, and `Closeable.close`.

Control flow: the `FileContext` constructor fetches `FileStatus` to capture length, builds an async open request with sequential read policy and the known status, waits for the future through `FutureIO.awaitFuture`, then delegates all I/O calls to the opened stream.

State and persistence behavior: stores only the wrapped stream and immutable length. No persistence is performed beyond reads against the underlying filesystem.

Dependencies and integration points: bridges Hadoop `FileContext`, `Path`, `FileStatus`, `FSDataInputStream`, `Options.OpenFileOptions`, and Apache Avro `SeekableInput`.

Risks: caller-supplied length can be stale or wrong in the direct constructor. The `FileContext` constructor blocks awaiting an async builder result and can surface open failures before Avro begins reading. It assumes sequential policy is suitable for Avro access, though Avro can seek.

Test signals: verify length from status, read delegation, seek/tell consistency, close propagation, and open-builder options when constructed from `FileContext`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/AvroFSInput.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BBPartHandle.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BBPartHandle.java

Purpose: provides a private, unstable `PartHandle` implementation backed by a byte array for multipart upload part identifiers.

Important APIs and types: static `from(ByteBuffer)` creates a `PartHandle`; `bytes()` returns a new `ByteBuffer` wrapping the stored array; equality compares against any `PartHandle` by `ByteBuffer.equals`; `hashCode()` uses `Arrays.hashCode`.

Control flow: construction stores `byteBuffer.array()` directly. Reads wrap that same byte array for consumers.

State and persistence behavior: state is the byte array representing the serialized part handle. It is serializable through the `PartHandle` contract but has no external persistence logic.

Dependencies and integration points: used by multipart upload code that needs a simple byte-buffer-backed handle representation.

Risks: `ByteBuffer.array()` requires an array-backed buffer and ignores buffer position/limit, so direct, read-only, sliced, or offset buffers can fail or capture extra bytes. The stored array is not defensively copied, so mutations to the original backing array can mutate the handle. `ByteBuffer.equals` is position/limit-sensitive, making equality dependent on returned buffer state.

Test signals: cover array-backed input, direct/read-only rejection, position/limit behavior, equality with another handle, hash stability, and mutation of the original buffer backing array.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BBPartHandle.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BBUploadHandle.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BBUploadHandle.java

Purpose: private, unstable `UploadHandle` implementation backed by a byte array for multipart upload session identifiers.

Important APIs and types: static `from(ByteBuffer)` creates an `UploadHandle`; `bytes()` returns a wrapped `ByteBuffer`; `equals` accepts any `UploadHandle`; `hashCode` hashes the raw byte array.

Control flow: constructor stores `byteBuffer.array()` directly and later exposes that array through `ByteBuffer.wrap`.

State and persistence behavior: the only state is the backing byte array. The class has no storage or lifecycle behavior beyond the serializable handle contract.

Dependencies and integration points: integrates with Hadoop multipart upload APIs as a simple upload session token representation.

Risks: same buffer hazards as `BBPartHandle`: direct/read-only buffers cannot be converted, position/limit are ignored on input, the backing array is not copied, and equality is tied to `ByteBuffer` remaining-byte semantics.

Test signals: verify construction from ordinary buffers, failure for unsupported buffer kinds, immutability expectations under backing-array mutation, equality against other `UploadHandle` implementations, and hash/equality consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BBUploadHandle.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BatchListingOperations.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BatchListingOperations.java

Purpose: declares an optional, unstable filesystem extension for listing multiple paths in batched requests.

Important APIs and types: `batchedListStatusIterator(List<Path>)` returns `RemoteIterator<PartialListing<FileStatus>>`; `batchedListLocatedStatusIterator(List<Path>)` returns located entries with block locations.

Control flow: no implementation; filesystem implementations decide batching and iterator behavior. The interface documentation ties support to `CommonPathCapabilities.FS_EXPERIMENTAL_BATCH_LISTING`.

State and persistence behavior: none in the interface.

Dependencies and integration points: integrates with `Path`, `RemoteIterator`, `PartialListing`, `FileStatus`, `LocatedFileStatus`, and path capability probing.

Risks: capability declaration and interface implementation can diverge. Ordering and partial failure semantics are delegated to implementers and need clear implementation-specific tests.

Test signals: for implementers, validate one `PartialListing` per requested path, located status block metadata, error propagation, empty path lists, and capability advertisement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BatchListingOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BatchedRemoteIterator.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BatchedRemoteIterator.java

Purpose: provides a generic `RemoteIterator` implementation that pages through remote results using a previous-key marker.

Important APIs and types: nested `BatchedEntries<E>` exposes `get`, `size`, and `hasMore`; `BatchedListEntries<E>` wraps a `List<E>` plus a continuation flag; subclasses implement `makeRequest(K prevKey)` and `elementToPrevKey(E element)`.

Control flow: first `hasNext` or `next` triggers `makeRequest(prevKey)`. When the current batch is exhausted, `hasMore=false` ends iteration, while `hasMore=true` requests another batch using the last returned element's key. Empty returned batches are treated as end-of-data by setting `entries` to null.

State and persistence behavior: holds only in-memory iterator cursor state: previous key, current entries, and current index. It performs no persistence.

Dependencies and integration points: intended for HDFS and object-store listing APIs that use marker-based pagination, while exposing the standard Hadoop `RemoteIterator` contract.

Risks: if a service returns an empty batch with `hasMore=true`, iteration terminates early. If `elementToPrevKey` is unstable or non-monotonic, callers can skip or repeat entries. The class is not thread-safe.

Test signals: cover initial request, multi-page traversal, empty first page, exact-boundary pages, `next()` after exhaustion, and marker progression from returned entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BatchedRemoteIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BlockLocation.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BlockLocation.java

Purpose: serializable data holder describing where a file block or erasure-coded block group resides: hosts, transfer names, topology paths, storage IDs/types, offset, length, and corruption state.

Important APIs and types: multiple constructors normalize null arrays to shared empty arrays and intern string arrays through `StringInterner`; getters and setters expose hosts, cached hosts, names, topology paths, storage IDs, storage types, offset, length, and corrupt flag; `isStriped()` defaults false; `toString()` prints offset, length, corruption, and hosts.

Control flow: constructors funnel into the full constructor. Setters repeat the null-to-empty and string-interning behavior. Copy constructor copies array references rather than deep-copying arrays.

State and persistence behavior: mutable in-memory metadata object with Java serialization UID. It does not persist block locations itself; namenode/filesystem clients populate it from storage metadata.

Dependencies and integration points: returned by `FileSystem` and `FileContext` block location APIs, embedded in `LocatedFileStatus`, and interpreted differently for replicated vs erasure-coded files.

Risks: arrays are exposed directly by getters and accepted directly by setters, so callers can mutate internal state. Copy construction is shallow. `isStriped()` is false unless subclasses override, so erasure-coded specializations must be used where needed.

Test signals: validate constructor null handling, string interning side effects, getter/setter mutation, shallow copy behavior, `toString()` with corrupt blocks, and compatibility with located status serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BlockLocation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BlockStoragePolicySpi.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BlockStoragePolicySpi.java

Purpose: stable public SPI describing a block storage placement policy independently of HDFS implementation classes.

Important APIs and types: exposes policy name, preferred `StorageType[]`, creation fallbacks, replication fallbacks, and `isCopyOnCreateFile()` for inherit-only policies.

Control flow: interface only; concrete policy classes supply arrays and flags.

State and persistence behavior: no state in the interface. Implementations represent policy metadata that may come from namenode policy definitions.

Dependencies and integration points: returned from `AbstractFileSystem.getStoragePolicy` and `getAllStoragePolicies`; used by filesystem clients that need storage-type placement information.

Risks: array return values can be mutable depending on implementation. Callers should not assume HDFS-only policy names or storage types.

Test signals: implementation tests should assert stable names, fallback arrays, copy-on-create semantics, and defensive-copy behavior if promised by the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BlockStoragePolicySpi.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BufferedFSInputStream.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BufferedFSInputStream.java

Purpose: wraps an `FSInputStream` in a `BufferedInputStream` while preserving Hadoop seek, positioned read, file descriptor, stream capability, vectored read, and IO statistics interfaces.

Important APIs and types: implements `Seekable`, `PositionedReadable`, `HasFileDescriptor`, `IOStatisticsSource`, and `StreamCapabilities`. Delegates positioned reads and vectored reads to the underlying `FSInputStream`/`PositionedReadable`.

Control flow: `getPos()` subtracts unread buffered bytes from the wrapped stream position. `seek()` rejects closed or negative positions, repositions within the current buffer when possible, otherwise invalidates the buffer and seeks the underlying stream. `skip()` is implemented as `seek(getPos()+n)`. Capability and stats methods probe/delegate to the inner stream.

State and persistence behavior: state is inherited buffering fields (`buf`, `pos`, `count`, `in`) plus underlying stream state. No persistence.

Dependencies and integration points: commonly used by filesystem open paths to add buffering while maintaining Hadoop stream contracts and vector I/O.

Risks: vectored read methods cast `in` to `PositionedReadable`, so construction with a non-positioned `FSInputStream` would fail at runtime for those methods. `skip(n)` returns `n` after seek and may report skipped bytes even if the underlying seek past EOF later behaves differently. Buffer-aware seek logic depends on accurate underlying `getPos()`.

Test signals: verify seek within buffer vs outside buffer, negative seek, closed stream errors, `getPos()` after buffered reads, positioned/vectored delegation, file descriptor passthrough, capabilities, and IO statistics retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BufferedFSInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BulkDelete.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BulkDelete.java

Purpose: unstable public API for deleting batches of files or objects, especially object-store keys, without promising atomicity or directory marker preservation.

Important APIs and types: extends `IOStatisticsSource` and `Closeable`; exposes `pageSize()`, `basePath()`, and `bulkDelete(Collection<Path>)` returning failed path/message entries.

Control flow: no implementation. Contract requires submitted paths to be absolute, under `basePath`, no more than `pageSize`, and files/objects rather than directories.

State and persistence behavior: implementations may hold store clients/statistics and must be closed to release resources and update IO statistics. Deletions persist in the backing filesystem/object store.

Dependencies and integration points: created by `BulkDeleteSource`; callers can use `BulkDeleteUtils` for validation; support should be advertised through `CommonPathCapabilities.BULK_DELETE`.

Risks: non-atomic and idempotent semantics mean retries can delete newly created objects at the same keys. Large batches can stress object-store write IOPS. Directories are unsupported with undefined outcomes.

Test signals: implementation tests should cover page-size enforcement, base-path validation, partial failures, retry/idempotency behavior, statistics close behavior, and directory inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BulkDelete.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BulkDeleteSource.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BulkDeleteSource.java

Purpose: optional filesystem extension for creating path-scoped `BulkDelete` operations.

Important APIs and types: single `createBulkDelete(Path)` method, throwing unsupported, illegal argument, or IO exceptions depending on support and path resolution.

Control flow: interface only. Implementations typically resolve the path and return a delete object without performing network deletion at creation time.

State and persistence behavior: none in the interface. Returned `BulkDelete` instances own any operation state.

Dependencies and integration points: paired with `BulkDelete` and `CommonPathCapabilities.BULK_DELETE`.

Risks: implementing this interface is not sufficient by itself; callers are expected to rely on successful object creation and capability probing. Path validation and symlink resolution are implementation-dependent.

Test signals: verify capability advertisement, unsupported paths, invalid paths, symlink/path resolution, and that creation itself avoids delete side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BulkDeleteSource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BulkDeleteUtils.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BulkDeleteUtils.java

Purpose: small helper class centralizing client-side validation for bulk delete path collections.

Important APIs and types: `validateBulkDeletePaths(Collection<Path>, int, Path)` checks non-null collection, page-size upper bound, absolute paths, and parent containment. `validatePathIsUnderParent(Path, Path)` walks ancestors until the base path is found.

Control flow: validation uses `requireNonNull` and Hadoop `Preconditions.checkArgument`; per-path checks are applied with `forEach`.

State and persistence behavior: stateless utility, no persistence.

Dependencies and integration points: used by `BulkDelete` implementations or callers before submitting batches.

Risks: base path null is not explicitly checked; containment relies on `Path.equals` and does not canonicalize schemes, authorities, dot segments, symlinks, or case. It permits deleting the base path itself.

Test signals: cover null collection, page overflow, relative paths, exact base path, nested descendants, sibling paths with similar prefixes, qualified vs unqualified paths, and null base path behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BulkDeleteUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ByteBufferPositionedReadable.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ByteBufferPositionedReadable.java

Purpose: evolving stream interface for positioned reads into a `ByteBuffer`, including a read-fully variant.

Important APIs and types: `read(long position, ByteBuffer buf)` returns bytes read or EOF; `readFully(long position, ByteBuffer buf)` fills the remaining buffer or throws `EOFException`.

Control flow: interface only. Contract says reads must not change the stream's current offset, should be thread-safe, must advance buffer position on success, and must treat zero-length requests as valid.

State and persistence behavior: no interface state. Implementations read from the underlying file without modifying the sequential stream cursor.

Dependencies and integration points: complements `PositionedReadable`, `ByteBufferReadable`, and `StreamCapabilities.PREADBYTEBUFFER`.

Risks: buffer state after exceptions is undefined. Callers must probe capability before downcasting or invoking.

Test signals: implementation tests should cover zero-length reads, EOF returns vs `EOFException`, buffer position/limit changes, thread-safety, current-position preservation, and direct vs heap buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ByteBufferPositionedReadable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ByteBufferReadable.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ByteBufferReadable.java

Purpose: evolving stream interface for sequential reads into a `ByteBuffer` instead of a byte array.

Important APIs and types: single `read(ByteBuffer buf)` method with standard read return values and buffer position advancement.

Control flow: interface only. Contract leaves buffer state undefined on exception and requires zero-length requests to be accepted.

State and persistence behavior: no interface state; implementations advance the underlying stream position as a sequential read.

Dependencies and integration points: used by `FSDataInputStream`, zero-copy/fallback code, and capability `StreamCapabilities.READBYTEBUFFER`.

Risks: callers must check capability; unsupported streams can throw. Exception handling must assume partial buffer mutation.

Test signals: implementation tests should cover heap/direct buffers, empty buffers, EOF, partial reads, exception buffer state expectations, and capability advertisement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ByteBufferReadable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ByteBufferUtil.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ByteBufferUtil.java

Purpose: private helper for fallback reads when zero-copy reads are unavailable, using a `ByteBufferPool`.

Important APIs and types: `fallbackRead(InputStream, ByteBufferPool, int)` allocates direct buffers when the stream supports true byte-buffer reads and heap buffers otherwise. `streamHasByteBufferRead` avoids treating `FSDataInputStream` wrapper support as sufficient unless the wrapped stream also implements `ByteBufferReadable`.

Control flow: validate pool and allocated buffer; choose directness; cap requested length to capacity. For direct/byte-buffer-readable streams, loop until max length or EOF, then flip. For heap fallback, read once into the backing array and set the limit. On error or EOF without data, return the buffer to the pool and return null.

State and persistence behavior: stateless. Buffer ownership transfers to the caller only on success; otherwise returned to the pool.

Dependencies and integration points: integrates with `ByteBufferPool`, `ByteBufferReadable`, `FSDataInputStream`, and zero-copy read paths.

Risks: heap fallback assumes `buffer.array()` is available; this is enforced indirectly by `useDirect=false` and pool compliance. Direct loop can spin if a buggy stream repeatedly returns zero before filling the buffer. Returning null at EOF must be handled by callers.

Test signals: cover null pool, pool returning null, direct vs heap allocation validation, EOF before data, partial EOF after data, buffer return on failure, zero-return stream behavior, and `FSDataInputStream` wrapping rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ByteBufferUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CachingGetSpaceUsed.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CachingGetSpaceUsed.java

Purpose: abstract base for disk-space-used estimators that cache usage and optionally refresh it in a background daemon thread.

Important APIs and types: implements `Closeable` and `GetSpaceUsed`; holds `AtomicLong used`, `AtomicBoolean running`, refresh interval, jitter, canonical directory path, and refresh thread. Subclasses implement `refresh()`. Public helpers include `getUsed`, `getDirPath`, `incDfsUsed`, `getRefreshInterval`, `getJitter`, and protected `setUsed`.

Control flow: construction canonicalizes the target path and seeds `used`. `init()` performs an immediate refresh when initial used is negative and first refresh is enabled, otherwise starts a `SubjectInheritingThread` if interval is positive. The refresh thread sleeps for interval plus random jitter, clamps to at least one millisecond, then invokes `refresh()` until `running` is false. `close()` flips running false and interrupts the thread.

State and persistence behavior: cached usage lives in memory and can be adjusted optimistically by `incDfsUsed`. Actual persistence is external filesystem state measured by subclass `refresh()`.

Dependencies and integration points: used by HDFS/MapReduce storage accounting; builder values come from `GetSpaceUsed` construction paths and common filesystem space-used configuration keys.

Risks: `refresh()` exceptions other than `InterruptedException` are not caught inside the loop, so subclass runtime exceptions can kill the background thread. Jitter uses `nextLong(-jitter, jitter)`, excluding the positive upper bound. `close()` does not join the thread, so immediate post-close assertions can race.

Test signals: cover initial negative usage behavior, interval zero disabling the thread, jitter bounds, `incDfsUsed`, non-negative `getUsed`, close/interrupt behavior, subject inheritance, and subclass refresh failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CachingGetSpaceUsed.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CanSetDropBehind.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CanSetDropBehind.java

Purpose: evolving stream capability interface for toggling drop-behind cache behavior.

Important APIs and types: `setDropBehind(Boolean dropCache)` accepts true/false or null to restore/default behavior, and may throw `IOException` or `UnsupportedOperationException`.

Control flow: interface only; stream implementations decide how to pass hints to OS/filesystem clients.

State and persistence behavior: no interface state. Implementations may mutate per-stream caching hints, not file contents.

Dependencies and integration points: used by streams exposed through `FSDataInputStream`/`FSDataOutputStream` and capability/probe paths.

Risks: null semantics and support vary by stream. Callers should handle unsupported operations even if the stream type is known.

Test signals: implementation tests should cover true, false, null, post-close calls, unsupported streams, and propagation to the underlying native/client cache hint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CanSetDropBehind.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CanSetReadahead.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CanSetReadahead.java

Purpose: evolving stream capability interface for setting per-stream readahead.

Important APIs and types: `setReadahead(Long readahead)` accepts byte count or null for default and may throw `IOException` or `UnsupportedOperationException`.

Control flow: interface only; implementations update stream/client read-ahead hints.

State and persistence behavior: no interface state. Effects are transient stream configuration.

Dependencies and integration points: used by Hadoop stream wrappers and callers tuning sequential/remote reads.

Risks: negative values, null, and post-close behavior are implementation-defined unless validated by concrete streams. Documentation typo mentions dropBehind in the IOException text.

Test signals: implementation tests should cover positive values, zero, null/default reset, invalid negative values, unsupported streams, and actual read path hint propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CanSetReadahead.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CanUnbuffer.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CanUnbuffer.java

Purpose: evolving interface for streams that can release buffers, sockets, or file descriptors on request.

Important APIs and types: single `unbuffer()` method.

Control flow: interface only; implementations free transient resources and may lazily reacquire them on later reads.

State and persistence behavior: no interface state; implementation state is transient resource ownership.

Dependencies and integration points: implemented by `FSDataInputStream` wrappers and remote filesystem streams to reduce idle resource pressure.

Risks: callers may assume unbuffer is harmless, but implementations must preserve subsequent read correctness. No checked exception is declared, so failures are typically runtime or logged.

Test signals: implementation tests should call `unbuffer()` before reads, after partial reads, after close, multiple times, and verify later seek/read behavior plus resource release metrics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CanUnbuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ChecksumException.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ChecksumException.java

Purpose: stable public `IOException` subtype indicating a checksum mismatch or malformed checksum data at a file position.

Important APIs and types: constructor stores a description and long position; `getPos()` returns the position.

Control flow: simple exception data holder.

State and persistence behavior: serializable exception state includes message and position; no persistence.

Dependencies and integration points: thrown by `FSInputChecker`, `ChecksumFileSystem`, `ChecksumFs`, and checksum-aware streams.

Risks: position can be any caller-supplied long; code catching generic `IOException` may lose checksum-specific diagnostics unless it checks this type.

Test signals: verify message, position, serialization compatibility, and propagation through checksum read paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ChecksumException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ChecksumFileSystem.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ChecksumFileSystem.java

Purpose: `FileSystem` wrapper that provides client-side CRC32 checksums by creating and verifying hidden sibling `.crc` files alongside raw data files.

Important APIs and types: extends `FilterFileSystem`; `getChecksumFile`, `isChecksumFile`, `getChecksumFileLength`, `getBytesPerSum`, `setVerifyChecksum`, `setWriteChecksum`, `open`, `create`, `createNonRecursive`, `rename`, `delete`, filtered listing methods, and `reportChecksumFailure`. Internal `ChecksumFSInputChecker` extends `FSInputChecker`; `ChecksumFSOutputSummer` extends `FSOutputSummer`; `FSDataBoundedInputStream` prevents seeking/skipping past EOF.

Control flow: configuration loads local bytes-per-checksum and validates it positive. `open()` uses `ChecksumFSInputChecker` when verification is enabled, otherwise opens raw data, then wraps in a bounded stream. The input checker opens the data stream and corresponding `.crc` file, validates the `crc\0` header and bytes-per-sum, and reads checksum chunks aligned to data chunks; missing checksum files disable checksum validation. Vectored reads validate checksum ranges by reading both data and `.crc` ranges and combining futures. `create()` ensures parents, writes data through `ChecksumFSOutputSummer`, and creates the checksum file with header and per-chunk CRCs; when checksum writing is disabled it deletes any stale checksum file. Metadata operations such as permission, owner, ACL, and replication are applied to the data file and then the checksum file when present. Rename and delete keep checksum siblings in sync. Listings filter out checksum files.

State and persistence behavior: persistent state is in the raw filesystem as paired data files and hidden `.crc` files. Runtime state includes `bytesPerChecksum`, `verifyChecksum`, and `writeChecksum`; stream classes hold open data/checksum streams and checksum buffers.

Dependencies and integration points: uses raw `FileSystem`, `FilterFileSystem`, `FSInputChecker`, `FSOutputSummer`, `DataChecksum`, `CRC32`, `FileUtil`, ACL/permission classes, vectored read utilities, IO statistics, and stream capability plumbing.

Risks: checksum/data operations are not atomic across sibling files, so rename, delete, create, and metadata updates can leave stale or missing `.crc` files after partial failure. Missing checksum files silently disable validation except for warning cases. Append, truncate, and concat are unsupported. Vectored checksum validation has complex buffer slicing and EOF adjustment behavior. Default checksum file filtering can hide files whose names match `.x.crc` even if user-created.

Test signals: cover checksum file naming and length math, read validation success/failure, missing or corrupt checksum headers, positioned reads, vectored reads with partial final chunks, create with and without checksum writing, stale checksum deletion, metadata propagation, rename/delete failure cases, listing filters, `hasPathCapability`, and unsupported append/truncate/concat.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ChecksumFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ChecksumFs.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ChecksumFs.java

Purpose: `AbstractFileSystem`/`FileContext` counterpart to `ChecksumFileSystem`, wrapping an `AbstractFileSystem` with client-side `.crc` file generation and verification.

Important APIs and types: extends `FilterFs`; exposes `getRawFs`, `getChecksumFile`, `isChecksumFile`, `getChecksumFileLength`, `getBytesPerSum`, `open`, `createInternal`, `setReplication`, `renameInternal`, `delete`, `listStatus`, `listLocatedStatus`, and `reportChecksumFailure`. Internal `ChecksumFSInputChecker` and `ChecksumFSOutputSummer` mirror the `FileSystem` implementation.

Control flow: constructor reads default bytes-per-checksum from raw FS server defaults. Open creates a checksum input checker that reads the raw data stream and corresponding checksum stream, validates header and chunk size, and verifies CRC32 chunks. Create builds data and checksum outputs through raw `createInternal`, writing checksum header and chunk CRCs. Rename/delete/setReplication coordinate data file and checksum file operations. Listings filter checksum files from array and iterator results.

State and persistence behavior: persistent state is raw FS data plus hidden `.crc` siblings. Runtime state includes `defaultBytesPerChecksum`, `verifyChecksum`, and stream-local data/checksum handles.

Dependencies and integration points: integrates with `AbstractFileSystem`, `FilterFs`, `FileContext` flows, `FSInputChecker`, `FSOutputSummer`, `DataChecksum`, permissions, `CreateFlag`, and `ChecksumOpt`.

Risks: same paired-file non-atomicity as `ChecksumFileSystem`. It has no write-checksum disable knob and lacks the newer vectored read and builder overrides present in `ChecksumFileSystem`. `seekToNewSource` assumes `sums` is non-null; missing checksum behavior plus source switching should be tested. Raw FS implementations that already checksum internally can lead to layered checksumming.

Test signals: cover raw server-default checksum size, create/read verification, missing checksum file, corrupt checksum file, rename overwrite/non-overwrite, directory vs file delete, listing filters, replication propagation, EOF seek/skip bounds, and source switching on checksum failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ChecksumFs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ClosedIOException.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ClosedIOException.java

Purpose: unstable public `PathIOException` subtype for operations attempted against a closed stream, cache, or closable resource.

Important APIs and types: constructor accepts path string and custom message, delegating to `PathIOException`.

Control flow: exception data holder only.

State and persistence behavior: exception state is path and message; no persistence.

Dependencies and integration points: used by filesystem code that wants path-aware diagnostics for closed resources.

Risks: only provides one constructor; callers needing a cause must use another exception type or wrapping.

Test signals: verify path/message formatting from `PathIOException`, serialization behavior, and use in closed-resource code paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ClosedIOException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ClusterStorageCapacityExceededException.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ClusterStorageCapacityExceededException.java

Purpose: evolving public `IOException` used by HDFS and related clients to signal cluster-wide storage capacity exhaustion.

Important APIs and types: standard no-arg, message, message-plus-cause, and cause constructors.

Control flow: exception type only.

State and persistence behavior: standard exception message/cause state; no persistence.

Dependencies and integration points: raised by storage allocation/write paths and observed by MapReduce/HDFS clients for capacity-specific handling.

Risks: callers catching generic `IOException` may not distinguish quota/capacity failures. No extra structured fields identify cluster, storage type, or remaining capacity.

Test signals: verify constructor message/cause combinations and propagation through write/allocation failure paths that need capacity-specific behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ClusterStorageCapacityExceededException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CommonConfigurationKeys.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CommonConfigurationKeys.java

Purpose: private unstable extension of `CommonConfigurationKeysPublic` adding internal or less-public Hadoop common configuration key constants and defaults.

Important APIs and types: class of `public static final` constants for filesystem home/umask, IPC ping/RPC/server limits/callqueue settings, compression buffers/codecs, service authorization ACLs, token service DNS behavior, HA health monitor/failover controller timeouts, HTTP static user and Jetty alias serving, Kerberos ticket cache, async IPC limits, ZooKeeper client settings including SSL, domain-name resolver implementation, KMS URI selection, JVM metrics options, IOStatistics logging/thread-level settings, temp dir, security resolver, and local filesystem checksum verification.

Control flow: no executable logic beyond class initialization of constants and imported default classes such as `StaticUserWebFilter`, `DomainNameResolver`, and `DNSDomainNameResolver`.

State and persistence behavior: constants only. Values become effective when other components read matching keys from `Configuration`; this file itself stores no runtime state.

Dependencies and integration points: inherited by broad Hadoop common, IPC, security, HA, metrics, ZooKeeper, filesystem, compression, and local FS code. Extends the public constants class so consumers often import this one for both public and internal keys.

Risks: string constants are compatibility surface even when marked private; changing names/defaults can break deployed configs. Some constants are ACL/security-sensitive and default choices affect exposure. Deprecated or duplicated names can cause migration confusion.

Test signals: configuration tests should assert defaults match `core-default.xml`, deprecated aliases still map as expected, sensitive/security keys are honored, and components consuming these constants use the intended defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CommonConfigurationKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CommonConfigurationKeysPublic.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CommonConfigurationKeysPublic.java

Purpose: public constant registry for documented Hadoop common configuration keys and defaults, generally mirroring `core-default.xml`.

Important APIs and types: exposes filesystem defaults (`fs.defaultFS`, df/du intervals, trash, file implementation, creation parallelism), topology mapping keys, IO and sequence/TFile tuning, caller context, IPC client/server networking and slow RPC settings, socket factory and SOCKS proxy, group mapping/cache/authentication/security keys, crypto codec defaults for AES and SM4 CTR, KMS client cache/failover settings, secure random and credential provider keys, sensitive config redaction regexes, tags, shutdown timeout, Prometheus/JMX/HTTP metrics settings, and server metrics runner interval.

Control flow: no methods; class initialization builds some default strings from imported crypto codec classes and `CipherSuite` suffixes, and builds the sensitive-config regex list with `String.join`.

State and persistence behavior: constants only. Configuration persistence lives in XML/configuration files and consumers.

Dependencies and integration points: imported throughout Hadoop common, HDFS, MapReduce, security, crypto, KMS, IPC, HTTP, metrics, and filesystem components. `CommonConfigurationKeys` extends this class for internal additions.

Risks: as a public class, constants are API compatibility. Defaults affect cluster behavior, security posture, performance, and backward compatibility. The sensitive config default includes a self-reference constant name string, so consumers must understand it as a redaction pattern list rather than resolving recursively.

Test signals: verify constants align with `core-default.xml`, public deprecations remain available, crypto codec defaults instantiate in expected order, sensitive-key redaction catches cloud and credential patterns, and changed defaults have migration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CommonConfigurationKeysPublic.java -->
