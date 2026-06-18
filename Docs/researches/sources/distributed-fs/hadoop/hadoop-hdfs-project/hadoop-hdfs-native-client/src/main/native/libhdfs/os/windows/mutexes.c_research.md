# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/windows/mutexes.c

## Purpose
This Windows implementation supplies global `libhdfs` mutexes using `CRITICAL_SECTION`.

## Important APIs, Control Flow, and State
`jvmMutex` and `jclassInitMutex` are global critical sections. Because there is no simple static critical-section initializer, `initializeMutexes` calls `InitializeCriticalSection` for both and is registered as a CRT global initializer through the `.CRT$XCU` section. `mutexLock` and `mutexUnlock` call `EnterCriticalSection` and `LeaveCriticalSection`, returning 0.

## Dependencies and Integration Points
It depends on `<windows.h>` and `os/mutexes.h`. The implementation supports the same bootstrap synchronization used by `jni_helper.c` and `jclasses.c`.

## Risks and Test Signals
Correct CRT initializer retention is the main risk, especially across MSVC versions and static/shared library modes. Unlike POSIX wrappers, lock failures are not reported. Tests should build and load the DLL, call into libhdfs before any explicit initialization, and stress concurrent JVM/bootstrap access.
