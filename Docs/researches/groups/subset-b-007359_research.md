<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/TFile.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/TFile.java

## Purpose
`TFile` is Hadoop's byte-oriented sorted or unsorted key/value container built on `BCFile`. It exposes public `Writer` and `Reader` APIs for appending records, writing named metadata blocks, scanning by full file, byte range, key range, or record number, and retrieving TFile metadata/index structures. Keys are raw bytes limited to 64 KiB; values are raw bytes with chunked encoding so large values do not need full buffering.

## Important APIs and Types
Top-level constants define supported compression names (`gz`, `lzo`, `none`), comparator names (`memcmp`, `jclass:`), `API_VERSION`, and configuration keys for chunk and filesystem buffering. `Writer` owns `prepareAppendKey`, `prepareAppendValue`, `append`, `prepareMetaBlock`, and `close`. `Reader` owns metadata access, comparator access, `getFirstKey`, `getLastKey`, `getKeyNear`, record-number mapping, and scanner creation. `Reader.Scanner` owns cursor movement (`advance`, `rewind`, `seekToEnd`, `lowerBound`, `upperBound`) and `Scanner.Entry` owns key/value extraction and comparison. Internal persisted metadata is modeled by `TFileMeta`, `TFileIndex`, and `TFileIndexEntry`.

## Control Flow
Writing is a strict state machine: `READY -> IN_KEY -> END_KEY -> IN_VALUE -> READY`, with `CLOSED` terminal. A key stream close writes a varint key length and key bytes, checks sorted order when a comparator is configured, and records first/last keys. A value stream close finalizes chunk encoding, increments per-block and whole-file record counts, and may close the current BCFile data block once compressed size reaches the configured minimum. `close` forces the last data block closed, writes `TFile.meta`, writes `TFile.index`, then closes/cleans BCFile resources.

Reading constructs a `BCFile.Reader`, loads `TFile.meta`, and lazily loads `TFile.index` on first indexed operation. Scanners convert byte/key/record ranges into `Location(blockIndex, recordIndex)` bounds. Cursor movement opens data blocks on demand, parses each key length/key/value chunk decoder, and consumes value streams before skipping to the next record. Sorted-key seeks binary-search the block index, then scan within the candidate block.

## State and Persistence
Persistent state lives in BCFile data blocks plus two TFile metadata blocks. `TFile.meta` stores version, total record count, and comparator name. `TFile.index` stores the first key, then one `TFileIndexEntry` per data block containing that block's last key and record count. In-memory reader state includes the lazy index, reusable key/value buffers, current block reader, and scanner bounds. `Scanner.Entry` values are single-use because the value stream is not cached.

## Dependencies and Integration Points
The class integrates with `BCFile`, `Chunk`, `CompareUtils`, Hadoop `FSDataInputStream`/`FSDataOutputStream`, Hadoop raw comparators, `BytesWritable`, `DataInputBuffer`, `DataOutputBuffer`, and Java serialization comparators by class name. Configuration keys control chunk buffer size and TFile-layer I/O buffering. The `main` method delegates to `TFileDumper`.

## Risks and Edge Cases
Writer errors increment `errorCount`; after an append failure the writer is intentionally inconsistent and close only cleans resources. Sorted files rely on comparator correctness and default constructor availability for `jclass:` comparators. Scanners throw if values are examined multiple times. Key lengths from corrupt files can exceed the fixed 64 KiB scanner buffer. Multi-threaded reading shares seek/read behavior in the underlying stream and is not designed for true parallel scanner I/O. Version compatibility only checks major version.

## Test Signals
Useful tests should cover append state errors, sorted-order enforcement, fixed and unknown value lengths, metadata block writing after data blocks, scanner ranges by byte/key/record, lower/upper-bound duplicate-key behavior, lazy index loading, corrupt/truncated varint/key/value handling, and comparator instantiation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/TFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/TFileDumper.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/TFileDumper.java

## Purpose
`TFileDumper` is a package-private diagnostics utility that opens a TFile and prints human-readable structural information: file versions, compression, record counts, block sizes, metadata overhead, per-data-block index entries, and per-meta-block regions.

## Important APIs and Types
The public surface is the static `dumpInfo(String file, PrintStream out, Configuration conf)` method. The nested `Align` enum formats table cells as left, center, right, or zero-padded numeric fields and calculates display widths.

## Control Flow
`dumpInfo` resolves the Hadoop `Path`, obtains file length and an `FSDataInputStream`, constructs a `TFile.Reader`, then collects properties from the underlying `BCFile.Reader` and `TFileMeta`. It totals compressed and raw data block sizes, totals meta block sizes, derives metadata-index/header sizes, prints the property table, forces the TFile data index loaded, and prints data-block and meta-block tables.

## State and Persistence
The utility does not mutate TFiles. It holds transient maps of formatted properties and uses reader internals such as `readerBCF.dataIndex`, `readerBCF.metaIndex`, and `reader.tfileIndex`. Streams and reader are cleaned in a `finally` block via `IOUtils.cleanupWithLogger`.

## Dependencies and Integration Points
It depends on Hadoop filesystem APIs, `TFile.Reader`, `BCFile.BlockRegion`, `BCFile.MetaIndexEntry`, `TFileIndexEntry`, `Compression.Algorithm`, and `Utils.Version`. It is invoked by `TFile.main` for command-line dumping.

## Risks and Edge Cases
The data block compression-ratio code divides by `dataSize` when compression is not `none`; malformed or empty compressed data metadata could make that unsafe. `Meta-Data Size Ratio` divides by `metaSize`, which should normally include required TFile metadata but is still a corrupt-file risk. The non-ASCII key dump loop reads `key[i]` instead of `key[j]`, so large block indexes or short keys can produce wrong hex output or an array bounds exception. It also samples UTF-8 bytes without validating full code-point boundaries.

