# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/posix/thread_local_storage.c

## Purpose
This POSIX TLS implementation stores per-thread `ThreadLocalState` for `libhdfs`, including the thread's `JNIEnv*` and last Java exception strings, and detaches native threads from the JVM on thread exit.

## Important APIs, Control Flow, and State
`gTlsKey` is lazily created under `jvmMutex` with `pthread_key_create`, using `hdfsThreadDestructor` as the destructor. `threadLocalStorageCreate` mallocs state and initializes exception fields to null. `threadLocalStorageGet` creates the key if needed and reads `pthread_getspecific`; `threadLocalStorageSet` writes with `pthread_setspecific` and destroys state on failure. `hdfsThreadDestructor` gets the `JavaVM` from `JNIEnv`, detaches the current thread, logs failures with Java thread ID/name if possible, frees exception strings, and frees the state.

## Dependencies and Integration Points
It depends on JNI, pthreads, `exception.h`, and `jni_helper.h`. `getJNIEnv` relies on these routines while holding `jvmMutex`.

## Risks and Test Signals
Destructor behavior is delicate because it calls back into JNI during thread teardown. Tests should cover lazy key creation, repeated get/set, thread-exit detach, exception-string freeing, many concurrent threads, and failure handling when Java thread introspection itself throws.
