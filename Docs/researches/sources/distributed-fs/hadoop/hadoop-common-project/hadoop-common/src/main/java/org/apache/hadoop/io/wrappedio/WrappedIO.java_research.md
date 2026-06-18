# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/wrappedio/WrappedIO.java

## Purpose

`WrappedIO` is a public, unstable, reflection-friendly facade over newer Hadoop filesystem APIs. It lets downstream libraries compile against older Hadoop versions while dynamically invoking APIs such as bulk delete, `openFile()`, path/stream capabilities, enclosing roots, and positioned ByteBuffer reads when available.

## Important APIs, control flow, and state

All methods are static and the class has no mutable state. Bulk delete methods create a `BulkDelete` from a `FileSystem`, use try-with-resources, and convert checked IO exceptions to `UncheckedIOException` through `FunctionalIO.uncheckIOExceptions()`. Capability probes call `PathCapabilities.hasPathCapability()` or `StreamCapabilities.hasCapability()`, returning false for IO failures or non-capable objects. `fileSystem_openFile()` configures a `FutureDataInputStreamBuilder` with read policy, file status, length, and arbitrary options, then blocks on `FutureIO.awaitFuture(builder.build())`. `byteBufferPositionedReadable_readFully()` requires `ByteBufferPositionedReadable`; availability recursively unwraps `FSDataInputStream` and checks `StreamCapabilities.PREADBYTEBUFFER`.

## Dependencies and integration points

The dynamic counterpart is `DynamicWrappedIO`, which loads these static methods through `DynMethods`. Filesystem contract tests and external storage libraries use this layer to access cloud-optimized open options and bulk delete without hard linkage to newer APIs.

## Risks and test signals

The wrapper intentionally maps some checked IO failures to unchecked exceptions or false capability probes, so callers must understand which errors are observable. Bulk delete is non-atomic and idempotence can delete newly recreated objects under retried paths. ByteBuffer availability depends both on interface type and capability declaration. `TestWrappedIO` covers class resolution, method lookup, open-file behavior, ByteBuffer positioned reads, filesystem IO statistics access, and missing-class fallback behavior; bulk delete contract tests exercise the delete wrappers.