## Test Signals
Tests should dump empty files, compressed and uncompressed files, files with user metadata blocks, non-ASCII/binary end keys, and malformed or edge metadata sizes. A targeted regression should exercise a binary key in a data block whose block index differs from the byte sample index.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/TFileDumper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/Utils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/Utils.java

## Purpose
`Utils` provides shared TFile utilities: compact variable-length integer encoding, nullable UTF-8 string encoding via Hadoop `Text`, a small version type, and lower/upper-bound binary-search helpers.

## Important APIs and Types
`writeVInt`, `writeVLong`, `readVInt`, and `readVLong` implement the TFile-specific signed variable-length integer format. `writeString` and `readString` serialize nullable strings as a VInt byte length followed by `Text` bytes. `Version` stores major/minor shorts, serializes to four bytes, compares versions, and considers versions compatible when majors match. Overloaded `lowerBound` and `upperBound` methods operate on comparator-backed and comparable lists.

## Control Flow
`writeVLong` emits one byte for values in `[-32, 127)`, then progressively larger encodings based on the sign-extended high byte range, falling through switch cases to choose two-, three-, four-, or fixed-length forms. `readVLong` decodes from the first byte range and reads the required trailing bytes. Binary search helpers use standard half-open `[low, high)` loops.

## State and Persistence
The class is stateless. Its encodings are persistent on-disk contracts used by TFile metadata/index and record streams, so changes would be format-breaking unless versioned.

## Dependencies and Integration Points
`TFile`, `BCFile`, and related TFile code use these methods for record lengths, index entries, metadata strings, and version compatibility. It depends only on `DataInput`, `DataOutput`, `Text`, `Comparator`, and `List`.

## Risks and Edge Cases
`readVInt` throws a runtime exception if the decoded long does not fit in an int. Corrupt first bytes can produce `IOException` or runtime internal errors. String decoding trusts the serialized length and may allocate large buffers for corrupt inputs. `Version.hashCode` shifts a signed short-derived major value, which is acceptable for equality but not a stable format hash. Binary search helpers assume sorted input according to the same comparator used for lookup.

## Test Signals
High-value tests include round trips for every integer encoding boundary, negative values, max/min int and long ranges, corrupt first-byte forms, nullable and non-ASCII strings, version compatibility/ordering, and binary searches over empty, duplicate, and boundary-key lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/Utils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/Errno.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/Errno.java

## Purpose
`Errno` is a Java enum mirror of POSIX errno categories used by Hadoop native I/O wrappers to expose native failures in a platform-neutral Java exception type.

## Important APIs and Types
The enum values include common filesystem and process errors such as `EPERM`, `ENOENT`, `EACCES`, `EEXIST`, `ENOSPC`, `ENOTEMPTY`, `EOVERFLOW`, and a fallback `UNKNOWN`.

## Control Flow
There is no runtime control flow in this file. Native code and wrapper methods select enum constants when constructing `NativeIOException`.

## State and Persistence
The enum is immutable and has no persistent state. Its ordering can matter if JNI code maps numeric errno values by ordinal, so adding or reordering values would be risky unless native mapping is name-based.

## Dependencies and Integration Points
`NativeIOException`, `NativeIO`, and callers such as secure file creation use it to detect specific conditions like `EEXIST` and translate them into Hadoop exceptions.

## Risks and Edge Cases
The list is not exhaustive for every POSIX platform. Unsupported native errno values must degrade to `UNKNOWN`, which can reduce caller-specific handling. Windows error codes do not use this enum directly except as a generic fallback.

## Test Signals
Tests should verify JNI/native mappings for representative errno values, fallback to `UNKNOWN`, and caller behavior for `EEXIST`, `ENOENT`, `EBADF`, and permission-related errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/Errno.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/NativeIO.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/NativeIO.java

## Purpose
`NativeIO` centralizes JNI-backed filesystem, memory, cache, and platform-specific I/O operations that Java did not historically expose directly. It provides POSIX wrappers, Windows wrappers, persistent-memory helpers, owner/stat lookup, secure file creation, rename/link/copy helpers, and fallbacks when native code is unavailable.

## Important APIs and Types
`NativeIO.POSIX` exposes open/stat/chmod/fadvise/sync_file_range/mlock/mmap/munmap, PMDK support state, `Pmem`, `PmemMappedRegion`, `CacheManipulator`, and `Stat`. `NativeIO.Windows` exposes CreateFile-style constants, file/directory creation with mode, share-delete descriptors, access checks, and working-set extension. Top-level methods include `isAvailable`, `getOwner`, `getShareDeleteFileDescriptor`, `getCreateForWriteFileOutputStream`, `renameTo`, `link`, and `copyFileUnbuffered`.

## Control Flow
Three static initialization paths attempt JNI initialization: POSIX nested initialization, Windows nested initialization, and top-level initialization. They check `NativeCodeLoader.isNativeCodeLoaded`, call native init methods, set `nativeLoaded`, and log advisory diagnostics on failure. POSIX operations generally check native support, translate Windows-specific errors where needed, and cache capability fallbacks when native symbols are missing. File creation chooses POSIX `open(O_CREAT|O_EXCL)` or Windows `CreateFile(CREATE_NEW)`. `copyFileUnbuffered` uses a native Windows path when possible and otherwise loops `FileChannel.transferTo` until all bytes are copied.

## State and Persistence
Static state includes native-loaded flags, fadvise/sync-file-range capability booleans, PMDK support state, configurable UID/group name cache timeouts, concurrent ID/name caches, and a lazily initialized top-level UID cache. Persistent effects include chmod, file creation, directory creation, hard links, rename, mmap/pmem mapping, unbuffered copy, cache hints, and memory locking.

## Dependencies and Integration Points
The class integrates with Hadoop `NativeCodeLoader`, `Shell`, `CommonConfigurationKeys`, `HardLink`, `PathIOException`, `SecureIOUtils.AlreadyExistsException`, `CleanerUtil`, and `PerformanceAdvisory`, plus JDK `FileDescriptor`, channels, direct buffers, `Unsafe`, and platform JNI implementations in libhadoop.

