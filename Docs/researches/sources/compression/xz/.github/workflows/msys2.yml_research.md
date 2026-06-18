# sources/compression/xz/.github/workflows/msys2.yml

## Purpose
This workflow validates XZ under MSYS2 environments, covering both CMake and autotools builds across mingw32, ucrt64, clang64, msys, and clangarm64.

## Important Control Flow
The matrix chooses runner and MSYS2 system. Setup differs for `msys` versus mingw-like systems, then Git is configured to avoid CRLF conversion. The workflow runs CMake full shared, CMake small static on `windows-latest`, `autogen.sh --no-po4a`, autotools full shared, and autotools small static on `windows-latest`. On failure it uploads CTest and autotools logs.

## State, Dependencies, and Integration
State is in build directories `b-cmake-*` and `b-autotools-*`. Dependencies include `msys2/setup-msys2`, pacboy packages, Ninja, CMake, autotools, gettext, and a shell default of `msys2 {0}`. It exercises Windows/POSIX compatibility paths in both build systems.

## Risks and Test Signals
This workflow is high-value for path, symlink, CRLF, MinGW, UCRT, clang, and ARM64 Windows coverage. Risks include action version drift, package changes, and differences between MSYS and native Windows behavior.
