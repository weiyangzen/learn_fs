# subset-b-007582 research

This grouped report covers the requested Hadoop S3A stream, prefetch, S3Guard, select, statistics, and tool source files. Each section is wrapped with the exact reconciliation markers required for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/ObjectInputStreamFactory.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/ObjectInputStreamFactory.java

Purpose: defines the stable service interface for S3A object input stream factories. It lets `S3AStore` create, bind, start, and query stream implementations without changing the factory method signature as new read parameters are added.

Important APIs/types/functions: `ObjectInputStreamFactory` extends Hadoop `Service` and `StreamCapabilities`; `bind(FactoryBindingParameters)` wires store callbacks after init and before start; `readObject(ObjectReadParameters)` creates an `ObjectInputStream`; `factoryRequirements()` exposes thread/vector IO needs; `streamType()` identifies the produced `InputStreamType`; nested `StreamFactoryCallbacks` supplies a synchronous AWS `S3Client` and factory statistic increments.

Control flow: store code constructs a factory, initializes it as a service, binds extra callbacks, then calls `readObject()` for each opened object. Implementations may lazily contact S3 after returning the stream.

State/persistence: the interface persists no data, but it defines a lifecycle state contract through `Service`. Implementations may retain bound callbacks and configuration.

Dependencies/integration: integrates with AWS SDK v2 `S3Client`, Hadoop service lifecycle, stream capability probing, S3A `Statistic`, and the stream factory selection layer in `StreamIntegration`.

Risks/test signals: lifecycle misuse is the main risk, especially calling `bind()` outside init/start ordering. Tests should exercise custom factories, service lifecycle, factory requirement propagation, and capability/statistic callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/ObjectInputStreamFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/ObjectReadParameters.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/ObjectReadParameters.java

Purpose: mutable builder-style parameter object for object stream creation. It centralizes read context, object metadata, callbacks, statistics, executors, local storage, encryption, and audit span inputs so factory APIs stay stable.

Important APIs/types/functions: getters and `with...()` setters cover `S3AReadOpContext`, `S3ObjectAttributes`, `ObjectInputStreamCallbacks`, `S3AInputStreamStatistics`, bounded `ExecutorService`, `LocalDirAllocator`, `EncryptionSecrets`, and `AuditSpan`. `validate()` requires every required field with `requireNonNull()` and returns `this`.

Control flow: callers populate the object, usually validate it near stream creation, then pass it into `ObjectInputStreamFactory.readObject()`. The setters do not freeze or clone values, so later mutation by the caller remains visible.

State/persistence: keeps in-memory references only. No external persistence. Because validation is not immutability, the object is not a safe long-lived immutable configuration snapshot.

Dependencies/integration: bridges S3A read planning (`S3AReadOpContext`), metadata (`S3ObjectAttributes`), auditing, encryption, local temp allocation, statistics, and executor resources into classic, analytics, or prefetch stream factories.

Risks/test signals: missing required parameters fail late at validation or stream construction. Tests should assert all mandatory fields are checked, builder chaining preserves object identity, and factories consume the expected executor, allocator, encryption secrets, and audit span.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/ObjectReadParameters.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/StreamFactoryRequirements.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/StreamFactoryRequirements.java

Purpose: immutable description of resources and filesystem behavior required by a stream factory. It lets the filesystem size shared pools and configure vectored IO based on the selected stream type.

Important APIs/types/functions: constructor accepts shared thread count, per-stream thread count, mutable `VectoredIOContext`, and varargs `Requirements`. It calls `vectoredIOContext.build()` to freeze the vector context. Accessors include `sharedThreads()`, `streamThreads()`, `requiresFuturePool()`, `vectoredIOContext()`, and `requires(Requirements)`. Requirement flags are `ExpectUnauditedGetRequests` and `RequiresFuturePool`.

Control flow: a factory computes requirements after configuration initialization. The S3A filesystem reads these values before serving streams and adjusts background pools/auditing/vector behavior.

State/persistence: contains final in-memory values only. No persistence. The enum set is built from varargs and then treated as read-only by callers.

Dependencies/integration: depends on `VectoredIOContext` and is returned by `ObjectInputStreamFactory.factoryRequirements()`.

Risks/test signals: incorrect thread counts can underprovision or oversubscribe stream workloads; vector context immutability depends on `build()`. Tests should assert vararg flags, no-flag behavior, vector configuration propagation, and `toString()` diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/StreamFactoryRequirements.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/StreamIntegration.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/StreamIntegration.java

Purpose: central stream integration utility for resolving configured S3A input stream types, constructing factories, loading custom factories, and building vectored IO context from configuration.

Important APIs/types/functions: constants name stream modes (`classic`, `prefetch`, `analytics`, `custom`, `default`), with `DEFAULT_STREAM_TYPE` set to analytics. `factoryFromConfig()` resolves an `InputStreamType` and invokes its factory function. `determineInputStreamType()` handles deprecated `fs.s3a.prefetch.enabled`, default mapping, enum resolution, and invalid type errors. `loadCustomFactory()` requires `INPUT_STREAM_CUSTOM_FACTORY`, loads a no-arg constructor, and wraps instantiation failures. `populateVectoredIOContext()` reads min seek, max merged read size, and active range read settings.

Control flow: stream selection first honors deprecated prefetch enablement, then resolves `fs.s3a.input.stream.type`, then constructs the factory. Custom factories are reflection-loaded only for the custom enum path.

State/persistence: stateless utility. The only durable behavior is configuration interpretation and one-time deprecation logging through `LogExactlyOnce`.

Dependencies/integration: ties Hadoop `Configuration`, `ConfigurationHelper.resolveEnum`, S3A constants, `VectoredIOContext`, and `InputStreamType` factory functions together.

Risks/test signals: wrong default or deprecated-option precedence changes runtime stream type. Custom factory loading can fail on missing class/no no-arg constructor. Tests should cover empty/default/custom/invalid values, deprecated prefetch override, and vectored IO bounds parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/StreamIntegration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/package-info.java

Purpose: package documentation for private, unstable S3A stream implementation classes and factory integration.

Important APIs/types/functions: no executable APIs. The package annotations mark the stream implementation package as private and unstable.

Control flow: none.

State/persistence: none.

