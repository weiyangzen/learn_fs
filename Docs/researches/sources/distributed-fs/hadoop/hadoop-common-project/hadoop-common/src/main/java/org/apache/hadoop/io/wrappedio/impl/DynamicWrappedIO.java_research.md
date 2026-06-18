# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/wrappedio/impl/DynamicWrappedIO.java

## Purpose

`DynamicWrappedIO` is the dynamic binding layer for `WrappedIO`. It locates the wrapper class and selected static methods at runtime using Hadoop's `DynMethods`, then exposes typed methods that either invoke the bound API or fall back to older behavior.

## Important APIs, control flow, and state

Construction loads `org.apache.hadoop.io.wrappedio.WrappedIO`, sets `loaded`, and binds methods for bulk delete, `fileSystem_openFile`, path and stream capability probes, and ByteBuffer positioned reads. `requireAllMethodsAvailable()` is a test helper. Public methods call `checkAvailable()` when the API is mandatory, `available()` when false fallback is acceptable, and `extractIOEs()` to surface checked IO failures from reflective invocation. `openFile()` uses the singleton instance; `openFileOnInstance()` prefers reflected `fileSystem_openFile()` with read policies and file status, otherwise calls classic `fs.open(path)`.

State is immutable after construction: the loaded flag and unbound method handles. The singleton `INSTANCE` gives callers a shared default binding.

## Dependencies and integration points

This class integrates downstream storage code with `WrappedIO` and is tested under `TestWrappedIO` and bulk-delete contract tests. It depends on `BindingUtils`, `DynMethods`, `FileSystem`, `FileStatus`, `FSDataInputStream`, `Path`, and `ByteBuffer`.

## Risks and test signals

Method signatures must match exactly. A notable risk is the binding for `byteBufferPositionedReadable_readFullyAvailable`: the wrapped method returns `boolean`, while this class loads it with `Void.class`, so method availability depends on `BindingUtils` behavior around primitive/boxed return matching and should be covered by `testAllMethodsFound()` and `testByteBufferPositionedReadable()`. Missing classes or methods intentionally degrade to false/unavailable or classic `open()`, but mandatory invocations throw `UnsupportedOperationException`. Reflection can also wrap runtime exceptions, so IO extraction tests are important.
