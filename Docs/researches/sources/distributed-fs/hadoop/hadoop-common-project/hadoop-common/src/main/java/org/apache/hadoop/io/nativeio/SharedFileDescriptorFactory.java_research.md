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
