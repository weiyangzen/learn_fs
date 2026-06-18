# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/pom.xml

## Purpose
Maven module descriptor for the HDFS native client jar and native build/test profiles.

## Important APIs, Types, And Functions
Declares module metadata, properties such as `require.fuse`, `require.libwebhdfs`, `native_ctest_args`, dependencies on HDFS client/common/test jars and JUnit, RAT exclusions for native trees, and profiles `native-win`, `native`, and `native-clang`.

## Control Flow
Default build produces a jar. Native profiles drive CMake compilation and CTest execution through Hadoop Maven plugin or antrun. Windows uses `cmake` plus `msbuild`; Unix and clang profiles call `cmake-compile`, then run `ctest --output-on-failure` with classpath and native library path environment variables.

## State, Persistence, And Dependencies
Generated native outputs live under Maven target directories, with distribution copies under `target/bin` on Windows and `target/native/target/usr/local/lib` on non-Windows. Tests depend on correct `CLASSPATH`, `LD_LIBRARY_PATH`/`DYLD_LIBRARY_PATH`, `HADOOP_HOME` on Windows, and optional OpenSSL/FUSE/libwebhdfs requirements.

## Integration Points
Bridges Maven lifecycle to `src/CMakeLists.txt`, native libhdfs, libhdfs++/libwebhdfs, FUSE, native tests, and Hadoop common native libraries.

## Risks
Profile behavior is platform-sensitive. Optional native components can be skipped unless their `require.*` properties are true, which can hide missing dependencies. Environment variables are central to JNI loading; incorrect library paths cause native tests to fail before assertions.

## Test Signals
Signals include successful `cmake-compile`, `msbuild` on Windows, `ctest` native test pass, and failures when required OpenSSL/FUSE/libwebhdfs components are absent.
