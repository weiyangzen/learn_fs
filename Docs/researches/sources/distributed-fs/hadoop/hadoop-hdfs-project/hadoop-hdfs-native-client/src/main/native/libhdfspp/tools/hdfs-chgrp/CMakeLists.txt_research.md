<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chgrp/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chgrp/CMakeLists.txt

## Purpose
Builds the `hdfs-chgrp` libhdfs++ command-line tool library and executable.

## Important APIs, Types, And Functions
CMake declarations: `add_library(hdfs_chgrp_lib STATIC $<TARGET_OBJECTS:hdfs_tool_obj> $<TARGET_OBJECTS:hdfs_ownership_obj> hdfs-chgrp.cc)`, `target_include_directories(hdfs_chgrp_lib PRIVATE ../../tools hdfs-chgrp ${Boost_INCLUDE_DIRS})`, `target_link_libraries(hdfs_chgrp_lib PRIVATE Boost::boost Boost::program_options tools_common hdfspp_static)`, `add_executable(hdfs_chgrp main.cc)`, `target_include_directories(hdfs_chgrp PRIVATE ../../tools)`, `target_link_libraries(hdfs_chgrp PRIVATE hdfs_chgrp_lib)`, `install(TARGETS hdfs_chgrp RUNTIME DESTINATION bin)`.

## Control Flow
CMake creates a static tool-specific library from the shared `hdfs_tool_obj` object and the command implementation source, wires include directories and dependencies, then builds and installs the executable from `main.cc`.

## State And Persistence
No runtime state. Build artifacts are the static library and installed executable.

## Dependencies And Integration Points
Depends on Boost program_options, `tools_common`, `hdfspp_static`, and shared command base object code. The top-level tools CMake file adds this directory.

## Risks
Target naming follows Hadoop's historical camel-case executable names for some commands; renames can break tests and install scripts. Missing include paths or link dependencies surface at build time.

## Test Signals
Successful CMake generation, compilation, and install target creation validate this build glue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chgrp/CMakeLists.txt -->