## Risks and Edge Cases
Native and nested `nativeLoaded` flags are separate; callers must use the right availability check for the operation. Some fallbacks silently no-op after `UnsatisfiedLinkError` or `UnsupportedOperationException`, which avoids crashes but can hide missing OS optimizations. `getShareDeleteFileDescriptor` on non-Windows creates a `RandomAccessFile` and returns only its descriptor, making lifecycle ownership subtle. `copyFileUnbuffered` can spin if `transferTo` returns zero while bytes remain. UID cache configuration is read lazily and separately from POSIX cache configuration. `sun.misc.Unsafe` and manual unmap remain portability risks.

## Test Signals
Tests should run with native code available and unavailable, POSIX and Windows-specific mappings, secure create existing-file translation, chmod/stat owner lookup, fadvise/sync fallback disablement, direct and non-direct mlock, unmap unsupported paths, hard-link fallback, `transferTo` partial-copy loops, and PMDK support-state messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/NativeIO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/NativeIOException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/NativeIOException.java

## Purpose
`NativeIOException` wraps errors returned by Hadoop native I/O calls. On POSIX it carries an `Errno`; on Windows it carries a raw system error code.

## Important APIs and Types
Constructors accept `(String msg, Errno errno)` or `(String msg, int errorCode)`. Accessors `getErrno` and `getErrorCode` expose the platform-specific payload. `toString` selects error-code formatting on Windows and errno formatting elsewhere.

## Control Flow
The class has no complex flow. Callers choose the constructor that matches platform/native failure information, and downstream code inspects either `Errno` or integer error code.

## State and Persistence
Instances are serializable as `IOException` subclasses, with `serialVersionUID = 1L`. The POSIX constructor initializes Windows error code to success `0`; the Windows constructor initializes errno to `UNKNOWN`.

## Dependencies and Integration Points
It is used throughout `NativeIO` to translate JNI failures into Java exceptions and by callers that branch on `EEXIST`, Windows `ERROR_FILE_EXISTS`, invalid-handle codes, and similar conditions. It depends on `Shell.WINDOWS` for formatting.

## Risks and Edge Cases
`getErrorCode` returns `long` but stores an `int`; unsigned 32-bit Windows codes above `Integer.MAX_VALUE` are represented as signed values internally. Formatting is based on the current runtime OS rather than which constructor was used, so cross-platform serialized inspection may be confusing.

## Test Signals
Tests should verify POSIX and Windows constructor payloads, string formatting under platform conditions, and caller translations for representative errno/error-code values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/NativeIOException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/SharedFileDescriptorFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/SharedFileDescriptorFactory.java

## Purpose
`SharedFileDescriptorFactory` creates readable/writable file descriptors backed by temporary files in a configured directory, normally `/dev/shm` or `/tmp`, and unlinks those files so descriptors can be shared across processes without leaving durable paths.

## Important APIs and Types
`getLoadingFailureReason` reports why the factory cannot run. `create(String prefix, String[] paths)` probes candidate directories and returns the first usable factory. `getPath` reports the selected directory. `createDescriptor(String info, int length)` returns a `FileInputStream` wrapping a native-created descriptor. Native methods delete stale temp files and create exclusive resized descriptors.

## Control Flow
Creation first requires `NativeIO.isAvailable()` and a Unix OS. It rejects empty path lists, then tries each path by creating and closing a small test descriptor. On success it deletes stale files matching the prefix and returns a factory. On failure it accumulates per-path error messages and throws one combined `IOException`.

## State and Persistence
Factory instances store only `prefix` and `path`. Persistent side effects are native temporary file creation, unlinking, stale-file cleanup, and descriptor length setting. Files should normally disappear after unlink even if the JVM exits later.

## Dependencies and Integration Points
It depends on `NativeIO`, Apache Commons `SystemUtils.IS_OS_UNIX`, Java `FileDescriptor`/`FileInputStream`, and native libhadoop implementations. It is intended for subsystems that need shared memory-like descriptors.

## Risks and Edge Cases
Availability is Unix-only and native-code-only. Cleanup is prefix-based and implemented natively; a bad prefix/path pairing could delete unintended stale files if native filtering is wrong. Crashes between create and unlink are the exact failure mode the constructor cleanup tries to address. Returned `FileInputStream` owns descriptor closure.

## Test Signals
Tests should cover unavailable native code, non-Unix rejection, empty path lists, first-path failure with later-path success, aggregate errors, stale cleanup invocation, descriptor length, and descriptor cleanup after close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/SharedFileDescriptorFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/package-info.java

## Purpose
`package-info.java` documents and annotates the `org.apache.hadoop.io.nativeio` package as Hadoop-private and unstable.

## Important APIs and Types
The file applies package-level `@InterfaceAudience.Private` and `@InterfaceStability.Unstable` annotations.

## Control Flow
There is no executable control flow.

## State and Persistence
There is no runtime or persistent state. Its effect is metadata for API classification and generated documentation.

## Dependencies and Integration Points
It imports Hadoop classification annotations and applies them to all native I/O package documentation.

## Risks and Edge Cases
The package-level classification signals that downstream users should not depend on API stability. If public usage grows, changes in this package can still break external consumers despite the annotation.

## Test Signals
No functional tests are needed; source or doc checks can verify package annotations remain present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/AsyncCallHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/AsyncCallHandler.java

## Purpose
`AsyncCallHandler` adapts `RetryInvocationHandler` to Hadoop RPC asynchronous mode. It stores lower-layer async returns in thread-locals, tracks outstanding async retry calls, polls them on a daemon processor, and exposes an `AsyncGet` to the original caller.

