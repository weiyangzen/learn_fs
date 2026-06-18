# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/locks.h

## Purpose
This header defines pluggable global mutex support for libhdfs++ so applications can coordinate access to non-thread-safe shared libraries, especially GSSAPI/Kerberos.

## Important APIs, Control Flow, and State
`Mutex` is an abstract lock/unlock/string interface that may throw `LockFailure`. `LockGuard` is an RAII wrapper that locks in the constructor and unlocks in the destructor. `LockManager` holds process-global mutex pointers, allows a one-time `InitLocks(Mutex *gssapi)`, exposes `getGssapiMutex`, and has test-only reset/default accessors. Static state includes a state mutex, `_finalized`, `gssapiMtx`, and test default mutex.

## Dependencies and Integration Points
Authentication code uses `LockManager::getGssapiMutex` to serialize GSSAPI calls. Applications embedding libhdfs++ can install their own mutex before constructing any `FileSystem`.

## Risks and Test Signals
One-time initialization order is crucial. Failure to acquire locks must become clean status failures, not deadlocks. Tests should cover default initialization, custom mutex install exactly once, concurrent `InitLocks`, throwing mutexes, RAII unlock on exceptions, and test reset isolation.
