# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/jni_helper.h

## Purpose
This header publishes internal JNI helper contracts for string conversion, local-reference cleanup, method/constructor invocation, method ID lookup, object class introspection, JVM environment access, per-thread exception access, Java object type checks, Hadoop `Configuration#set`, and enum instance fetch.

## Important APIs, Control Flow, and State
`MethType` distinguishes static from instance method calls. `invokeMethod` takes a cached class enum and varargs matching the JNI signature; `findClassAndInvokeMethod` resolves a class name first and is documented mainly for bootstrap/tests. `getJNIEnv` creates or retrieves per-thread JNI state and may create the process JVM. `getLastTLSExceptionRootCause`, `getLastTLSExceptionStackTrace`, and `setTLSExceptionStrings` expose `ThreadLocalState` fields owned by the TLS layer.

## Dependencies and Integration Points
It includes `jclasses.h`, `<jni.h>`, stdio, stdlib, stdarg, and errno. The platform path separator macros are shared by classpath expansion in the implementation. Public libhdfs error APIs indirectly depend on the TLS exception functions.

## Risks and Test Signals
Because varargs are unchecked, mismatched signatures can crash or corrupt JNI calls. Returned C strings from `newCStr` are malloc-owned, Java local refs must be deleted by callers, and last-exception pointers are valid only until the next relevant call on the same thread. Tests should validate ownership, static/instance validation, null handling, and thread isolation.