## Important APIs and Types
Static APIs are `getAsyncReturn` and `setLowerLayerAsyncReturn`. Internal types include `ConcurrentQueue`, `AsyncCallQueue`, `AsyncCallQueue.Processor`, `AsyncValue`, and `AsyncCall`, which extends `RetryInvocationHandler.Call`.

## Control Flow
When a retry proxy is invoked in asynchronous mode, `RetryInvocationHandler` creates an `AsyncCall`. `AsyncCall.invoke` temporarily enables lower-level RPC async mode, calls the target method, expects a null direct result plus a lower-layer `AsyncGet`, and registers itself on first attempt. The processor daemon repeatedly calls `checkCalls`, removes completed calls, computes the next wait period, and sleeps on the handler monitor. `AsyncCall.isDone` advances the retry state machine: complete returns/exceptions set `AsyncValue`, retries are invoked again, and wait/in-progress states stay queued.

## State and Persistence
State is in thread-local async returns, a concurrent call queue, an atomic processor thread reference, per-call lower-layer async handle, `AsyncValue<CallReturn>`, and a `hasSuccessfulCall` flag used by logging. There is no persistent state.

## Dependencies and Integration Points
It integrates with Hadoop `Client` asynchronous mode and call-id propagation, `Daemon`, `Time`, `AsyncGet`, `Preconditions`, and `RetryInvocationHandler.Call`.

## Risks and Edge Cases
Thread-local returns must be consumed exactly once; missing lower-layer async values fail preconditions. `AsyncValue.set` forbids setting a completed call twice. The processor stop logic depends on queue-empty grace timing and monitor waits, so missed notifications could add up to the max wait period. The `RETRY` state in `isDone` invokes once immediately after processing retry info, which can make state transitions dense. `hasSuccessfulCall` is set when async `get` succeeds, not when lower-layer work finishes.

## Test Signals
Tests should cover successful async calls, delayed lower-layer completion, retry with wait, failover under async mode, exception propagation from `AsyncGet`, timeout behavior, daemon start/stop grace period, and thread-local cleanup after retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/AsyncCallHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/AtMostOnce.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/AtMostOnce.java

## Purpose
`AtMostOnce` marks RPC interface methods whose server side guarantees duplicate suppression through a retry cache, allowing clients to retry after failover or uncertain network failures.

## Important APIs and Types
It is a runtime-retained, inherited method annotation targeted at `ElementType.METHOD` and marked `@InterfaceStability.Evolving`.

## Control Flow
`RetryInvocationHandler.ProxyDescriptor.idempotentOrAtMostOnce` reflects on the provider interface method and passes the annotation result to `RetryPolicy.shouldRetry`.

## State and Persistence
The annotation has no fields. Its runtime metadata affects retry behavior but stores no mutable state.

## Dependencies and Integration Points
It is paired with `Idempotent` in retry/failover safety checks and is consumed by `FailoverOnNetworkExceptionRetry` to decide whether socket/IO failures may fail over and retry.

## Risks and Edge Cases
Correctness depends on the server actually maintaining a retry cache and returning prior responses for duplicates. Misannotation can turn uncertain side-effecting calls into repeated operations or, conversely, prevent safe retry if omitted.

## Test Signals
Tests should verify reflection through proxy interfaces, retry policy input flags, duplicate request behavior in servers with retry cache, and failover decisions for methods with and without the annotation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/AtMostOnce.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/CallReturn.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/CallReturn.java

## Purpose
`CallReturn` is the internal result envelope for one retry invocation attempt. It distinguishes returned values, thrown exceptions, retry scheduling states, and async in-progress states without throwing immediately through the retry loop.

## Important APIs and Types
The `State` enum includes `RETURNED`, `EXCEPTION`, `RETRY`, `WAIT_RETRY`, `ASYNC_CALL_IN_PROGRESS`, and `ASYNC_INVOKED`. Static singleton instances represent non-value states. Constructors wrap successful return values or throwables. `getReturnValue` rethrows stored exceptions and asserts returned state.

## Control Flow
`RetryInvocationHandler.Call.invokeOnce` and `AsyncCallHandler.AsyncCall.isDone` switch on `State` to decide whether to return to the caller, retry, wait, or keep polling.

## State and Persistence
Each instance stores at most one return value or one throwable plus a state. Preconditions reject simultaneous value and throwable. No persistent state exists.

## Dependencies and Integration Points
It depends on Hadoop `Preconditions` and is tightly coupled to `RetryInvocationHandler` and `AsyncCallHandler`.

## Risks and Edge Cases
`getReturnValue` throws if called for retry/async states, so all callers must check state first. Null is a valid return value but indistinguishable from internal null storage except by state. Exception state stores `Throwable`, not only `Exception`, preserving broader failures.

## Test Signals
Tests should cover state transitions in synchronous and asynchronous calls, exception rethrow, null successful return values, and precondition failures for invalid state/value access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/CallReturn.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/DefaultFailoverProxyProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/DefaultFailoverProxyProvider.java

## Purpose
`DefaultFailoverProxyProvider` adapts a single implementation object to the `FailoverProxyProvider` interface for retry proxies that do not actually fail over to alternate backends.

## Important APIs and Types
The constructor stores the interface class and proxy object. `getInterface` returns the interface, `getProxy` returns a new `ProxyInfo` around the same proxy, `performFailover` is a no-op, and `close` stops the proxy through `RPC.stopProxy`.

## Control Flow
Retry proxies use this provider when callers pass a concrete implementation rather than a custom failover provider. Any policy action requesting failover will call `performFailover`, but the active proxy remains unchanged.

## State and Persistence
The provider stores only the proxy and interface references. No persistent state is written.

## Dependencies and Integration Points
It integrates with `RetryProxy`, `RetryInvocationHandler`, `FailoverProxyProvider`, and Hadoop IPC `RPC.stopProxy`.

