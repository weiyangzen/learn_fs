# sources/compression/zstd/.github/workflows/dev-short-tests.yml

Purpose: broad but faster pull-request workflow covering build variants, packaging systems, Windows/MSYS/Cygwin, external compressors, architecture emulation, size budgets, and compiler feature switches.

Important behavior: jobs validate linux-kernel import/test, benchmarking, 32-bit check, C89/C++/GNU90/C99 compatibility, dynamic library linkage, GCC 7/8 builds, MinGW cross compile, ARM build, shellcheck, zlib wrapper with Valgrind, LZ4/threadpool/library build scripts, AVX2 and 32-bit builds, external compressor matrices, implicit fallthrough warnings, Meson Linux/Windows/MinGW, Visual Studio matrices, lib size thresholds, minified decompressor macros, dynamic BMI2 modes, all program variants, QEMU consistency across many architectures, MSYS2 MinGW short tests, Visual Studio runtime tests, Cygwin tests, pkg-config install/use, version compatibility, PGO, musl, Intel CET/SDE, and Intel oneAPI `icx`.

State, dependencies, and integration: it touches nearly every build system and many package managers. It integrates top-level make, lib/program/test targets, Meson, CMake indirectly, Visual Studio solutions, kernel contrib, wrappers, and examples.

Risks and test signals: breadth creates external-service/package flake risk, but failures are high-signal because this workflow encodes zstd's portability contract across compilers, OS layers, optional libraries, and CPU features.
