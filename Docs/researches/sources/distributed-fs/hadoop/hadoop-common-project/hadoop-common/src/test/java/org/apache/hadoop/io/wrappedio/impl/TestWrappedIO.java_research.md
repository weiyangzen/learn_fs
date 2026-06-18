# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/wrappedio/impl/TestWrappedIO.java

## Purpose
`TestWrappedIO` validates dynamic/reflection-based access to newer Hadoop filesystem APIs through `DynamicWrappedIO`, ensuring callers can use open-file, stream capability, byte-buffer positioned reads, and bulk delete features while degrading safely when methods are absent.

## Important APIs, Types, and Functions
The test uses `DynamicWrappedIO`, `DynamicWrappedStatistics`, `WrappedIO.streamCapabilities_hasCapability()`, `FileSystem.openFile` wrappers, `CommonPathCapabilities.BULK_DELETE`, `FS_OPTION_OPENFILE_LENGTH`, `FS_OPTION_OPENFILE_READ_POLICY`, `ByteBufferPositionedReadable` wrappers, and local filesystem contract utilities. Helper `openFile()` delegates to `io.fileSystem_openFile()`, and `map()` builds string option maps.

## Control Flow
Setup initializes the local filesystem contract, wrapped I/O, statistics wrapper, and statistics context. `testOpenFileOperations()` creates a file, opens it through multiple wrapper paths, checks read policy and length options, validates EOF behavior beyond file length, probes stream capabilities, aggregates I/O stats, and performs bulk delete. `testByteBufferPositionedReadable()` verifies direct and wrapped positioned byte-buffer reads when available, otherwise expects unsupported operation. Fallback tests bind to nonexistent or incompatible classes and assert probes return false or operations throw expected exceptions.

## State and Persistence
Temporary files are created through the local filesystem contract and deleted by test cleanup or bulk delete. I/O statistics snapshots are created, aggregated, optionally saved, and logged. Thread-local IOStatisticsContext is reset during setup.

## Dependencies and Integration Points
It integrates local FS contract testing, dynamic binding utilities, stream capabilities, filesystem bulk delete APIs, open-file builder options, and wrapped statistics. This protects compatibility shims used by downstream code that must run against multiple Hadoop versions.

## Risks and Edge Cases
Reflection binding must distinguish missing methods, non-static methods, and unavailable class names. Local filesystem may not support byte-buffer positioned reads, so that branch intentionally accepts unsupported behavior. The EOF validation depends on stream semantics around seeking past known length.

## Test Signals
Signals include successful dynamic method discovery, correct first-byte reads from wrapped open calls, matching stream capability probes, expected EOF and FileNotFound exceptions, positive bulk delete page size, empty bulk delete failures list, and safe fallback behavior when wrapped classes or methods are missing.
