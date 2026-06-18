# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/CMakeLists.txt

## Purpose
This CMake file is the examples entry point for libhdfs++, grouping C and C++ example programs.

## Important APIs, Control Flow, and State
It simply calls `add_subdirectory(c)` and `add_subdirectory(cc)`. There is no runtime state; it controls build inclusion when examples are enabled by the top-level CMake file.

## Dependencies and Integration Points
The parent build adds this directory only when `HDFSPP_LIBRARY_ONLY` is not set. Child directories define actual example executables linked against `hdfspp_static`, `tools_common`, x-platform helpers, and uriparser where needed.

## Risks and Test Signals
The file is straightforward, but missing child directories or disabled targets can break example coverage. Tests should configure a full build and verify both C and C++ example targets are generated.
