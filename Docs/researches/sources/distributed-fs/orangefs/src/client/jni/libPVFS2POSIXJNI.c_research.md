<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/jni/libPVFS2POSIXJNI.c -->
# sources/distributed-fs/orangefs/src/client/jni/libPVFS2POSIXJNI.c

## Purpose

`libPVFS2POSIXJNI.c` implements the native methods for `PVFS2POSIXJNI`, exposing a broad POSIX-like API to Java. It is the low-level bridge used by the Hadoop OrangeFS adapter for metadata, permissions, open/read/write/seek, directory creation, rename/delete, stat/statfs, xattrs, links, and time operations.

## Important APIs, Types, and Functions

The file exports JNI wrappers for `access`, `chmod`, `chown`, `close`, `creat`, `dup`, `faccessat`, `fallocate`, `fchmod*`, `fchown*`, `fdatasync`, `fsync`, `ftruncate`, `open`, `openWithHints`, `openat`, `pread`, `pwrite`, `read`, `write`, `lseek`, `mkdir`, `mkdirTolerateExisting`, `rename`, `rmdir`, `stat`, `lstat`, `fstat`, `statfs`, `fstatfs`, `statvfs`, `unlink`, `utime`, `utimes`, symlink/link APIs, and xattr list/remove APIs. Helpers `fill_stat`, `fill_statfs`, and related object construction translate native structs into Java `Stat`, `Statfs`, and `Statvfs` objects. `fillPVFS2POSIXJNIFlags` publishes native constants into Java.

## Control Flow

Each JNI function converts Java strings or byte arrays into native pointers, calls the corresponding libc/POSIX or OrangeFS-interposed function, checks failures with common macros, releases Java resources, and returns primitive values or Java wrapper objects. `openWithHints` adds OrangeFS-specific layout/striping hints before opening a file. `mkdirTolerateExisting` treats an existing directory as success to support recursive Hadoop `mkdirs` races.

## State, Persistence, and Concurrency

The file itself stores no global filesystem state, but it mutates OrangeFS/POSIX persistent state through file descriptors, paths, metadata, xattrs, and timestamps. File descriptor lifetime is controlled by Java callers. Native `errno` is process/thread-local but diagnostics are printed to stderr. Concurrent Java calls can operate on shared file descriptors if the caller shares them.

## Dependencies and Integration Points

It depends on JNI headers, POSIX headers, OrangeFS client interception/libraries available at runtime, and Java classes matching the native method names and signatures. Hadoop `OrangeFileSystem` uses this layer for `stat`, `mkdirTolerateExisting`, `chmod`, `rename`, `unlink`, `isDir`, and stream/file operations.

## Risks and Test Signals

Risks include Java/native signature drift, resource leaks on missing `ReleaseStringUTFChars`/descriptor close paths, partial read/write handling, platform differences in struct fields, `errno` reuse, and unsupported operations on OrangeFS. Tests should call every wrapper with success and failure cases, verify `Stat`/`Statfs` field mapping, exercise large reads/writes and xattrs, run under leak sanitizers where possible, and validate Hadoop operations that depend on `mkdirTolerateExisting` and `openWithHints`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/jni/libPVFS2POSIXJNI.c -->
