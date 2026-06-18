# sources/compression/zstd/.github/workflows/windows-artifacts.yml

Purpose: build and publish Windows binary artifact packages for x86_64, i686, and ARM64.

Important behavior: runs on selected branches and published releases. The matrix uses MSYS2 for mingw64/mingw32 and CMake/Visual Studio on `windows-11-arm` for ARM64. MSYS2 jobs build static zlib and LZ4 dependencies, then build zstd programs with static linking and external library support. ARM64 configures `build/cmake` for Visual Studio 2022 ARM64 with programs/shared/static enabled. All variants run `lib/dll/example/build_package.bat`, rename `bin` to `zstd-${ref}-${ziparch}`, upload an inspection artifact, package a zip, and upload it to a GitHub release on release events.

State, dependencies, and integration: state includes cloned zlib/lz4 repos, MSYS2 packages, CMake build dirs, generated bin directories, artifacts, and release assets.

Risks and test signals: branch/ref names flow into artifact names. Static dependency versions are pinned by tags. The workflow tests packaging scripts and release upload path, but not full CLI runtime behavior beyond successful package build.
