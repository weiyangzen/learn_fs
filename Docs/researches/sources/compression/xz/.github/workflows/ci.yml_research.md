# sources/compression/xz/.github/workflows/ci.yml

## Purpose
This GitHub Actions workflow is the primary POSIX CI matrix for XZ Utils. It runs autotools and CMake builds on Ubuntu x86_64, Ubuntu ARM, and macOS, covering full builds and many feature-disabled configurations.

## Important Control Flow
The `POSIX` job installs dependencies conditionally for OS and build system, then repeatedly calls `./build-aux/ci_build.bash` for build and test phases. Special lanes cover 32-bit GCC, sanitizers, Valgrind, musl, full features, no encoders, no decoders, no threads, no BCJ, no Delta, reduced check algorithms, and small mode. Failed runs upload `build-aux/artifacts`.

## State, Dependencies, and Integration
The workflow depends on GitHub-hosted runners, package managers, autotools/CMake, gettext/po4a/doxygen, musl tools, Valgrind, and the shared `ci_build.bash` contract. Build state is placed outside the source tree in `../xz_build` by the wrapper.

## Risks and Test Signals
This workflow is the broadest automated signal for build-option compatibility. Risk areas include runner package drift, timeouts, and feature-matrix gaps on non-POSIX systems handled by separate workflows. Artifact upload on failure preserves test logs for diagnosis.
