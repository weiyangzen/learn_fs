<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/SharedFileDescriptorFactory.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/SharedFileDescriptorFactory.c

## Purpose
`SharedFileDescriptorFactory.c` creates anonymous, pre-sized file descriptors backed by temporary files and deletes stale temporary files for Hadoop shared-memory use cases.

## Important APIs, Types, and Functions
JNI exports are `deleteStaleTemporaryFiles0()` and `createDescriptor0()`. Internal helper `zero_fully()` writes zero-filled buffers to size the file. A static `pthread_mutex_t g_rand_lock` serializes `rand()` usage.

## Control Flow
Stale cleanup opens a target directory, scans entries, and unlinks files whose names start with the supplied prefix. Descriptor creation builds a path from directory, prefix, and random suffix; opens it with `O_CREAT | O_EXCL | O_RDWR`; retries on name collision or interrupt; unlinks the file immediately after opening; writes zeroes up to requested length; seeks back to start; and wraps the fd in a Java `FileDescriptor`.

## State and Persistence
Only the random mutex is static. Created files are unlinked after opening, so storage persists only as long as the descriptor remains open. The fd is returned to Java for lifecycle management.

## Dependencies and Integration Points
It depends on Unix filesystem APIs, `file_descriptor`, and exception helpers. It is compiled only under `UNIX` and supports Java `SharedFileDescriptorFactory`.

## Risks and Edge Cases
On `EEXIST`, the code retries without changing `rnd`, which can spin forever if the same generated path persists. `rand()` is not seeded here. `zero_fully()` does not handle `write()` returning zero. Error messages sometimes use the directory path instead of the full target path.

## Test Signals
Tests should cover descriptor creation length/content, unlink-after-open semantics, stale cleanup by prefix, collision handling, path-too-long errors, interrupted writes/opens, and close cleanup from Java.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/SharedFileDescriptorFactory.c -->
