# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/exception.h

## Purpose
`exception.h` documents and declares the libhdfs JNI exception handling contract: clear Java exceptions promptly, return local `jthrowable` references to callers, translate handled exceptions to errno, and store last exception diagnostics in thread-local state.

## Important APIs and definitions
The header defines print-suppression flags `PRINT_EXC_ALL`, `NOPRINT_EXC_FILE_NOT_FOUND`, `NOPRINT_EXC_ACCESS_CONTROL`, `NOPRINT_EXC_UNRESOLVED_LINK`, `NOPRINT_EXC_PARENT_NOT_DIRECTORY`, and `NOPRINT_EXC_ILLEGAL_ARGUMENT`. It declares `getExceptionInfo`, `printExceptionAndFreeV`, `printExceptionAndFree`, `printPendingExceptionAndFree`, `getPendingExceptionAndClear`, and `newRuntimeError`, with printf-format checking where available.

## Control flow and integration
libhdfs JNI wrappers call helper functions such as `invokeMethod`; when those helpers return a `jthrowable`, callers pass it to `printExceptionAndFree` with contextual text and optional no-print flags, then propagate the returned errno through `errno` and conventional C return values. Functions that detect a still-pending JNI exception call `printPendingExceptionAndFree` or `getPendingExceptionAndClear`.

## State and persistence
The header states the key state rule: root cause and stack trace strings from the last exception on a thread are stored in thread-local state and read later by public libhdfs APIs. The header itself owns no storage.

## Dependencies
It includes `platform.h`, JNI, stdio, stdlib, stdarg, search, and errno. The implementation depends on JNI helper and class cache modules.

## Risks
The correctness of the whole libhdfs C API depends on this convention. Leaving pending Java exceptions uncleared can cause undefined JNI behavior in later calls, while freeing an exception too early would lose diagnostics. No-print flags reduce log noise but can also hide unexpected recurrent failures if used too broadly.

## Test signals
Expected-error tests in threaded and ops coverage validate errno and TLS diagnostics. Compilation with `TYPE_CHECKED_PRINTF_FORMAT` catches mismatched format arguments in exception-context calls.