Dependencies/integration: documents the package consumed by S3A filesystem internals and alternate stream factories.

Risks/test signals: no runtime risk. Test signal is compile-time/package-level annotation visibility and Javadoc generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/write/WriteObjectFlags.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/write/WriteObjectFlags.java

Purpose: enum of S3A object-write feature flags used both for builder option parsing and output stream `hasCapability()` probes.

Important APIs/types/functions: flags include `ConditionalOverwrite`, `ConditionalOverwriteEtag`, `CreateMultipart`, `Performance`, and non-configurable `Recursive`. Each flag stores its configuration/capability key. `isEnabled(Configuration)` reads a boolean key defaulting false. `hasKey(String)` matches non-empty keys.

Control flow: create-file/build paths can map option keys to enum values and probe booleans; output streams can expose the same key namespace as capabilities.

State/persistence: enum constants are static process state only. No persistence.

Dependencies/integration: depends on Hadoop create-file option keys and S3A constants for multipart/performance behavior.

Risks/test signals: `Recursive` has an empty key, so `isEnabled()` on it always reads an empty config key and should not be used for configurable options. Tests should assert key matching, disabled defaults, and capability names for conditional overwrite and multipart behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/write/WriteObjectFlags.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/write/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/write/package-info.java

Purpose: package documentation for internal S3A write implementation support.

Important APIs/types/functions: no executable APIs; package annotations mark the package private and unstable.

Control flow: none.

State/persistence: none.

Dependencies/integration: groups write implementation helpers used by S3A output stream and create-file code.

Risks/test signals: no direct runtime risk; verify package annotations and generated Javadoc if API visibility matters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/write/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/package-info.java

Purpose: top-level package documentation for the S3A connector.

Important APIs/types/functions: no executable code. Package annotations establish intended audience/stability for S3A package APIs.

Control flow: none.

State/persistence: none.

Dependencies/integration: this package contains the main S3A filesystem, constants, status objects, invokers, and public integration points used by Hadoop and tools.

Risks/test signals: no runtime behavior. Documentation and annotation changes can affect downstream expectations for public/private API status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/PrefetchOptions.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/PrefetchOptions.java

Purpose: immutable holder for prefetch block size and prefetch queue depth.

Important APIs/types/functions: constructor validates `prefetchBlockSize > 0` and `prefetchBlockCount > 0`; getters expose both values.

Control flow: `PrefetchingInputStreamFactory` builds this once during service init and passes it into every `S3APrefetchingInputStream`.

State/persistence: final in-memory values only. No persistence or mutability.

Dependencies/integration: uses Hadoop `Preconditions.checkArgument`; consumed by prefetch stream constructors and block manager setup.

Risks/test signals: bad config values fail early. Tests should cover zero/negative rejection and propagation of configured values into in-memory versus caching stream decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/PrefetchOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/PrefetchingInputStreamFactory.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/PrefetchingInputStreamFactory.java

Purpose: `ObjectInputStreamFactory` implementation for the prefetch stream. It parses prefetch configuration and creates `S3APrefetchingInputStream` instances.

Important APIs/types/functions: extends `AbstractObjectInputStreamFactory`; `streamType()` returns `InputStreamType.Prefetch`; `serviceInit()` reads `PREFETCH_BLOCK_SIZE_KEY` and `PREFETCH_BLOCK_COUNT_KEY`, validates int-sized block size, and constructs `PrefetchOptions`; `readObject()` returns a new `S3APrefetchingInputStream`; `factoryRequirements()` requests `prefetchBlockCount` shared threads, no stream threads, a vectored context with min seek set to zero, and `RequiresFuturePool`.

Control flow: service init prepares shared options; each read creates a wrapper stream. Range merging is disabled for vectored IO by setting min seek to zero to avoid fetching discarded bytes.

State/persistence: stores configured block size/count and immutable options for factory lifetime.

Dependencies/integration: integrates with S3A constants, `S3AUtils` config parsers, `StreamIntegration.populateVectoredIOContext`, and future-pool provisioning.

Risks/test signals: large block sizes above int max fail; low queue counts reduce throughput; vector settings deliberately alter read coalescing. Tests should cover config validation, requirements, and stream creation with validated `ObjectReadParameters`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/PrefetchingInputStreamFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ABlockManager.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ABlockManager.java

Purpose: simple `BlockManager` implementation that reads blocks directly from S3 without caching or prefetching. It provides a baseline implementation.

Important APIs/types/functions: constructor accepts `S3ARemoteObjectReader` and `BlockData`; `read(ByteBuffer,long,int)` delegates to `reader.read()`; `close()` closes the reader.

Control flow: callers request a block, and the manager synchronously reads the range from the remote object reader.

State/persistence: owns a reader reference and block metadata inherited from `BlockManager`. No local cache persistence.

Dependencies/integration: depends on Hadoop prefetch framework `BlockManager`, `BlockData`, and `Validate`, plus S3A's remote object reader.

Risks/test signals: since it has no cache, repeated seeks cause repeated S3 reads. Tests should verify null validation, range delegation, and close propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ABlockManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ACachingBlockManager.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ACachingBlockManager.java

Purpose: S3A specialization of the generic `CachingBlockManager`, using `S3ARemoteObjectReader` as the backing range reader.

Important APIs/types/functions: constructor passes `BlockManagerParameters` to the superclass and validates the reader; `getReader()` supports tests/subclasses; `read(ByteBuffer,long,int)` delegates to the reader; synchronized `close()` closes the reader before superclass cleanup.

Control flow: `S3ACachingInputStream` requests prefetch/cache operations from this manager. Cache and buffer-pool behavior lives in the superclass, while this class supplies S3 range reads.

State/persistence: inherits cache state, local-file cache management, buffer pool, and asynchronous futures from `CachingBlockManager`; this class adds only the reader reference.

Dependencies/integration: integrates S3 remote reads with `org.apache.hadoop.fs.impl.prefetch` caching infrastructure and local directory allocation configured upstream.

Risks/test signals: close ordering matters to cancel S3 reads and cleanup cache resources. Tests should cover read delegation, reader visibility, idempotent/synchronized close, and interaction with failed prefetch futures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ACachingBlockManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ACachingInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ACachingInputStream.java

