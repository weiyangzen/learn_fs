# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/HadoopJNI.cmake

Purpose: Shared JNI discovery module for Hadoop native components, ensuring the CMake build uses a JVM matching Maven-provided architecture.

Important APIs and control flow: the file first validates `JVM_ARCH_DATA_MODEL` is defined and either 32 or 64. On Linux, it derives `_java_home` from `JAVA_HOME`, maps `CMAKE_SYSTEM_PROCESSOR` to Java library architecture directories (`i386`, `amd64`, `arm`, `ppc64le`/`ppc64`, or processor name), searches only under `JAVA_HOME` for `jni.h`, `jni_md.h` or IBM `jniport.h`, and `jvm`/`JavaVM`. It sets `JNI_INCLUDE_DIRS` and `JNI_LIBRARIES`, emits diagnostic messages, fails if any component is missing, then still invokes `find_package(JNI REQUIRED)`. Non-Linux uses standard `find_package(Java REQUIRED)`, `include(UseJava)`, and `find_package(JNI REQUIRED)`.

State and dependencies: state is CMake variables for Java include paths, JVM library, JNI include/library variables, and temporary `_java_home`/`_java_libarch`. It depends on `JAVA_HOME`, Maven-provided `JVM_ARCH_DATA_MODEL`, CMake `FindJNI`, and Java/JNI installation layout.

Integration points: included by native targets requiring JNI headers or JVM libraries. It cooperates with `HadoopCommon.cmake`, which may alter `CMAKE_SYSTEM_PROCESSOR` for 32-bit builds before JNI discovery.

Risks and test signals: Linux discovery intentionally ignores system paths, so an unset or wrong `JAVA_HOME` is fatal even if system JNI exists. Mixed JDK layouts across Java 8 and later are handled by broad path globs, but unusual vendors can still fail. Diagnostic messages are useful build signals.