## Risks and Edge Cases
Policies that return failover actions with this provider will retry the same backend, which may be intended for local retry but not high availability. `close` assumes `RPC.stopProxy` is appropriate for the wrapped object.

## Test Signals
Tests should verify stable proxy return, no-op failover, interface propagation for annotations, and close behavior for RPC and non-RPC proxy objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/DefaultFailoverProxyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/FailoverProxyProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/FailoverProxyProvider.java

## Purpose
`FailoverProxyProvider` defines how retry proxies obtain the current backend proxy and switch to another backend when retry policy chooses failover.

## Important APIs and Types
`ProxyInfo<T>` carries the proxy and a debug string, with `getString(methodName)` and `toString` helpers. Interface methods are `getProxy`, `performFailover`, and `getInterface`; the provider is also `Closeable`.

## Control Flow
`RetryInvocationHandler.ProxyDescriptor` calls `getProxy` during construction and after failover, calls `performFailover(currentProxy)` under synchronization, and uses `getInterface` to reflect `Idempotent`/`AtMostOnce` annotations on declared methods.

## State and Persistence
The interface does not define state, but implementations normally hold one or more backend proxies and current selection. No persistence is required by the contract.

## Dependencies and Integration Points
It integrates with `RetryPolicy`, `RetryInvocationHandler`, annotations, and Hadoop RPC client lifecycle management.

## Risks and Edge Cases
Implementations must be thread-safe enough for concurrent retry calls. `ProxyInfo.proxyInfo` may be null, so logging should tolerate it. `getInterface` must return the actual annotated interface, not only a generated proxy class, or retry safety checks will be wrong.

## Test Signals
Tests should cover provider failover sequencing, annotation lookup through `getInterface`, concurrent failover suppression, close propagation, and logging/debug strings for null and non-null proxy info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/FailoverProxyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/Idempotent.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/Idempotent.java

## Purpose
`Idempotent` marks interface methods that can safely be retried because repeated execution has the same effect as one execution.

## Important APIs and Types
It is a runtime-retained, inherited method annotation targeted at methods and classified as evolving.

## Control Flow
`RetryInvocationHandler` reflects this annotation and passes a boolean to `RetryPolicy.shouldRetry`. `FailoverOnNetworkExceptionRetry` uses the boolean to allow failover and retry for socket or uncertain IO failures.

## State and Persistence
The annotation has no elements and no mutable state.

## Dependencies and Integration Points
It is part of the retry package contract with `AtMostOnce`, `RetryPolicy`, and `FailoverProxyProvider`.

## Risks and Edge Cases
Misannotating a non-idempotent method can duplicate side effects. Omitting it can reduce availability because failover policies will fail uncertain network calls instead of retrying.

## Test Signals
Tests should verify runtime retention, inherited behavior on interface methods, interaction with failover-on-network policy, and behavior differences between annotated and unannotated methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/Idempotent.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/LossyRetryInvocationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/LossyRetryInvocationHandler.java

## Purpose
`LossyRetryInvocationHandler` is a test-only subclass of `RetryInvocationHandler` that simulates lost responses by throwing fake `RetriableException`s for the first N successful underlying method invocations.

## Important APIs and Types
The constructor accepts `numToDrop`, a `FailoverProxyProvider`, and a `RetryPolicy`. It overrides `invoke` to reset a thread-local retry count and `invokeMethod` to drop results until the configured count is reached.

## Control Flow
Each top-level invocation sets `RetryCount` to zero. The underlying method is invoked normally; if the thread-local count is below `numToDrop`, the handler increments it and throws `RetriableException`, causing retry policy handling. Once enough responses have been dropped, it returns the real result.

## State and Persistence
State includes immutable `numToDrop` and a static thread-local counter. No persistent state exists.

## Dependencies and Integration Points
It integrates with retry tests, `RetriableException`, and the superclass retry/failover machinery.

## Risks and Edge Cases
The static thread-local is not cleared after invocation, so long-lived test threads can retain the last integer value. Because it invokes the target before throwing, it simulates lost responses rather than pre-execution failures and can duplicate side effects unless paired with idempotent/at-most-once test methods.

## Test Signals
Tests using this handler should assert exact retry counts, final returned value after drops, behavior when policy retry budget is too small, and no cross-thread interference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/LossyRetryInvocationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/MultiException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/MultiException.java

## Purpose
`MultiException` is an `IOException` wrapper for returning multiple keyed exceptions from a call so retry policy can evaluate all underlying failures.

## Important APIs and Types
The constructor accepts a `Map<String, Exception>`. `getExceptions` exposes that map. `toString` returns the map's `toString`.

## Control Flow
`RetryInvocationHandler.RetryInfo.newRetryInfo` detects `MultiException`, iterates its exception values, asks the retry policy about each, selects the most severe retry decision, and uses the maximum retry delay among non-fail decisions.

## State and Persistence
The instance stores a reference to the provided map without copying. It has no other state.

## Dependencies and Integration Points
It depends on `IOException` and `Map`, and is consumed by retry invocation handling.

## Risks and Edge Cases
Because the map is not defensively copied, external mutation can change exception contents after construction. Empty maps cause retry aggregation to produce no action, which would be unsafe if not prevented by callers. The class does not set a message or cause on `IOException`.

## Test Signals
Tests should cover aggregation of fail/retry/failover decisions, delay selection, map mutation behavior, empty-map handling expectations, and string output with keyed exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/MultiException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryInvocationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryInvocationHandler.java

## Purpose
`RetryInvocationHandler` is the dynamic-proxy invocation handler that applies Hadoop retry and failover policies around method calls, including RPC call-id propagation and asynchronous RPC integration.

## Important APIs and Types
The main public contract is `InvocationHandler.invoke`, `close`, `getConnectionId`, and `getProxyProvider`. Internal `Call` tracks one logical invocation, retry/failover counters, policy, call ID, and pending `RetryInfo`. `ProxyDescriptor` owns the active `FailoverProxyProvider.ProxyInfo` and failover count. `RetryInfo` captures selected retry action, delay, expected failover count, and failure exception.