Purpose: remote input stream for larger objects that reads block-by-block, prefetches ahead on sequential reads, and caches partially consumed blocks to local disk when seek patterns suggest reuse.

Important APIs/types/functions: constructor builds `BlockManagerParameters` with future pool, block data, buffer pool size `prefetchBlockCount + 1`, configuration, `LocalDirAllocator`, max cache blocks, stream statistics, and tracker factory. `ensureCurrentBuffer()` is the main read-position algorithm. `createBlockManager()` returns `S3ACachingBlockManager` and is overridable for tests. `close()` closes the block manager then remote stream.

Control flow: on read, `ensureCurrentBuffer()` validates offset, detects out-of-order reads via `FilePosition.setAbsolute()`, releases fully read blocks, caches partially read ones, cancels prefetches after seeks, queues one block after a seek or `numBlocksToPrefetch` blocks for sequential reads, fetches the current block with duration tracking, then binds it into `FilePosition`.

State/persistence: maintains prefetch count and a block manager that may store blocks in local temporary files and memory buffers. Close deletes cached files and frees buffers through the block manager.

Dependencies/integration: integrates `S3ARemoteInputStream`, prefetch framework `BlockManager`, `BufferData`, `FilePosition`, S3A statistics, local directory allocation, and stream statistic name `STREAM_READ_BLOCK_ACQUIRE_AND_READ`.

Risks/test signals: seek-heavy workloads can cause cancellations and local cache churn; local disk configuration and max block count constrain behavior. Tests should cover sequential prefetch, lazy seek, partial-buffer caching, full-buffer release, cache cleanup, and statistics tracking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ACachingInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3AInMemoryInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3AInMemoryInputStream.java

Purpose: optimized prefetch stream for small objects whose length is less than or equal to the configured prefetch block size. It loads the full object into one `ByteBuffer`.

Important APIs/types/functions: constructor allocates `ByteBuffer` sized to the object length. `ensureCurrentBuffer()` lazily reads the full file through `S3ARemoteObjectReader` the first time data is needed, wraps it in `BufferData`, and later only updates `FilePosition` for seeks.

Control flow: first read fills the entire buffer from offset zero; subsequent reads and seeks reuse the same in-memory buffer until close.

State/persistence: object contents are held in heap memory for the stream lifetime. No disk persistence.

Dependencies/integration: extends `S3ARemoteInputStream` and uses prefetch framework `BufferData`/`FilePosition`.

Risks/test signals: object length is cast to int after the wrapper's block-size decision; large unexpected lengths would be unsafe. Tests should cover empty file behavior, first-read load, lazy seek, EOF, and close path inherited from the superclass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3AInMemoryInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3APrefetchingInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3APrefetchingInputStream.java

Purpose: public `ObjectInputStream` wrapper for the prefetch implementation. It selects the in-memory or caching remote stream, synchronizes public stream methods, and preserves statistics access after close.

Important APIs/types/functions: constructor validates `S3ObjectAttributes`, callbacks, and statistics, then chooses `S3AInMemoryInputStream` when file size is within one block and `S3ACachingInputStream` otherwise. Overrides `available()`, `getPos()`, `read()`, `read(byte[],int,int)`, `close()`, `seek()`, `setReadahead()`, `hasCapability()`, `getS3AStreamStatistics()`, `getIOStatistics()`, `seekToNewSource()`, and `markSupported()`.

Control flow: all read/seek/available methods check `isClosed()` then delegate to `inputStream`. Close closes and nulls the delegate, then calls `super.close()`. `getPos()`, `getS3AStreamStatistics()`, and `getIOStatistics()` cache last values so callers can inspect after close.

State/persistence: holds one delegate stream, last read position, cached IO statistics, and cached S3A stream statistics. Underlying delegate may keep memory or local cache state.

Dependencies/integration: integrates `ObjectReadParameters`, `InputStreamType.Prefetch`, S3A stream statistics, Hadoop stream capabilities, and the prefetch remote streams.

Risks/test signals: synchronized methods serialize access but do not make the underlying resources reusable after close. Tests should verify delegate choice, post-close diagnostics, capability reporting, leak finalizer behavior, unsupported mark/new-source behavior, and correct exception on closed stream.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3APrefetchingInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ARemoteInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ARemoteInputStream.java

Purpose: abstract base `InputStream` for prefetch remote streams. It implements common seek/read/close/statistics behavior while subclasses decide how to ensure a current buffer.

Important APIs/types/functions: constructor creates `ChangeTracker`, records input policy/readahead, builds `BlockData`, `FilePosition`, `S3ARemoteObject`, and `S3ARemoteObjectReader`. Public APIs include `getIOStatistics()`, `getS3AStreamStatistics()`, `setReadahead()`, `hasCapability()`, `available()`, `getPos()`, `seek()`, `read()`, `read(byte[],int,int)`, `close()`, `markSupported()`, and unsupported `mark/reset/skip`. Protected helpers expose file, reader, attributes, position, block data, context, and offset formatting.

Control flow: reads check close/EOF, call subclass `ensureCurrentBuffer()`, copy bytes from `FilePosition.buffer()`, advance `nextReadPos`, and update stream/filesystem byte counters. Seek is lazy and only changes `nextReadPos`; the next read moves buffers.

State/persistence: maintains volatile `closed`, current file position, next-read offset, block metadata, callbacks, remote object, reader, change tracker, input policy, and IO statistics. Close releases references, closes reader and callbacks, invalidates file position, and closes statistics.

Dependencies/integration: depends on S3A read context, object attributes, callbacks, change detection policy, Hadoop prefetch `BlockData`/`FilePosition`, and IOStatistics.

Risks/test signals: buffer position and `nextReadPos` must remain consistent across partial reads and seeks. Tests should cover EOF, negative/past-EOF seek, available behavior, byte/stat counters, close idempotence, and subclass buffer transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ARemoteInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ARemoteObject.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ARemoteObject.java

Purpose: encapsulates low-level S3 range GET behavior for prefetch streams, including request construction, change tracking, statistics, and stream draining on close.

