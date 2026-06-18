# sources/compression/xz/.github/workflows/msvc.yml

## Purpose
This workflow validates CMake builds with Microsoft Visual C++ and ClangCL on Windows. It covers Win32 and x64 Debug/Release configurations.

## Important Control Flow
The `MSVC` job checks out the repo, configures a Win32 build, builds/tests Debug and Release with `ctest`, repeats for x64, then configures `-T ClangCL -A x64` and tests Debug/Release. All builds use CMake's multi-config generator semantics.

## State, Dependencies, and Integration
Build directories are `build-msvc-win32`, `build-msvc-x64`, and `build-clangcl-x64`. Dependencies are Windows GitHub runners, Visual Studio CMake generators, CTest, and the top-level `CMakeLists.txt`.

## Risks and Test Signals
This is the main native Windows/MSVC signal for resource files, DLL/import library naming, manifests, and compiler compatibility. It does not exercise autotools or MSYS2 shell behavior; those are handled by the MSYS2 workflow.
