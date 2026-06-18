# sources/distributed-fs/lizardfs/cmake/mingw32-w64-toolchain.cmake

## Purpose
This CMake toolchain file configures 64-bit MinGW-w64 cross-compilation for Windows.

## Important APIs, Types, and Functions
It sets `CMAKE_SYSTEM_NAME` to `Windows`, `CMAKE_SYSTEM_VERSION` to `8`, C, C++, and resource compilers to `x86_64-w64-mingw32-*`, and root paths to `/usr/x86_64-w64-mingw32/` and `/usr/local/x86_64-w64-mingw32/`.

## Control Flow and State
The file directs CMake discovery so build tools come from the host while libraries and includes come from target roots. Shared-library link flags for C and C++ are cleared.

## Dependencies and Integration Points
It is selected via `CMAKE_TOOLCHAIN_FILE` and interacts with top-level MinGW conditionals that alter compiler flags, definitions, and enabled subdirectories.

## Risks and Edge Cases
Hard-coded toolchain names and sysroots may not match all distributions. Like the 32-bit file, it fixes the target Windows version and clears shared-link flags globally.

## Test Signals
Configure and build success with an installed `x86_64-w64-mingw32` toolchain are the main signals.