Important APIs/types/functions: constructor validates read context, attributes, callbacks, statistics, and `ChangeTracker`. `getReadInvoker()`, `getStatistics()`, `getPath()`, static `getPath(S3ObjectAttributes)`, and `size()` expose metadata. `openForRead(long,int)` validates range, increments stream-open stats, builds a ranged `GetObjectRequest`, applies change constraints, tracks get duration, invokes `client.getObject()`, and processes response change metadata. Package-private `close(ResponseInputStream,int)` drains synchronously below async drain threshold or submits `SDKStreamDrainer`.

Control flow: `S3ARemoteObjectReader` opens a ranged stream, reads bytes, then calls `close()` with remaining bytes so the SDK stream is drained or aborted appropriately.

State/persistence: holds immutable references to context, attributes, callbacks, statistics, change tracker, and derived URI. No persistence.

Dependencies/integration: AWS SDK v2 `GetObjectRequest/ResponseInputStream`, S3A `Invoker`, `S3AUtils.formatRange`, `SDKStreamDrainer`, change tracking, and stream statistics.

Risks/test signals: off-by-one range formatting, change constraint failures, and drain threshold behavior are critical. Tests should cover invalid ranges, request mutation, change tracker response handling, get duration failure tracking, and async drain submission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ARemoteObject.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ARemoteObjectReader.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ARemoteObjectReader.java

Purpose: range-block reader that fills a `ByteBuffer` from an `S3ARemoteObject` with S3A retry/statistics integration.

Important APIs/types/functions: constructor validates `S3ARemoteObject`. `read(ByteBuffer,long,int)` validates buffer, offset, and size, returns -1 if closed, clamps request size to remaining object bytes, then calls `readOneBlockWithRetries()`. `close()` sets a volatile closed flag. `readOneBlockWithRetries()` starts read statistics, invokes retrying `Invoker.retry()`, tracks `STREAM_READ_REMOTE_BLOCK_READ`, handles EOF/socket/IO exceptions, adjusts buffer limit, and records completion. `readOneBlock()` opens the S3 range and copies 64 KiB chunks into the buffer until size is satisfied or closed.

Control flow: a block manager calls `read()` for a block; the reader retries the remote read according to context invoker policy, then updates the buffer for consumers.

State/persistence: owns remote object reference, stream statistics, and a closed flag. No data cache.

Dependencies/integration: integrates with S3A `Invoker`, AWS `ResponseInputStream`, Hadoop IO statistics binding, and `S3ARemoteObject.close()`.

Risks/test signals: the code uses buffer position to compute bytes read and sets limit to that position, so callers must prepare buffer positions correctly. Tests should cover partial object tails, EOF during body read, close during read, retry accounting, and buffer limit/position outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ARemoteObjectReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/package-info.java

Purpose: package documentation for the high-performance S3A prefetch input stream implementation.

Important APIs/types/functions: no executable APIs. Package annotations mark it private and unstable.

Control flow: none.

State/persistence: none.

Dependencies/integration: describes stream code that reads S3 data in blocks and can cache blocks in the local filesystem.

Risks/test signals: no direct runtime risk; validate package annotations and Javadoc if API surface changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/s3guard/S3Guard.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/s3guard/S3Guard.java

Purpose: compatibility utility for a now-removed/unsupported S3Guard feature set while retaining authoritative-path helper logic.

Important APIs/types/functions: private constructor prevents instantiation. `checkNoS3Guard(URI,Configuration)` rejects configured metadata stores other than the null metadata store. `getAuthoritativePaths(URI,Configuration)` reads authoritative path config. `allowAuthoritative(Path,S3AFileSystem,Set<Path>)` decides whether a path is covered by authoritative configuration.

Control flow: filesystem startup/tooling can call `checkNoS3Guard()` to fail fast if legacy metadata store config is present. Authoritative-path checks normalize configured paths and compare requested paths against the bucket filesystem.

State/persistence: stateless utility. Reads configuration only.

Dependencies/integration: uses S3A constants, Hadoop `Path`, `Configuration`, `PathIOException`, and `S3AFileSystem`.

Risks/test signals: legacy config must produce clear failures instead of silently enabling removed behavior. Tests should cover null/default metadata store allowance, non-null metadata store rejection, bucket-qualified authoritative paths, and path matching edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/s3guard/S3Guard.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/s3guard/S3GuardTool.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/s3guard/S3GuardTool.java

Purpose: command-line entry point and base class for S3A administrative commands historically under `s3guard`. It now rejects unsupported S3Guard commands while dispatching supported bucket, marker, bucket-info, and multipart upload tools.

Important APIs/types/functions: base `S3GuardTool` handles `CommandFormat`, filesystem binding/unwrapping, age option parsing, IO statistics dumping, formatted errors, and `ExitUtil.ExitException` helpers. Nested `BucketInfo` reports bucket/client/committer/security/marker/capability status and validates requested flags. Nested `Uploads` lists, expects, or aborts multipart uploads, with optional age filters, verbose mode, and force prompt bypass. Static `run(Configuration,String...)` parses generic options, rejects unsupported command names, dispatches subcommands, and cleans up. `main()` maps exceptions to launcher exit codes.

Control flow: CLI parses generic Hadoop options, selects a subcommand, constructs the tool, delegates through `ToolRunner`, then closes resources. `BucketInfo` binds to an S3A FS, probes location/capabilities, prints config and validates requested properties. `Uploads` resolves mode, prompts before abort unless forced, iterates `fs.listUploads(prefix)`, filters by age, optionally aborts through `WriteOperationHelper`, and validates expected counts.

State/persistence: base class holds the bound base filesystem and S3A filesystem until close. Upload abort mode mutates remote S3 multipart upload state. Other modes mainly inspect configuration and remote metadata.

Dependencies/integration: integrates Hadoop `Tool`, `GenericOptionsParser`, `ToolRunner`, S3A filesystem internals, commit constants, delegation tokens, audit spans, AWS multipart uploads, marker/bucket tools, and IO statistics logging.

Risks/test signals: user-facing exit code mapping is important for scripts. Upload abort is destructive and protected only by prompt/force. Tests should cover unsupported commands, wrong filesystem binding, bucket-info validation flags, upload mode mutual exclusion, age filtering, expected count failures, and cleanup on exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/s3guard/S3GuardTool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/s3guard/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/s3guard/package-info.java

Purpose: package documentation for S3Guard compatibility and administrative tooling.

