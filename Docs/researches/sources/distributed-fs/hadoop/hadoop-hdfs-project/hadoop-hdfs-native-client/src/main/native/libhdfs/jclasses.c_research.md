# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/jclasses.c

## Purpose
`jclasses.c` initializes and serves cached JNI `jclass` global references for Java classes frequently used by `libhdfs`. It avoids repeated `FindClass` calls and centralizes the mapping from `CachedJavaClass` enum values to JVM class names.

## Important APIs, Control Flow, and State
The global `cachedJavaClasses` array stores a `jclass` and class-name string per enum entry. `initCachedClasses` is guarded by `jclassInitMutex` and `jclassesInitialized`, populates class-name strings, then loops through all entries calling `initCachedClass`. `initCachedClass` finds a local class, promotes it to a global reference, clears and returns any pending exception, and deletes the local reference. `getJclass` and `getClassName` are simple indexed accessors used by `invokeMethod` and constructor helpers.

## Dependencies and Integration Points
It depends on JNI, `exception.h` for pending-exception handling, `jni_helper.h` for local reference cleanup, and `os/mutexes.h` for cross-platform initialization locking. It must run after a JVM exists and before cached-class method invocation.

## Risks and Test Signals
The cache is process-long and has no eviction or global-ref cleanup, which is intentional but makes startup failures sticky: a missing Java dependency aborts class initialization before setting `jclassesInitialized`. The enum order must match the array use. Tests should verify idempotent concurrent initialization, failure on missing classes, valid global refs after local ref deletion, and all enum values having class names.
