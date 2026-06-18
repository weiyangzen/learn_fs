# sources/distributed-fs/lizardfs/cmake/mingw32-toolchain.cmake

## Purpose
This CMake toolchain file configures 32-bit MinGW cross-compilation for Windows.

## Important APIs, Types, and Functions
It sets `CMAKE_SYSTEM_NAME` to `Windows`, `CMAKE_SYSTEM_VERSION` to `8`, C, C++, and resource compilers to `i686-w64-mingw32-*`, and root paths to `/usr/i686-w64-mingw32/` and `/usr/local/i686-w64-mingw32/`.

## Control Flow and State
The file is consumed by CMake before project configuration. It directs find behavior: programs are searched on the host, while libraries and includes are searched only in the target root. It clears shared-library link flags for C and C++.

## Dependencies and Integration Points
It is used with `cmake -DCMAKE_TOOLCHAIN_FILE=cmake/mingw32-toolchain.cmake ...`. Top-level MinGW checks then add Windows definitions and skip non-MinGW subsystems.

## Risks and Edge Cases
Compiler names and root paths are distro-specific. Clearing shared-library link flags may be required for this project but can surprise future shared targets. The system version is fixed at Windows 8.

## Test Signals
Successful CMake configure with this toolchain and compilation of MinGW-supported targets are the signals. Missing cross compiler fails early.
