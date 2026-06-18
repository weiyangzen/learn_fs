# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/libhdfs_getjni_test.cc

## Purpose

This test verifies that repeated libhdfs JNI initialization failures do not crash the process.

## Important APIs, types, and functions

The file overrides JNI runtime entry points `JNI_GetDefaultJavaVMInitArgs()`, `JNI_CreateJavaVM()`, and `JNI_GetCreatedJavaVMs()` to always fail. `TestRepeatedGetJNIFailsButNoCrash` calls `hdfsConnectNewInstance(NULL, 0)` twice and expects null both times.

## Control flow, state, and persistence

The test links libhdfs without the JVM library so these local JNI symbols intercept initialization. Both connect attempts fail, but the important behavior is that libhdfs cleans up or reuses failure state safely enough to retry without a crash. No filesystem state persists.

## Dependencies and integration points

It depends on gmock, `hdfs/hdfs.h`, JNI headers, and CMake's special `HDFS_STATIC_LIBS_NO_JVM` setup. It exercises legacy libhdfs behavior used alongside libhdfspp wrapper tests.

## Risks and test signals

The test protects against stale JVM initialization state after failure. Link setup is delicate: if real JVM symbols win, the test no longer exercises the intended path. Passing indicates failure handling is repeatable, not that JNI can successfully initialize.