## Control Flow
`invoke` determines whether the current proxy is an RPC proxy, allocates a call ID for RPC, creates either a synchronous `Call` or async `AsyncCall`, then loops until the call returns, throws, or async mode reports submitted. `Call.invokeOnce` invokes the method, catches exceptions, refuses retry if the thread is interrupted, asks `handleException` for retry info, sleeps or returns wait state, applies retry counters, and performs failover when needed. Failover is synchronized and only occurs if the provider failover count still equals the count observed before the attempt, preventing multiple concurrent failed calls from each causing separate failovers.

## State and Persistence
Instance state includes proxy descriptor, default and method-specific policies, successful-call flag, a set of proxy strings that have failed at least once for logging suppression, and an `AsyncCallHandler`. Per-call state includes counters and retry info. No persistent state exists, but RPC call ID and retry count are pushed to `Client` for server-side retry semantics.

## Dependencies and Integration Points
It integrates with `RetryProxy`, `FailoverProxyProvider`, `RetryPolicy`, `Idempotent`, `AtMostOnce`, Hadoop IPC `Client`, `RPC`, `RpcInvocationHandler`, `ProtocolTranslator`, and `AsyncCallHandler`.

## Risks and Edge Cases
Method policy mapping is by method name only, not signature. `method.setAccessible(true)` may be restricted on newer runtimes. `failedAtLeastOnce` is a plain `HashSet` accessed without synchronization, so concurrent invocations may race in logging state. Annotation lookup requires the provider interface to expose the exact method. MultiException aggregation depends on non-empty exception collections. Interrupted threads stop retry by rethrowing. Async mode changes control flow by returning null for submitted calls and storing the real result in a thread-local async handle.

## Test Signals
Tests should cover retry budgets, delay handling, interruption, failover count suppression under concurrency, method-specific policies, idempotent/at-most-once annotation effects, RPC call-id retry counts, async submission/completion, logging suppression after successful calls, and closing provider resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryInvocationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryPolicies.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryPolicies.java

## Purpose
`RetryPolicies` is the factory and implementation collection for common Hadoop retry strategies: no retry, retry forever, fixed/proportional/exponential retry limits, exception-dependent retry, remote-exception retry, multiple-linear-random retry, and failover-on-network-exception behavior.

## Important APIs and Types
Public factories include `retryForeverWithFixedSleep`, `retryUpToMaximumCountWithFixedSleep`, `retryUpToMaximumTimeWithFixedSleep`, `retryUpToMaximumCountWithProportionalSleep`, `exponentialBackoffRetry`, `retryByException`, `retryByRemoteException`, `retryOtherThanRemoteAndSaslException`, and `failoverOnNetworkException`. `MultipleLinearRandomRetry` is public with `Pair` and `parseCommaSeparatedString`.

## Control Flow
Simple policies return static fail/retry actions or bounded retry actions with computed delays. `RetryLimited` fails once retry count reaches max and otherwise delegates sleep calculation. `MultipleLinearRandomRetry` maps the current retry number to configured `(numRetries, sleepMillis)` bands and randomizes sleep in `[0.5x, 1.5x]`. Exception-dependent policies select a nested policy by exact exception class or remote exception class name. `FailoverOnNetworkExceptionRetry` first enforces failover/retry limits, fails SASL/token/access-control errors, fails over for connection/standby/observer-active classes, retries retriable exceptions, and only failovers generic socket/IO errors when the method is idempotent or at-most-once.

## State and Persistence
Policies are intended to be immutable. Several cache their string representation lazily. There is no persistent state; runtime randomness comes from `ThreadLocalRandom`.

## Dependencies and Integration Points
It integrates with Hadoop IPC exceptions (`RemoteException`, `RetriableException`, `StandbyException`, `ObserverRetryOnActiveException`), security exceptions (`AccessControlException`, `InvalidToken`, SASL), network exceptions, and `RetryInvocationHandler`.

## Risks and Edge Cases
`RetryUpToMaximumTimeWithFixedSleep` computes max retries as integer division by sleep time; zero sleep time would divide by zero. `calculateExponentialTime` multiplies before capping, so very large `time` and retry values can overflow before `Math.min`. `MultipleLinearRandomRetry.searchPair` uses `curRetry > numRetries`, which makes boundary semantics important. Exception maps use exact classes, not subclasses, except for explicit wrapping helpers. Access-control detection walks causes and can fail if cause chains are malformed.

## Test Signals
Tests should cover policy equality/hash behavior, all retry boundary counts, zero/negative constructor validation, random retry parse failures and valid bands, remote exception class-name matching, SASL/access/token fail-fast behavior, idempotent vs non-idempotent socket handling, exponential cap/overflow cases, and wrapped retriable/access-control exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryPolicies.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryPolicy.java

## Purpose
`RetryPolicy` defines the decision contract used by retry proxies to decide whether a failed method call should fail, retry, or fail over and retry.

## Important APIs and Types
`RetryAction` carries `RetryDecision action`, `delayMillis`, and optional `reason`. Static actions are `FAIL`, `RETRY`, and `FAILOVER_AND_RETRY`. `RetryDecision` ordering is `FAIL < RETRY < FAILOVER_AND_RETRY`, which is used by multi-exception aggregation.

## Control Flow
Implementations receive the exception, retry count, failover count, and idempotent/at-most-once flag in `shouldRetry`. They return an action or throw an exception to stop retrying.

## State and Persistence
The interface recommends immutable implementations. `RetryAction` is immutable and has no persistence.

## Dependencies and Integration Points
It is consumed by `RetryInvocationHandler`, `RetryPolicies`, `RetryUtils`, and failover providers. It references `Idempotent` and `AtMostOnce` as method-safety inputs.

