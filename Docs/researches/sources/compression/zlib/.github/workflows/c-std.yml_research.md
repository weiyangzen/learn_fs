# sources/compression/zlib/.github/workflows/c-std.yml

Purpose: GitHub Actions workflow that compiles zlib across many C language standards, compilers, architectures, operating systems, and build systems with warnings treated as errors.

Important jobs: `main` covers GCC/Clang on Linux, macOS, Windows, and Windows ARM64 across configure and CMake builders and C89 through C2x/GNU2x modes. `msvc` covers MSVC CMake builds with default, C11, C17, and latest modes across supported Windows architectures.

Control flow: matrix exclusions remove unsupported combinations such as configure on Windows, 32-bit macOS, 32-bit Windows GCC, and GCC on Windows ARM64. Configure jobs run `./configure`, `make`, and `make test`; CMake jobs configure, build, and run CTest. MSVC builds both a no-test build and a build with tests/minizip.

State and persistence: CI-only build directories and installed packages; no repository state is changed. Linux 32-bit jobs install multilib packages, Windows jobs install Ninja.

Dependencies and integration: uses `actions/checkout@v6`, system compilers, Chocolatey, CMake, CTest, make, and zlib options such as `ZLIB_BUILD_TESTING` and `ZLIB_BUILD_MINIZIP`.

Risks: the matrix is large and costly. Older C modes require `-DZLIB_INSECURE` to compile code paths that use legacy prototypes. `ctest ./build` is unusual but intended to run tests for the build tree.

Test signals: strong standards-compatibility signal because `-Werror -Wall -Wextra` is applied broadly; CTest and `make test` verify runtime examples where enabled.
