<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/optional_wrapper.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/optional_wrapper.h

## Purpose
Wraps the third-party `optional.hpp` compatibility header and suppresses selected Clang diagnostics around it.

## Important APIs, Types, And Functions
The file conditionally pushes Clang diagnostics, defines `TR2_OPTIONAL_DISABLE_EMULATION_OF_TYPE_TRAITS` for older Clang handling, includes `<optional.hpp>`, then restores diagnostics.

## Control Flow
There is no runtime flow; it is a compile-time compatibility shim.

## State And Persistence
No state exists.

## Dependencies And Integration Points
Included by common headers that use `std::experimental::optional`, including configuration, auth, and event code.

## Risks
The wrapper assumes the project-provided `optional.hpp` is on the include path. Compiler-specific warning suppression may become stale as toolchains change.

## Test Signals
Build matrix coverage across Clang and GCC, especially older Clang versions, is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/optional_wrapper.h -->