## Risks and Edge Cases
Policy implementations must keep retry and failover counts semantics straight: retries include failover retries in the caller. Negative delays are not prohibited by `RetryAction` itself, so policies should validate. Throwing from `shouldRetry` bypasses action handling.

## Test Signals
Tests should validate action ordering assumptions, delay propagation, reason logging, implementation immutability, and behavior when policies throw.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryProxy.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryProxy.java

## Purpose
`RetryProxy` is a factory for dynamic proxies that apply `RetryInvocationHandler` to an interface implementation or failover proxy provider.

## Important APIs and Types
It has four `create` overloads: implementation plus single policy, provider plus single policy, implementation plus method-policy map with default fail, and provider plus method-policy map plus explicit default policy.

## Control Flow
Overloads that receive a concrete implementation wrap it in `DefaultFailoverProxyProvider`. All paths create a JDK dynamic proxy with the provider interface class loader, the requested interface, and a new `RetryInvocationHandler`.

## State and Persistence
`RetryProxy` is stateless. Generated proxy instances hold their invocation handler state.

## Dependencies and Integration Points
It depends on Java `Proxy`, `RetryInvocationHandler`, `DefaultFailoverProxyProvider`, `FailoverProxyProvider`, and `RetryPolicy`. It is the usual entry point shown in retry package docs.

## Risks and Edge Cases
The class loader comes from `proxyProvider.getInterface()`, not necessarily the `iface` argument. Method-policy maps key by method name and cannot distinguish overloads. Returned type is `Object`, so callers must cast correctly.

## Test Signals
Tests should create proxies with all overloads, verify interface/classloader behavior, method-policy routing, default policy fallback, provider close propagation, and overloaded method handling expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryProxy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryUtils.java

## Purpose
`RetryUtils` builds configured default retry policies, especially `MultipleLinearRandomRetry` wrappers that selectively retry IO, protobuf service, retriable, and configured remote exceptions.

## Important APIs and Types
`getDefaultRetryPolicy` reads enable/spec configuration and returns either `TRY_ONCE_THEN_FAIL` or a `WrapperRetryPolicy`. `getMultipleLinearRandomRetry` returns the parsed configured policy, the parsed default policy on parse failure, or null when disabled. `WrapperRetryPolicy` unwraps `ServiceException`, picks the nested policy, and defines equality/hash based on the multiple-linear policy.

## Control Flow
The utility first checks the enable flag. If enabled, it parses the policy spec string of sleep/retry pairs. The wrapper chooses multiple-linear retry for `RetriableException`, wrapped retriable remote exceptions, a configured remote exception class name, non-remote IOExceptions, and ServiceExceptions; otherwise it chooses `TRY_ONCE_THEN_FAIL`.

## State and Persistence
The class is stateless except logger. Wrapper instances store the selected multiple-linear policy and remote exception class name. No persistent state exists.

## Dependencies and Integration Points
It integrates with `Configuration`, `RetryPolicies.MultipleLinearRandomRetry`, Hadoop IPC `RemoteException`/`RetriableException`, protobuf `ServiceException`, and retry users that define configuration keys.

## Risks and Edge Cases
If both configured and default policy specs fail to parse, `getMultipleLinearRandomRetry` can return null even when enabled. `WrapperRetryPolicy.equals` ignores `remoteExceptionToRetry`, which is documented for connection-failure handling but can surprise if comparing full semantics. Logging format includes retry count and policy class. ServiceException unwrapping only occurs when cause is an `Exception`.

## Test Signals
Tests should cover disabled policies, valid and invalid specs, fallback parsing, remote-exception class matching, service exception unwrapping, wrapped retriable exceptions, equality/hash behavior with different remote exception names, and non-IO fail-fast behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/package-info.java

## Purpose
`package-info.java` documents the retry package as a mechanism for selectively retrying methods that throw exceptions under configured circumstances.

## Important APIs and Types
The documentation references `RetryProxy`, `RetryPolicies`, and `RetryPolicy`, and applies package-level `@InterfaceAudience.Public` and `@InterfaceStability.Evolving`.

## Control Flow
There is no executable code. The example flow constructs an implementation, wraps it with `RetryProxy.create`, and invokes methods through the retrying proxy.

## State and Persistence
There is no state. The file affects generated docs and API classification metadata.

## Dependencies and Integration Points
It imports Hadoop classification annotations and describes integration with retry proxy factories and policies.

## Risks and Edge Cases
Documentation examples can drift from overload signatures or policy behavior. Since the package is public/evolving, compatibility expectations are stronger than the private native package but still allow API changes.

## Test Signals
No runtime tests are required; documentation/link checks can verify referenced classes and methods remain valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/Deserializer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/Deserializer.java

## Purpose
`Deserializer<T>` defines Hadoop's stream-based object deserialization contract for HDFS and MapReduce serialization frameworks.

## Important APIs and Types
The interface exposes `open(InputStream)`, `deserialize(T reuse)`, and `close`. Implementations may reuse the provided object or allocate a new one when the argument is null.

## Control Flow
Clients open the deserializer on an input stream, repeatedly call `deserialize`, then close it. The contract explicitly says deserializers are stateful but must not buffer input because other producers may read from the same stream between calls.

## State and Persistence
Implementations usually hold stream wrappers and reusable object state. The interface itself has no state. Deserialized objects are produced from the stream format owned by each `Serialization`.

## Dependencies and Integration Points
It pairs with `Serializer` and `Serialization`, and is used by `DeserializerComparator`, `JavaSerialization`, `WritableSerialization`, and `SerializationFactory`.

## Risks and Edge Cases
Implementations that buffer ahead can corrupt mixed stream consumers. Reuse semantics are optional, so callers cannot assume object identity. `close` closes the underlying stream according to this contract.

