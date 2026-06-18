# sources/compression/zlib/.github/workflows/msys-cygwin.yml

Purpose: Windows CI for MSYS2 and Cygwin environments using CMake.

Important jobs/settings: `MSys` matrix covers `mingw32`, `mingw64`, `ucrt64`, `clang64`, and `clangarm64` with `clangarm64` on Windows ARM. `cygwin` uses the Cygwin install action with CMake, GCC, and Ninja packages.

Control flow: MSYS2 jobs configure with Unix Makefiles, selecting `CC=clang` for clang64, then build and run CTest. Cygwin configures from the checkout path using Ninja, builds with `-j1`, and runs CTest.

State and persistence: build directories under the CI workspace; no repository modifications.

Dependencies and integration: uses `msys2/setup-msys2@v2`, `cygwin/cygwin-install-action@master`, CMake, make/Ninja, pacboy toolchains, and minizip options.

Risks: Cygwin action is pinned to `master`; fixed checkout path `/cygdrive/d/a/zlib/zlib` assumes GitHub workspace layout. `MINIZIP_ENABLE_BZIP2` is disabled for Cygwin, reducing coverage there.

Test signals: validates Unix-like Windows toolchains, DLL lookup behavior, minizip builds, and CTest execution under MSYS/Cygwin shells.
