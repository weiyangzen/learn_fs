# sources/compression/xz/cmake/tuklib_large_file_support.cmake

## Purpose
This module adds large-file support for platforms where `off_t` is smaller than 64 bits by default but becomes 64-bit with `_FILE_OFFSET_BITS=64`.

## Important Control Flow
`tuklib_large_file_support(TARGET_OR_ALL)` returns immediately for MSVC. It compiles a probe requiring `sizeof(off_t) >= 8`; if that fails, it repeats with `-D_FILE_OFFSET_BITS=64`. When the second probe succeeds, it exposes the `LARGE_FILE_SUPPORT` option defaulting ON and adds `_FILE_OFFSET_BITS=64` when enabled.

## State, Dependencies, and Integration
It uses `CheckCSourceCompiles`, `CMakePushCheckState`, and `tuklib_common.cmake`. It is called globally near the start of `CMakeLists.txt` so all targets and later checks see consistent file-offset behavior.

## Risks and Test Signals
Incorrect detection could break files larger than 2 GiB, especially on 32-bit platforms and MinGW-w64. CI lanes for 32-bit and large-file tests in related suites provide indirect coverage.