Important APIs/types/functions: no executable APIs; package annotations define audience/stability.

Control flow: none.

State/persistence: none.

Dependencies/integration: groups S3Guard-related compatibility helpers and command dispatch code.

Risks/test signals: no direct runtime risk; documentation should stay aligned with removed S3Guard support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/s3guard/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/select/SelectConstants.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/select/SelectConstants.java

Purpose: constant holder for legacy S3 Select configuration keys, capability strings, and CSV/JSON option values, while declaring S3 Select unsupported.

Important APIs/types/functions: private constructor prevents instantiation. `SELECT_UNSUPPORTED` is the user-facing unsupported message. Constants cover `fs.s3a.select.*`, SQL, capability, enablement, input/output format, compression, CSV input/output delimiters, quote settings, header options, and error SQL inclusion.

Control flow: no methods. Other code can reference constants for compatibility, config parsing, or unsupported command errors.

State/persistence: static constants only.

Dependencies/integration: used by `S3GuardTool` to reject `select` command with `EXIT_UNSUPPORTED_VERSION`, and by any remaining tests/config compatibility code.

Risks/test signals: stale constants may preserve compatibility but should not imply feature support. Tests should assert unsupported command behavior and constant names expected by existing configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/select/SelectConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/select/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/select/package-info.java

Purpose: package documentation for legacy S3 Select support namespace.

Important APIs/types/functions: no executable APIs; package annotations define private/unstable status.

Control flow: none.

State/persistence: none.

Dependencies/integration: groups constants used for unsupported S3 Select compatibility.

Risks/test signals: ensure documentation reflects that S3 Select is no longer supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/select/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/BlockOutputStreamStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/BlockOutputStreamStatistics.java

Purpose: statistics contract for block-based S3A output streams.

Important APIs/types/functions: extends `Closeable`, `S3AStatisticInterface`, and `PutTrackerStatistics`. Methods record block queue/start/complete/failure events, bytes transferred/written, multipart complete/abort exceptions, pending upload bytes, committed uploaded size, allocated/released/active blocks, counter/gauge lookups, hflush/hsync calls, and conditional create outcomes.

Control flow: output stream code calls methods at block lifecycle and sync/write boundaries; implementations update IOStatistics, gauges, counters, and durations.

State/persistence: interface only. Implementations may hold counters/gauges in memory and publish into filesystem statistics.

Dependencies/integration: used by S3A block output streams, multipart put trackers, and IOStatistics consumers.

Risks/test signals: missing event calls skew active block/pending byte gauges. Tests should exercise successful upload, failed upload, conditional create, sync calls, and close semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/BlockOutputStreamStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/ChangeTrackerStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/ChangeTrackerStatistics.java

Purpose: minimal statistics contract for object version/change tracking.

Important APIs/types/functions: `versionMismatchError()` increments mismatch count; `getVersionMismatches()` returns the accumulated mismatch count.

Control flow: `ChangeTracker` calls this when object version or ETag policies detect a mismatch during reads.

State/persistence: interface only. Implementations typically maintain an in-memory counter.

Dependencies/integration: consumed by `S3AInputStreamStatistics.getChangeTrackerStatistics()` and `CountingChangeTracker`.

Risks/test signals: mismatch counters are important diagnostics for consistency failures. Tests should verify increments and propagation through stream statistics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/ChangeTrackerStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/CommitterStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/CommitterStatistics.java

Purpose: statistics contract for S3A committers and task/job commit outcomes.

Important APIs/types/functions: extends `S3AStatisticInterface`. Methods record commit created/uploaded/completed/aborted/reverted/failed events and task/job completion success or failure.

Control flow: commit protocol implementations call these at lifecycle points so filesystem and job-level statistics reflect committer activity.

State/persistence: interface only. Implementations update IOStatistics/counters in memory.

Dependencies/integration: used by S3A committers and `S3AStatisticsContext.newCommitterStatistics()`.

Risks/test signals: missing failure/revert events can mask data-commit reliability issues. Tests should assert all committer branches update expected counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/CommitterStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/CountersAndGauges.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/CountersAndGauges.java

Purpose: shared statistics sink for S3A counters, gauges, quantiles, and durations.

Important APIs/types/functions: extends `DurationTrackerFactory`. Methods increment counters/gauges, decrement gauges, add quantile values, and record completed durations with success status.

Control flow: components receive a context implementing this interface and emit numeric events by `Statistic` enum key.

State/persistence: interface only. Implementations may forward into `S3AInstrumentation` and `IOStatisticsStore`.

Dependencies/integration: base for `S3AStatisticsContext` and `S3AStatisticInterface` behavior.

Risks/test signals: invalid statistic keys or incorrect sign on gauges can corrupt metrics. Tests should cover counter/gauge increments, duration success/failure paths, and quantile recording.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/CountersAndGauges.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/DelegationTokenStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/DelegationTokenStatistics.java

Purpose: statistics contract for S3A delegation token issuance.

Important APIs/types/functions: extends `S3AStatisticInterface`; `tokenIssued()` records creation/issuance of a token.

Control flow: delegation token integration calls `tokenIssued()` when issuing a token.

State/persistence: interface only.

Dependencies/integration: created by `S3AStatisticsContext.newDelegationTokenStatistics()`.

Risks/test signals: token issuance metrics are security/operational diagnostics. Tests should verify token issuance increments in real implementation and no-op behavior in empty context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/DelegationTokenStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/PutTrackerStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/PutTrackerStatistics.java

Purpose: statistics extension point for put tracker behavior.

Important APIs/types/functions: extends `S3AStatisticInterface`. In this source version it is a marker-style interface with no additional methods.

Control flow: output stream statistics can be passed where put tracker statistics are required.

State/persistence: interface only.

Dependencies/integration: inherited by `BlockOutputStreamStatistics`.

Risks/test signals: main risk is API drift if put tracker events are later added. Compile-time tests catch implementations that need updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/PutTrackerStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/S3AInputStreamStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/S3AInputStreamStatistics.java

Purpose: comprehensive statistics contract for S3A input streams, including classic, analytics, and prefetch reads.

