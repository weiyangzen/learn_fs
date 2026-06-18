# sources/distributed-fs/lizardfs/cmake/FindJudy.cmake

## Purpose
This find module locates Judy headers and library and performs a runtime check for a Judy1 behavior issue.

## Important APIs, Types, and Functions
It sets `JUDY_INCLUDE_DIR`, `JUDY_LIBRARY`, `JUDY_FOUND`, and `JUDY_HAVE_WORKING_JUDY1`. The runtime check compiles and runs a C program that repeatedly calls `Judy1Set` for many indexes and fails on `JERR` or false insertion.

## Control Flow and State
After finding the path/library, it sets `CMAKE_REQUIRED_INCLUDES` and `CMAKE_REQUIRED_LIBRARIES`, runs `check_c_source_runs`, unsets those variables, and delegates final package handling to `find_package_handle_standard_args`.

## Dependencies and Integration Points
`Libraries.cmake` calls `find_package(Judy)` and maps success to `LIZARDFS_HAVE_JUDY` and `LIZARDFS_HAVE_WORKING_JUDY1`, which are emitted by `config.h.in`.

## Risks and Edge Cases
The runtime test loops up to 50 million iterations, which can slow configuration or be impossible under cross-compilation. Runtime checks also fail when compiled binaries cannot execute on the configure host.

## Test Signals
Configure-time Judy discovery and the working-Judy macro are the signals. Source code using Judy should be guarded by these macros.
