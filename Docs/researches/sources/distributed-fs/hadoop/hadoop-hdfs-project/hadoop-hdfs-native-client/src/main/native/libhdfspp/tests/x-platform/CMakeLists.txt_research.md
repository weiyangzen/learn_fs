<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/CMakeLists.txt

## Purpose
Defines libhdfs++ x-platform unit-test targets for path utilities, syscall wrappers, `ssize_t` compatibility, and directory iteration including the C API wrapper.

## Important APIs, Types, And Functions
CMake declarations: `add_executable(x_platform_utils_test $<TARGET_OBJECTS:x_platform_obj> utils_common_test.cc utils_test_main.cc utils_win_test.cc)`, `add_executable(x_platform_syscall_test $<TARGET_OBJECTS:x_platform_obj> syscall_common_test.cc utils_test_main.cc syscall_win_test.cc)`, `add_executable(x_platform_utils_test $<TARGET_OBJECTS:x_platform_obj> utils_common_test.cc utils_test_main.cc utils_nix_test.cc)`, `add_executable(x_platform_syscall_test $<TARGET_OBJECTS:x_platform_obj> syscall_common_test.cc utils_test_main.cc syscall_nix_test.cc)`, `target_include_directories(x_platform_utils_test PRIVATE ${LIBHDFSPP_LIB_DIR})`, `target_link_libraries(x_platform_utils_test gmock_main)`, `add_test(x_platform_utils_test x_platform_utils_test)`, `target_include_directories(x_platform_syscall_test PRIVATE ${LIBHDFSPP_LIB_DIR})`, `target_link_libraries(x_platform_syscall_test gmock_main)`, `add_test(x_platform_syscall_test x_platform_syscall_test)`, `add_executable(x_platform_types_test types_test.cc)`, `target_include_directories(x_platform_types_test PRIVATE ${LIBHDFSPP_LIB_DIR})`, `target_link_libraries(x_platform_types_test gtest_main)`, `add_test(x_platform_types_test x_platform_types_test)`, `add_library(x_platform_dirent_test_obj OBJECT $<TARGET_OBJECTS:x_platform_obj> dirent_test.cc)`, `add_executable(x_platform_dirent_test $<TARGET_OBJECTS:x_platform_dirent_test_obj> $<TARGET_OBJECTS:x_platform_obj>)`, `target_include_directories(x_platform_dirent_test PRIVATE ${LIBHDFSPP_LIB_DIR})`, `target_link_libraries(x_platform_dirent_test PRIVATE gtest_main)`, `add_test(x_platform_dirent_test x_platform_dirent_test)`, `add_executable(x_platform_dirent_c_test $<TARGET_OBJECTS:x_platform_dirent_test_obj> $<TARGET_OBJECTS:x_platform_obj> $<TARGET_OBJECTS:x_platform_obj_c_api> c-api/dirent_test.cc)`, `target_compile_definitions(x_platform_dirent_c_test PRIVATE USE_X_PLATFORM_DIRENT)`, `target_include_directories(x_platform_dirent_c_test PRIVATE ${LIBHDFSPP_LIB_DIR} ../)`, `target_link_libraries(x_platform_dirent_c_test PRIVATE gtest_main)`, `add_test(x_platform_dirent_c_test x_platform_dirent_c_test)`.

## Control Flow
CMake selects Windows or non-Windows source files for utils and syscall tests, then registers each executable with `add_test`. Directory iteration tests reuse an object library and build both C++ and C API test executables.

## State And Persistence
No runtime state. Build state consists of test executables and object libraries.

## Dependencies And Integration Points
Depends on `x_platform_obj`, `x_platform_obj_c_api`, gtest/gmock, and `${LIBHDFSPP_LIB_DIR}` includes.

## Risks
Platform branches must remain symmetric as x-platform APIs evolve. Reusing object libraries requires compatible compile definitions, especially `USE_X_PLATFORM_DIRENT` for the C API test.

## Test Signals
Successful configure/build plus registered CTest targets `x_platform_utils_test`, `x_platform_syscall_test`, `x_platform_types_test`, `x_platform_dirent_test`, and `x_platform_dirent_c_test`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/CMakeLists.txt -->
