# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/nativeio/TestSharedFileDescriptorFactory.java

## Purpose
`TestSharedFileDescriptorFactory` validates creation, cleanup, and directory fallback behavior for Hadoop's shared file descriptor factory.

## Important APIs, Types, and Functions
The suite uses `SharedFileDescriptorFactory.getLoadingFailureReason()`, `SharedFileDescriptorFactory.create(prefix, paths)`, `createDescriptor(name, length)`, and `getPath()`. Helpers create temporary remainder files and use `FileUtil.fullyDelete()`.

## Control Flow
`setup()` skips when the factory failed to load. `testReadAndWrite()` creates a descriptor-backed input stream, wraps the same descriptor in an output stream, writes a byte, seeks the input channel to zero, and verifies readback. `testCleanupRemainders()` creates stale prefixed files and asserts factory construction removes them on Unix native I/O. `testDirectoryFallbacks()` first verifies all-bad directories fail, then supplies a good fallback path and checks it is selected.

## State and Persistence
Temporary directories live under the common test directory. Created descriptor files and stale remainder files are deleted by the factory or explicit cleanup. No durable state is intended.

## Dependencies and Integration Points
The file depends on `NativeIO.isAvailable()`, Apache Commons `SystemUtils.IS_OS_UNIX`, Hadoop `Path.SEPARATOR`, `FileUtil`, and the native shared descriptor implementation used by components needing shared memory or mmap-backed descriptors.

## Risks and Edge Cases
Tests assume root directory is permission denied for descriptor creation. Cleanup behavior is Unix-gated. Descriptor lifecycle must avoid closing one stream before the other in a way that invalidates the shared FD unexpectedly.

## Test Signals
Signals are successful byte write/read through a shared descriptor, removal of stale prefix remainders, correct IOException when all paths are unusable, and selection of the first usable fallback directory.
