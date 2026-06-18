# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ReadaheadPool.java

Purpose: `ReadaheadPool` manages a singleton daemon thread pool that issues asynchronous POSIX readahead hints on file descriptors through Hadoop native IO, helping sequential readers warm the OS page cache.

Important APIs and types: `getInstance()` lazily returns a singleton only when `NativeIO.isAvailable()`. `resetInstance()` shuts down the singleton for tests. `readaheadStream(...)` decides when to submit the next request based on current position, configured readahead length, maximum offset, and the previous request. `submitReadahead(...)` enqueues a `ReadaheadRequestImpl`. The `ReadaheadRequest` interface exposes `cancel`, `getOffset`, and `getLength`.

Control flow: callers repeatedly pass their current read position and prior request. If readahead is disabled or no bytes remain, no request is made. Once the reader reaches halfway through the prior readahead window, the prior request is canceled and a new request is submitted for `min(readaheadLength, maxOffsetToRead - curPos)`. Worker threads call `posixFadviseIfPossible(..., POSIX_FADV_WILLNEED)` unless canceled or the descriptor is invalid.

State and persistence: process-wide state is the singleton and its `ThreadPoolExecutor` with a bounded queue and discard-oldest rejection policy. Each request stores identifier, file descriptor, offset, length, and volatile cancellation flag. There is no durable persistence.

Dependencies and integration points: depends on `NativeIO.POSIX`, POSIX fadvise constants, Guava `ThreadFactoryBuilder`, Hadoop `Preconditions`, SLF4J, and Java executors. It integrates with local file readers that can expose `FileDescriptor`s.

Risks and test signals: risks include queue pressure silently discarding oldest work, races with descriptor close/reuse, native IO unavailability returning null singleton, cancellation not removing queued tasks, and precondition failure if caller passes `curPos > maxOffsetToRead`. Tests should cover singleton availability/reset, trigger threshold behavior, max-offset clipping, cancellation before close, native failure logging, disabled/zero lengths, and executor rejection under load.
