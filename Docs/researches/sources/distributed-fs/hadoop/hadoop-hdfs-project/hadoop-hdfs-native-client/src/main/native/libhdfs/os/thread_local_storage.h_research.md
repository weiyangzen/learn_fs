# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/thread_local_storage.h

## Purpose
This header defines the cross-platform TLS contract for `libhdfs` per-thread JNI state and optional fast TLS macros.

## Important APIs, Control Flow, and State
When `HAVE_BETTER_TLS` is defined, `THREAD_LOCAL_STORAGE_GET_QUICK` and `THREAD_LOCAL_STORAGE_SET_QUICK` use a static `__thread struct ThreadLocalState *quickTlsEnv` inside the calling function to avoid platform TLS lookup after initialization. `ThreadLocalState` stores `JNIEnv *env`, `lastExceptionStackTrace`, and `lastExceptionRootCause`. The declared API creates state, gets/sets state for the current thread, and destroys state via `hdfsThreadDestructor`.

## Dependencies and Integration Points
It includes `<jni.h>` and is used by `jni_helper.c` plus POSIX/Windows TLS implementations. Public exception accessors depend on the string fields staying valid until replacement or thread teardown.

## Risks and Test Signals
Quick TLS is function-local static TLS, so behavior depends on compiler/linker support and macro expansion sites. The get routine requires external mutual exclusion. Tests should cover builds with and without `HAVE_BETTER_TLS`, per-thread isolation, destructor cleanup, and exception-string lifetime.
