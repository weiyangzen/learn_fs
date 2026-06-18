# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/doc/Doxyfile.in

## Purpose
This is the Doxygen template used by the libhdfs++ CMake `doc` target to generate API documentation.

## Important APIs, Control Flow, and State
It sets UTF-8 encoding, project name `libhdfspp`, output directory `doc`, two-space tab size, markdown support, and STL support. Its `INPUT` begins with `@PROJECT_SOURCE_DIR@/doc/mainpage.dox` and is configured by CMake into the build directory with variable substitution.

## Dependencies and Integration Points
`libhdfspp/CMakeLists.txt` calls `configure_file` and adds a `doc` custom target only when Doxygen is found. The template depends on source-tree documentation and headers being accessible at generation time.

## Risks and Test Signals
Documentation generation can silently omit APIs if `INPUT` paths drift from installed headers or source layout. Tests should configure with Doxygen present, run the `doc` target, and check that public headers such as `hdfspp.h`, `status.h`, and `hdfs_ext.h` appear in generated output.
