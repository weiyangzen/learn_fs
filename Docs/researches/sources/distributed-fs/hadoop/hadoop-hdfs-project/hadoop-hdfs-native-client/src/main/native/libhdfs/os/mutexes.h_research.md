# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/mutexes.h

## Purpose
`mutexes.h` defines the cross-platform synchronization abstraction used by `libhdfs` during bootstrap. It declares the singleton JVM mutex, Java-class cache initialization mutex, and lock/unlock wrappers.

## Important APIs, Control Flow, and State
The file exposes `extern mutex jvmMutex` and `extern mutex jclassInitMutex`, where `mutex` is provided by the selected platform header. `jvmMutex` protects JVM creation, attachment, and TLS access; `jclassInitMutex` protects idempotent cached class initialization. `mutexLock` and `mutexUnlock` return platform error codes and log failures in implementations.

## Dependencies and Integration Points
The header includes `platform.h`, which resolves to POSIX pthread types or Windows `CRITICAL_SECTION`. It is consumed by `jni_helper.c`, `jclasses.c`, and platform-specific mutex implementations.

## Risks and Test Signals
The comment notes there is no user-called library initialization function, so static initialization is required on every platform. Tests should stress concurrent first calls into `getJNIEnv` and `initCachedClasses`, verify recursive locking where needed by JVM bootstrap, and build both POSIX and Windows implementations.