Important APIs/types/functions: extends `AutoCloseable`, `S3AStatisticInterface`, and `ChangeTrackerStatistics` integration. Methods record seeks, stream opens/closes, read exceptions, bytes read, read/readFully/vectored starts and completions, discarded vectored bytes, GET/HEAD requests, prefetch bytes, footer parse failure, cache hits, input policy, unbuffering, prefetch operations, file-cache block events, executor acquisition, memory allocation/free, close/open/read counters, policy counters, change tracker stats, and duration trackers for GET and inner stream close.

Control flow: input streams call this at every lifecycle, request, seek, and buffer/prefetch event. Consumers can retrieve `IOStatistics` for reporting.

State/persistence: interface only. Implementations hold live counters/gauges/durations for a stream and may roll them into filesystem-level stats on close.

Dependencies/integration: used throughout S3A read paths, including prefetch streams and `S3ARemoteObject`.

Risks/test signals: high fan-out API means omissions are easy during new read implementations. Tests should cover close accounting, read/seeks, cache/prefetch events, vectored reads, change mismatch, and duration trackers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/S3AInputStreamStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/S3AMultipartUploaderStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/S3AMultipartUploaderStatistics.java

Purpose: statistics contract for the S3A multipart uploader API.

Important APIs/types/functions: extends `Closeable` and `DurationTrackerFactory`. Methods record instantiated uploader, upload started, part put with byte length, upload completed, upload aborted, and abort-uploads-under-path invocation.

Control flow: multipart uploader implementation calls these methods around upload lifecycle and cleanup actions.

State/persistence: interface only.

Dependencies/integration: created by `S3AStatisticsContext.createMultipartUploaderStatistics()` and implemented by `S3AMultipartUploaderStatisticsImpl`.

Risks/test signals: incorrect part byte accounting skews throughput/cost metrics. Tests should assert each multipart lifecycle method maps to the right `Statistic`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/S3AMultipartUploaderStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/S3AStatisticInterface.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/S3AStatisticInterface.java

Purpose: common base for S3A statistic sources that expose IOStatistics and duration tracking.

Important APIs/types/functions: extends `IOStatisticsSource` and `DurationTrackerFactory`.

Control flow: components can accept this interface when they only need statistics retrieval and duration tracker creation.

State/persistence: interface only.

Dependencies/integration: inherited by most S3A statistics contracts.

Risks/test signals: implementations should return non-null IOStatistics unless explicitly documented as an empty/no-op context. Compile-time use enforces duration tracker availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/S3AStatisticInterface.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/S3AStatisticsContext.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/S3AStatisticsContext.java

Purpose: factory and aggregate sink for S3A component-specific statistics.

Important APIs/types/functions: extends `CountersAndGauges`. Factory methods create input stream, committer, block output stream, delegation token, AWS SDK, and multipart uploader statistics objects.

Control flow: filesystem/store setup provides a context; components ask it for specialized statistics instances and also use it directly for aggregate counter/gauge/duration events.

State/persistence: interface only. Implementations may bind to live filesystem instrumentation or no-op contexts.

Dependencies/integration: implemented by `BondedS3AStatisticsContext` and `EmptyS3AStatisticsContext`.

Risks/test signals: wrong context binding can drop or double-count metrics. Tests should verify new instances are wired to filesystem instrumentation and empty context returns safe no-op instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/S3AStatisticsContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/StatisticTypeEnum.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/StatisticTypeEnum.java

Purpose: enum describing statistic value categories.

Important APIs/types/functions: values are `TYPE_COUNTER`, `TYPE_DURATION`, `TYPE_GAUGE`, and `TYPE_QUANTILE`.

Control flow: none in this file; other metadata/config code can use these values to classify statistics.

State/persistence: static enum constants only.

Dependencies/integration: part of S3A statistics API.

Risks/test signals: adding/removing enum values affects metadata consumers. Tests should cover mappings from `Statistic` definitions to these categories where used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/StatisticTypeEnum.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/StatisticsFromAwsSdk.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/StatisticsFromAwsSdk.java

Purpose: sink interface for metrics emitted by AWS SDK v2 metric publishers.

Important APIs/types/functions: methods update AWS request count, retry count, throttle exception count, API/service request time, client execute time, request marshalling time, signing time, and response processing time.

Control flow: `AwsStatisticsCollector.publish()` maps nested AWS metric collections into these callbacks.

State/persistence: interface only.

Dependencies/integration: implemented by `StatisticsFromAwsSdkImpl`; produced by `S3AStatisticsContext.newStatisticsFromAwsSdk()`.

Risks/test signals: SDK metric naming changes can stop callbacks from firing. Tests should feed synthetic metric collections and verify request/retry/throttle/duration counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/StatisticsFromAwsSdk.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/AbstractS3AStatisticsSource.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/AbstractS3AStatisticsSource.java

Purpose: base class for S3A statistics implementations backed by an `IOStatisticsStore`.

Important APIs/types/functions: `getIOStatistics()` returns the store; protected `setIOStatistics()` binds it; `incCounter()`, `incCounter(name,value)`, `incGauge()`, `lookupCounterValue()`, `lookupGaugeValue()`, and `trackDuration()` delegate to the store.

Control flow: subclasses construct/configure an `IOStatisticsStore`, call `setIOStatistics()`, then use helper methods to update metrics.

State/persistence: stores one mutable in-memory `IOStatisticsStore` reference. No external persistence.

Dependencies/integration: Hadoop `IOStatisticsStore`, `IOStatisticsSource`, and `DurationTrackerFactory`.

Risks/test signals: `setIOStatistics()` must be called before helpers are used. Tests should cover null/uninitialized misuse in subclasses, counter/gauge lookups, duration tracker creation, and `toString()` diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/AbstractS3AStatisticsSource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/AwsStatisticsCollector.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/AwsStatisticsCollector.java

Purpose: AWS SDK v2 `MetricPublisher` that translates SDK metric collections into S3A statistics callbacks.

Important APIs/types/functions: constructor accepts `StatisticsFromAwsSdk`. `publish(MetricCollection)` recursively flattens child metric collections, maps `CoreMetric.RETRY_COUNT` to retry and request counts, counts HTTP 429 throttles, and forwards durations for API call, service call, marshalling, signing, and unmarshalling. Helper methods `timing()`, `counter()`, and `recurseThroughChildren()` keep extraction generic. `close()` is no-op.

