# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/CMakeLists.txt

## Purpose
This is the main CMake build definition for libhdfs++. It configures dependencies, feature checks, optional docs/tests/examples/tools, Hadoop-tree import copying, object-library aggregation, static/shared library targets, and install layout.

## Important APIs, Control Flow, and State
The build requires CMake 3.5, C++17, Boost date_time 1.86, OpenSSL, Protobuf, absl, utf8_range, and threads. It fetches GoogleTest, validates `thread_local`, probes protobuf compiler/library compatibility, and configures valgrind if requested. SASL selection prefers Cyrus, falls back to GSASL, or fails unless `NO_SASL` is set. It defines Asio standalone flags, compiler flags, optional Doxygen target, and a `copy_on_demand` function for importing HDFS/common headers and protos when `HADOOP_BUILD` is true. It adds subdirectories, aggregates object targets into `hdfspp_static` and optionally `hdfspp`, installs headers/libraries, and defines `InstallToBuildDirectory`.

## Dependencies and Integration Points
It integrates Hadoop's `hadoop_add_dual_library` path when building inside Hadoop, otherwise creates standard CMake libraries. It wires third-party `uriparser2`, lib submodules, C bindings, examples, tests, and tools.

## Risks and Test Signals
Build risk is high around dependency versions, absl target names, SASL provider choice, fetched googletest network availability, MSVC shared builds, and imported Hadoop proto/header paths. Tests should run configure/build with `HADOOP_BUILD`, standalone, `HDFSPP_LIBRARY_ONLY`, `NO_SASL`, Cyrus, GSASL, shared/static, Unix, Apple, and MSVC variants.
