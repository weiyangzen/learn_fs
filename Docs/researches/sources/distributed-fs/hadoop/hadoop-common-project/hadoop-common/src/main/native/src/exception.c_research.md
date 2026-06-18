<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/exception.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/exception.c

## Purpose
`exception.c` centralizes small JNI exception-construction helpers used by Hadoop native code. It lets native call sites build Java exceptions without leaving an intermediate pending JNI exception and provides `terror()` as the common errno-to-text helper.

## Important APIs, Types, and Functions
The exported helpers are `newExceptionV()`, `newException()`, `newRuntimeException()`, `newIOException()`, and `terror()`. `newExceptionV()` does the real work: it locates a Java exception class, resolves the `(String)` constructor, formats a `printf`-style message with `vsnprintf`, creates the Java string and exception object, clears any construction-time pending JNI exception, and returns the throwable object for the caller to throw. The convenience wrappers bind specific class names or variadic argument handling.

## Control Flow
Callers usually build an exception object and then invoke `Throw`. Formatting first probes the required buffer length with a one-byte stack buffer, allocates heap storage for the final message, and releases local references on exit. If class lookup, constructor lookup, string creation, or object construction fails, the function captures and clears the pending exception so the caller receives a throwable object instead of a still-pending JNI state.

## State and Persistence
The file keeps no persistent state. All allocation is transient per exception creation, and `terror()` returns either `strerror()` output or legacy `sys_errlist` strings depending on platform/glibc feature checks.

## Dependencies and Integration Points
It depends on JNI, C varargs, standard formatting, and Hadoop's `org_apache_hadoop.h` macros. It is consumed by native IO, Unix socket, erasure-code, and security JNI files for consistent Java exception messages.

## Risks and Edge Cases
The helper assumes exception classes expose a one-argument string constructor. `msg = malloc(need + 1)` is not explicitly checked before the second `vsnprintf`, so severe allocation failure is a native crash risk. `terror()` has compatibility branches for glibc and non-glibc behavior; unsupported libc combinations could return less useful messages.

## Test Signals
Useful tests exercise formatted messages, missing class/constructor paths, very long messages, errno text under glibc and musl, and JNI callers that verify no unexpected pending exception remains after helper return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/exception.c -->