Control flow: AWS SDK calls `publish()` after API calls. The collector walks nested metrics because SDK metrics are stored at API call, attempt, and HTTP client levels.

State/persistence: holds final destination collector only; throttling count is local per publish call.

Dependencies/integration: AWS `MetricCollection`, `SdkMetric`, `CoreMetric`, `HttpMetric`, `HttpStatusCode`, and `StatisticsFromAwsSdk`.

Risks/test signals: request count is inferred as retries plus one when retry metric appears; missing retry metric could undercount requests. Tests should build nested metric collections with multiple attempts, throttles, and durations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/AwsStatisticsCollector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/BondedS3AStatisticsContext.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/BondedS3AStatisticsContext.java

Purpose: real `S3AStatisticsContext` bonded to filesystem instrumentation and per-filesystem instance statistics.

Important APIs/types/functions: constructor accepts `S3AFSStatisticsSource`, which supplies `S3AInstrumentation` and `FileSystem.Statistics`. Factory methods create instrumentation-backed input stream, committer, block output, delegation token, AWS SDK, and multipart uploader statistics. Counter/gauge/quantile/duration methods forward to instrumentation. `trackDuration()` delegates to the instrumentation duration tracker.

Control flow: the filesystem creates this context and hands it to S3A components. Components create specialized stats objects or record aggregate events, all routed into shared instrumentation.

State/persistence: holds the statistics source reference; actual mutable metric state resides in `S3AInstrumentation` and filesystem statistics.

Dependencies/integration: depends on `S3AInstrumentation`, `FileSystem.Statistics`, `Statistic`, and implementation classes such as `StatisticsFromAwsSdkImpl` and `S3AMultipartUploaderStatisticsImpl`.

Risks/test signals: source methods must return live instrumentation. Tests should verify each factory binds counters to the same source, counter/gauge deltas reach instrumentation, and durations close correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/BondedS3AStatisticsContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/CountingChangeTracker.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/CountingChangeTracker.java

Purpose: simple `ChangeTrackerStatistics` implementation backed by an `AtomicLong`.

Important APIs/types/functions: constructors accept an existing `AtomicLong` or allocate one. `versionMismatchError()` increments the counter. `getVersionMismatches()` returns the current value.

Control flow: change tracking code calls the increment method on mismatch; diagnostics read the count.

State/persistence: in-memory atomic counter only. Thread-safe increments.

Dependencies/integration: implements `ChangeTrackerStatistics`; used by empty/no-op stats and can be embedded in stream statistics.

Risks/test signals: low risk. Tests should verify external counter sharing, default zero value, increments, and thread-safe behavior if concurrent change checks are possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/CountingChangeTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/EmptyS3AStatisticsContext.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/EmptyS3AStatisticsContext.java

Purpose: no-op `S3AStatisticsContext` for tests and components that require a statistics context without binding to a filesystem.

Important APIs/types/functions: exposes singleton empty input stream, committer, output stream, delegation token, and AWS SDK statistics. Context-level counter/gauge/quantile/duration methods do nothing. Nested empty implementations satisfy each statistics interface, return zero counts, empty IOStatistics or null where documented by the implementation, and stub duration trackers. `EmptyMultipartUploaderStatistics` is public and no-op.

Control flow: callers can create stats objects and invoke any method safely; no metrics are retained except `getChangeTrackerStatistics()` returns a new `CountingChangeTracker` for input streams.

State/persistence: singleton no-op instances are static. No external persistence and effectively no mutable metrics beyond per-call new change trackers.

Dependencies/integration: uses Hadoop `emptyStatistics()` and `stubDurationTracker()` plus all S3A statistics interfaces.

Risks/test signals: no-op behavior can hide missing real context in production if used accidentally. Tests should confirm every interface method is implemented, returns safe zero/stub values, and close methods do not throw.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/EmptyS3AStatisticsContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/S3AMultipartUploaderStatisticsImpl.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/S3AMultipartUploaderStatisticsImpl.java

Purpose: real multipart uploader statistics implementation that maps uploader events to S3A `Statistic` counters and duration tracking.

Important APIs/types/functions: constructor accepts increment callback and duration tracker factory. Private `inc(Statistic,long)` forwards increments. Lifecycle methods increment instantiated, started, part byte/count, completed, aborted, and abort-under-path statistics. `trackDuration()` delegates to the duration tracker factory. `close()` is no-op.

Control flow: multipart uploader calls event methods; the implementation translates each event into one or more aggregate statistic updates.

State/persistence: holds callbacks only; metric state lives in the destination instrumentation.

Dependencies/integration: `Statistic`, `BiConsumer<Statistic,Long>`, and `DurationTrackerFactory`.

Risks/test signals: wrong statistic mapping affects user-visible counters. Tests should mock callbacks and verify exact statistics/counts for each event, especially part length bytes and count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/S3AMultipartUploaderStatisticsImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/StatisticsFromAwsSdkImpl.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/StatisticsFromAwsSdkImpl.java

Purpose: concrete AWS SDK statistics sink that records SDK counters and durations into a `CountersAndGauges` destination.

Important APIs/types/functions: constructor stores `CountersAndGauges`. Update methods increment request, retry, and throttle counters. Duration methods record request, client execute, marshalling, signing, and response processing durations as successful events. Static `mapErrorStatusCodeToStatisticName(int)` maps HTTP error status classes/specific statuses to S3A statistic names.

Control flow: `AwsStatisticsCollector` invokes this sink as metrics arrive from AWS SDK. This implementation translates events into `Statistic` keys.

State/persistence: holds destination reference only.

Dependencies/integration: depends on `CountersAndGauges`, `Statistic`, and Java `Duration`.

Risks/test signals: status-code mapping and duration statistic selection must match documented S3A metrics. Tests should cover request/retry/throttle increments, duration recording, and 4xx/5xx status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/StatisticsFromAwsSdkImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/package-info.java

Purpose: package documentation for internal S3A statistics implementations.

Important APIs/types/functions: no executable APIs; annotations mark the implementation package private/unstable.

Control flow: none.

State/persistence: none.

Dependencies/integration: groups concrete statistics contexts and AWS metric collectors.

