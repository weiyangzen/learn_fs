# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/jclasses.h

## Purpose
This header declares the `CachedJavaClass` enum, cache initialization/accessor functions, and string constants for Java and Hadoop class names used by JNI call sites in `libhdfs`.

## Important APIs, Control Flow, and State
`CachedJavaClass` enumerates Hadoop configuration, path, filesystem, stream, status, permission, read-statistics, async-builder, domain-socket, URI, byte-buffer, enum-set, exception-utils, and CompletableFuture classes, with `NUM_CACHED_CLASSES` as the count sentinel. `initCachedClasses(JNIEnv*)` is documented as idempotent and thread-safe; `getJclass` and `getClassName` retrieve the cached global reference and canonical slash-separated class name.

## Dependencies and Integration Points
The header depends on `<jni.h>` and is used by `jclasses.c`, `jni_helper.c`, and libhdfs operation implementations that need cached method calls. Macro constants provide compatibility for older code paths that call `FindClass` directly.

## Risks and Test Signals
Adding an enum requires updating initialization logic and potentially every switch/index consumer. The macro names and enum values are internal but widely shared. Tests should assert `NUM_CACHED_CLASSES` matches initialized entries, all cached classes resolve under the supported Hadoop classpath, and cached and macro class names stay consistent where both exist.
