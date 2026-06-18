# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FutureDataInputStreamBuilder.java

Purpose: `FutureDataInputStreamBuilder` defines the asynchronous open builder contract for `FSDataInputStream`.

Important APIs: inherited `FSBuilder` option methods, `build()` returning `CompletableFuture<FSDataInputStream>`, and default `withFileStatus(@Nullable FileStatus)`.

Control flow and state: this is an interface; implementations own option state. The default `withFileStatus` is a no-op so implementations opt in to using caller-provided status hints.

Dependencies and integration: used by `FileSystem.openFile`, `FileContext` opens, and utility copy methods that provide file length/status hints for object stores and async implementations.

Risks: `must` options are expected to throw for unsupported/unknown options, while `opt` options may be ignored; implementations must preserve that distinction. A provided `FileStatus` can become stale, so implementations must decide whether to trust it.

Test signals: async build success/failure paths, option validation semantics, no-op default `withFileStatus`, stale status handling in implementations, and cancellation/exception propagation through `CompletableFuture`.