Risks/test signals: no runtime risk; package visibility/documentation should remain consistent with private implementation intent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/package-info.java

Purpose: package documentation for S3A statistics interfaces.

Important APIs/types/functions: no executable APIs. It explains the interface/implementation package split and marks APIs private/unstable.

Control flow: none.

State/persistence: none.

Dependencies/integration: describes contracts used by streams, committers, delegation tokens, AWS SDK collectors, and output streams.

Risks/test signals: no runtime risk; documentation should match whether any extension points become public.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/BucketTool.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/BucketTool.java

Purpose: S3A administrative CLI subcommand for bucket operations, currently focused on creating buckets including S3 Express directory buckets.

Important APIs/types/functions: extends `S3GuardTool`; command name `bucket`; supports `-create`, `-region`, `-endpoint`, and `-zone`. `run()` parses exactly one S3A URL, validates scheme, requires `-create`, strips bucket-specific overrides, disables bucket probe and out-of-span audit rejection for creation, propagates endpoint/region, initializes an S3A filesystem, builds `CreateBucketConfiguration`, handles S3 Express zone/directory bucket settings, gets an AWS `S3Client`, and calls `createBucket()` through `Invoker.once()`. `removeBucketOverrides()` unsets bucket override keys for supplied global options.

Control flow: CLI parse -> validate options -> prepare configuration to avoid probing nonexistent bucket -> instantiate filesystem -> build request based on S3 Express capability -> create bucket -> close filesystem.

State/persistence: mutates the provided `Configuration` by unsetting/setting keys. Remote side effect is creation of an S3 bucket. No local persistence.

Dependencies/integration: AWS SDK S3 bucket creation models, S3A filesystem internals, S3 Express helpers, audit constants, network endpoint checks, and `DurationInfo`.

Risks/test signals: bucket creation is remote and irreversible without cleanup; probe disabling is required for nonexistent buckets; S3 Express zone rules are strict. Tests should cover URL scheme validation, missing create flag, override removal, probe failure mapping, S3 Express zone required/forbidden cases, and request fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/BucketTool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/MarkerTool.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/MarkerTool.java

Purpose: administrative tool to audit or clean surplus S3 directory markers under a path.

Important APIs/types/functions: extends `S3GuardTool`; supports mutually exclusive `-audit` and `-clean`, `-min`, `-max`, `-limit`, `-out`, and `-verbose`. `run()` parses options, resolves filesystem/path, executes a scan, optionally writes surplus marker paths to a UTF-8 file, and returns/throws based on `ScanResult.finish()`. `execute()` binds S3A FS, qualifies target, verifies existence, creates `MarkerToolOperations`, and calls `scan()`. `ScanResult` and `MarkerPurgeSummary` capture outcomes. `scanDirectoryTree()` lists objects and feeds `DirMarkerTracker`. `purgeMarkers()` shuffles surplus marker keys and bulk-deletes pages. `ScanArgs` and builder support programmatic execution.

Control flow: scan lists objects from a key prefix, retries with trailing slash after certain bad requests, classifies directory statuses as markers and files as files, reports surplus/leaf markers, optionally purges surplus markers, validates min/max marker count for audit, and handles listing limit interruption.

State/persistence: holds output stream, verbosity, store context, and operations during execution. Clean mode mutates remote S3 object state by deleting marker objects. `-out` writes a local file containing surplus marker paths.

Dependencies/integration: `DirMarkerTracker`, S3A `StoreContext`, `S3AFileStatus`, `S3ALocatedFileStatus`, AWS object identifiers, bulk delete settings, retry annotations, and `MarkerToolOperations`.

Risks/test signals: clean mode is destructive; randomized delete order affects deterministic tests unless mocked; min/max defaults make audit fail when any surplus marker is found unless max is raised. Tests should cover option parsing, audit/clean exclusivity, missing/wrong paths, listing fallback with trailing slash, limit interruption, leaf versus surplus classification, output file generation, and paged delete summaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/MarkerTool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/MarkerToolOperations.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/MarkerToolOperations.java

Purpose: narrow operations interface required by `MarkerTool`, decoupling the tool from the full S3A operation callback surface.

Important APIs/types/functions: `listObjects(Path,String)` returns a `RemoteIterator<S3AFileStatus>` including the key itself if found. `removeKeys(List<ObjectIdentifier>,boolean)` deletes S3 keys and can throw translated IO, AWS service, invalid request, or multi-delete exceptions. Retry annotations document mixed/translated retry behavior.

Control flow: `MarkerTool` calls `listObjects()` during scan and `removeKeys()` during purge.

State/persistence: interface only. Implementations may mutate remote S3 state on deletion.

Dependencies/integration: AWS SDK `ObjectIdentifier`, Hadoop `RemoteIterator`, S3A status/exception types, and retry annotations.

Risks/test signals: incorrect list semantics can miss root/path marker objects; delete behavior must reject root mistakes. Tests should mock this interface to drive marker scan and purge behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/MarkerToolOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/MarkerToolOperationsImpl.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/MarkerToolOperationsImpl.java

Purpose: adapter from the broad S3A `OperationCallbacks` interface to the narrow `MarkerToolOperations` interface.

Important APIs/types/functions: constructor stores `OperationCallbacks`; `listObjects()` delegates to `operationCallbacks.listObjects()`; `removeKeys()` delegates to `operationCallbacks.removeKeys(keysToDelete, deleteFakeDir)`.

Control flow: created by S3A filesystem/tooling and used by `MarkerTool` for scan and cleanup operations.

State/persistence: holds callback reference only.

Dependencies/integration: `OperationCallbacks`, S3A status types, AWS service exceptions, and multi-object delete exceptions.

Risks/test signals: adapter is thin; tests should verify exact delegation and exception propagation, especially `deleteFakeDir` flag preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/MarkerToolOperationsImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/package-info.java

Purpose: package documentation for S3A command-line tools independent of S3Guard internals.

Important APIs/types/functions: no executable APIs; package annotations mark private/unstable status.

Control flow: none.

State/persistence: none.

Dependencies/integration: groups bucket and marker administration tools.

Risks/test signals: no runtime risk; ensure package documentation remains aligned with supported CLI commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/package-info.java -->