## Test Signals
Tests should verify open/deserialize/close lifecycle, object reuse behavior per implementation, no read-ahead across object boundaries, error propagation, and close cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/Deserializer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/DeserializerComparator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/DeserializerComparator.java

## Purpose
`DeserializerComparator<T>` is a `RawComparator` base class that compares serialized byte slices by deserializing them and delegating to the normal object comparator.

## Important APIs and Types
The constructor accepts a `Deserializer<T>` and opens it on an internal `InputBuffer`. `compare(byte[], int, int, byte[], int, int)` resets the buffer to each byte slice, deserializes into reusable `key1` and `key2`, and returns `compare(key1, key2)`, which subclasses implement through `Comparator<T>`.

## Control Flow
Every raw comparison performs two deserialize operations. `IOException` from deserialization is wrapped in `RuntimeException` because `RawComparator.compare` cannot throw checked exceptions.

## State and Persistence
The comparator holds a reusable `InputBuffer`, one deserializer, and two reusable key objects. This makes instances stateful and not inherently thread-safe.

## Dependencies and Integration Points
It integrates with Hadoop `RawComparator`, `InputBuffer`, and serialization implementations such as `JavaSerializationComparator`.

## Risks and Edge Cases
Because it deserializes for every compare, it is slower than byte-native comparators for sort-heavy paths. Shared mutable `key1`/`key2` and `InputBuffer` make concurrent use unsafe. Implementations must tolerate deserializer reuse with changing buffer content.

## Test Signals
Tests should compare equivalent and ordered serialized keys, malformed byte slices, reuse of key objects across calls, runtime exception wrapping, and thread-safety assumptions if shared in sort code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/DeserializerComparator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/JavaSerialization.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/JavaSerialization.java

## Purpose
`JavaSerialization` is an experimental Hadoop `Serialization` implementation for Java `Serializable` objects using `ObjectInputStream` and `ObjectOutputStream`.

## Important APIs and Types
`JavaSerializationDeserializer` opens an `ObjectInputStream` with stream-header reading disabled and reads objects with `readObject`. `JavaSerializationSerializer` opens an `ObjectOutputStream` with stream-header writing disabled, calls `reset` before each `writeObject`, and closes the stream. The outer class accepts any class assignable to `Serializable`.

## Control Flow
Serialization writes each object without a per-stream Java serialization header and resets back-reference state before writing to avoid cross-object reference retention. Deserialization ignores any reuse object and always returns the next object read from the stream, wrapping `ClassNotFoundException` as `IOException`.

## State and Persistence
Serializer and deserializer instances hold object stream wrappers. The persisted format is Java native serialization objects without stream headers at this layer, which assumes the surrounding framework provides record boundaries and compatible stream handling.

## Dependencies and Integration Points
It implements Hadoop `Serialization<Serializable>`, produces `Serializer`/`Deserializer` pairs, and is paired with `JavaSerializationComparator` for comparable serializable keys.

## Risks and Edge Cases
Java serialization is unstable across class evolution, can be unsafe for untrusted data, and is marked experimental/unstable. Suppressing stream headers means these objects are not standalone standard Java serialization streams. Reuse is ignored, potentially increasing allocations. `IOException(e.toString())` loses the original `ClassNotFoundException` cause.

## Test Signals
Tests should cover round trips for simple serializable classes, multiple objects in one stream, object reference reset behavior, class-not-found handling, close behavior, compatibility with comparator deserialization, and rejection/acceptance by `Serializable` assignability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/JavaSerialization.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/JavaSerializationComparator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/JavaSerializationComparator.java

## Purpose
`JavaSerializationComparator` compares raw serialized Java-serialization keys by deserializing them and invoking their `Comparable` implementation.

## Important APIs and Types
The generic bound requires `T extends Serializable & Comparable<T>`. The constructor creates a `JavaSerializationDeserializer<T>` and passes it to `DeserializerComparator`. `compare(T o1, T o2)` delegates to `o1.compareTo(o2)`.

## Control Flow
Raw byte comparison flow is inherited: reset buffer to first slice, deserialize, reset to second slice, deserialize, then compare objects.

## State and Persistence
State lives in the superclass: an input buffer, deserializer, and reusable key references. The comparator has no additional fields.

## Dependencies and Integration Points
It integrates with `JavaSerialization`, `DeserializerComparator`, and Hadoop `RawComparator`. TFile documentation mentions Java comparator classes can be referenced with `jclass:` if they have default constructors.

## Risks and Edge Cases
It inherits performance and thread-safety costs from deserialization-based comparison. It assumes serialized objects are mutually comparable and non-null. Malformed serialized bytes produce runtime exceptions via the superclass.

## Test Signals
Tests should compare ordered serializable keys, equal keys, malformed data, null-handling expectations, constructor availability for reflective use, and repeated comparisons with object reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/JavaSerializationComparator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/Serialization.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/Serialization.java

## Purpose
`Serialization<T>` is Hadoop's abstraction for a matched serializer/deserializer pair that supports a set of Java classes.

## Important APIs and Types
The interface defines `accept(Class<?>)`, `getSerializer(Class<T>)`, and `getDeserializer(Class<T>)`.

## Control Flow
Factories such as `SerializationFactory` use `accept` to choose an implementation for a class, then obtain a serializer or deserializer to process streams.

## State and Persistence
The interface has no state. Implementations define stream formats and may carry configuration through Hadoop's `Configured` pattern.

## Dependencies and Integration Points
It is implemented by Java, Writable, and Avro serialization providers and is consumed by Hadoop data paths that need pluggable serialization.

## Risks and Edge Cases
`accept` can overlap across implementations; ordering in the factory determines selection. Generic type erasure means callers must ensure class/provider compatibility. Serializer/deserializer instances may be stateful and need proper lifecycle handling.

## Test Signals
Tests should verify provider selection order, accept behavior for supported/unsupported classes, serializer/deserializer creation, lifecycle, and behavior when no provider accepts a class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/Serialization.java -->
