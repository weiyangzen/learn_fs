# sources/distributed-fs/lizardfs/cmake/EnvTests.cmake

## Purpose
This module runs the build's portability and environment probes, replacing older autotools checks and generating variables used by `config.h.in`.

## Important APIs, Types, and Functions
It includes CMake check modules plus local helpers, defines the header list, handles FreeBSD include paths, calls `check_includes`, detects endianness, checks integer and system type sizes, probes struct members, required functions, optional functions, `clock_gettime`, mmap-related functions, C++ standard-library features, compiler flags, CPU dispatch support, Apple poll/select conversion, fallocate punch-hole constants, and `std::future`.

## Control Flow and State
The module runs during CMake configure before `config.h` generation. Required functions include POSIX and C library calls; non-MinGW builds add `getpass`, `poll`, and `realpath`. It temporarily changes `CMAKE_REQUIRED_INCLUDES` and `CMAKE_REQUIRED_FLAGS` for scoped probes, then unsets them.

## Dependencies and Integration Points
It depends on helper modules `CheckCXXExpression`, `CheckFunctions`, `CheckIncludes`, `CheckMembers`, and `SharedLibraries`. Its output variables map directly to `#cmakedefine` entries in `config.h.in`, influencing conditional compilation across LizardFS.

## Risks and Edge Cases
Probe order matters: some checks depend on include paths or compiler flags. The Judy bug/runtime check can be expensive when Judy is found. `sys/rusage.h` may not exist on all platforms but is included in the header list. Required function policy may need adjustment for newer or less POSIX-like platforms.

## Test Signals
Configure messages and generated macros are the signal. Required function misses produce errors; optional misses produce disabled feature macros. Build success across Linux, FreeBSD, macOS, SunOS, and MinGW validates this layer.
