<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/CMakeLists.txt

## Purpose
Defines the `common_obj` object library and the concrete `common` library for the native libhdfspp common layer. It centralizes utility, configuration, status, logging, retry, auth, formatting, and lock sources used by filesystem, RPC, reader, and binding modules.

## Important APIs, Types, And Functions
The build file conditionally links `dl` through `LIB_DL`, includes Boost and public include directories, and composes `common_obj` from `status.cc`, `sasl_digest_md5.cc`, `ioservice_impl.cc`, `options.cc`, `configuration*.cc`, `hdfs_configuration.cc`, `uri.cc`, `util.cc`, `retry_policy.cc`, `cancel_tracker.cc`, `logging.cc`, `libhdfs_events_impl.cc`, `auth_info.cc`, `namenode_info.cc`, `statinfo.cc`, `fsinfo.cc`, `content_summary.cc`, `locks.cc`, and `config_parser.cc`. It also folds in `x_platform_obj` and `uriparser2_obj` for the final `common` target.

## Control Flow
CMake first sets `LIB_DL` if dynamic-loader linkage is needed, then builds an object target for reuse and a normal library target for link consumers. Private include paths point at `../../lib`, making internal headers visible to common sources and downstream modules.

## State And Persistence
There is no runtime state. Build state is encoded in target membership and transitive object inclusion.

## Dependencies And Integration Points
This is the build integration point between Boost, x-platform portability code, the URI parser object target, and higher-level native HDFS components. If a new common source is added but omitted here, dependent libraries can compile headers but fail at link time.

## Risks
The object-library composition duplicates `x_platform_obj` in both `common_obj` and `common`, so changes should preserve existing linker expectations. Conditional `dl` linkage is platform-sensitive. Missing include directories or omitted source files can surface as downstream failures far away from this CMake file.

## Test Signals
Signals are clean CMake configuration on platforms with and without `NEED_LINK_DL`, successful native-client library links, and targeted tests that instantiate symbols from every common source file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/CMakeLists.txt -->
