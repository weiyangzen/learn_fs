# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/exception.c

## Purpose
`exception.c` centralizes libhdfs conversion of Java exceptions into POSIX-style errno values, stderr diagnostics, and thread-local root-cause/stack-trace strings.

## Important APIs and data
`gExceptionInfo` maps Java class names to no-print flags and errno values for file-not-found, access control, unresolved link, parent-not-directory, illegal argument, out-of-memory, safe mode, already-exists, quota exceeded, unsupported operation, and lease expired. Public functions include `getExceptionInfo`, `printExceptionAndFreeV`, `printExceptionAndFree`, `printPendingExceptionAndFree`, `getPendingExceptionAndClear`, and `newRuntimeError`. `getExceptionUtilString` calls Hadoop `ExceptionUtils` methods to extract root cause and stack trace strings.

## Control flow
Callers pass either an explicit `jthrowable` or rely on the pending JNI exception. The code determines the Java exception class, maps it to errno and print suppression policy, fetches root cause and stack trace, saves both in thread-local storage through `setTLSExceptionStrings`, optionally prints the supplied context plus exception details, deletes the local exception reference, and returns the mapped errno.

`printPendingExceptionAndFree` checks `ExceptionOccurred`, clears it if present, and delegates to the varargs implementation. `newRuntimeError` formats a C message into a Java `RuntimeException`, returning pending OOM exceptions if string or object construction fails.

## State and persistence
The persistent effect is per-thread exception diagnostic state exposed by `hdfsGetLastExceptionRootCause` and `hdfsGetLastExceptionStackTrace` in `hdfs.c`. The mapping table is static read-only process state. JNI local references are explicitly destroyed.

## Dependencies
It depends on `jni_helper` for method invocation, class-name extraction, and C string conversion; `jclasses` for `ExceptionUtils`; `platform.h`; and thread-local exception string storage from the JNI helper layer.

## Risks
Unknown exception classes map to `EINTERNAL`, which may hide more specific Java failures. `getExceptionInfo` uses `strstr(gExceptionInfo[i].name, excName)`, while `printExceptionAndFreeV` uses exact class-name comparison; callers passing partial names can see different behavior. If `ExceptionUtils` itself fails, diagnostics are degraded but the original exception is still consumed. Root cause and stack trace strings must be managed correctly by TLS storage to avoid leaks across repeated failures.

## Test signals
`test_libhdfs_threaded.c` checks TLS root cause and stack trace after an expected missing-file failure. Many tests depend on specific errno mappings such as `ENOENT`, `EACCES`, `EINVAL`, and `EPROTONOSUPPORT` for assertions and expected failure paths.
