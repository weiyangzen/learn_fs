# sources/compression/zstd/CMakeLists.txt

Purpose: thin top-level CMake wrapper so users can run `cmake -S .` at the repository root while keeping real policy and language configuration under `build/cmake`.

Important behavior: requires CMake 3.10, declares `project(zstd-superbuild LANGUAGES NONE)`, rejects in-source builds by comparing `CMAKE_SOURCE_DIR` and `CMAKE_BINARY_DIR`, and delegates with `add_subdirectory(build/cmake)`.

State, dependencies, and integration: no persistent state beyond generated CMake build files. It integrates with root-level CMake workflows and downstream users who expect the repository root to be configurable, while avoiding language enablement at the wrapper layer.

Risks and test signals: the main risk is divergence between root invocation and direct `build/cmake` invocation. The `cmake-root-basic` workflow explicitly validates this wrapper, and spaces-in-path CMake tests provide additional coverage.
