# sources/compression/zstd/.github/workflows/cmake-tests.yml

Purpose: focused CMake validation across root wrapper configuration, make-wrapper integration, path handling, Windows generators, and macOS ARM64.

Important behavior: common env sets short test timeouts and warning-as-error flags with tests enabled. Jobs cover `cmake -S .` root build, `make cmakebuild`, source paths containing spaces on Linux/Windows/macOS, Visual Studio 2022 x64/Win32/ARM64, MinGW, Clang-CL, Clang-CL AVX2, a no-`ZSTD_BUILD_TESTS` regression case, and Apple Silicon build/test. Windows jobs configure from `build/cmake`, build Debug, and run `ctest`; macOS builds Release and runs `ctest`.

State, dependencies, and integration: build directories and installed artifacts are ephemeral. It integrates the root `CMakeLists.txt` shim, `build/cmake` project, CTest labels, MSBuild setup, NMake/MinGW generators, and platform runners.

Risks and test signals: runner image changes and Windows ARM availability can affect stability. The spaces-in-path job is a useful packaging robustness check. Test coverage emphasizes CMake behavior rather than the full make/sanitizer matrix.
