# sources/compression/zlib/.github/workflows/configure.yml

Purpose: CI workflow for the traditional `./configure` and `Makefile.in` build path, including native, out-of-source, and cross-compiled targets.

Important jobs/settings: matrix covers Ubuntu GCC, out-of-source build, ARM soft/hard float, AArch64, PowerPC, PowerPC64, PowerPC64LE, s390x, and macOS GCC/Clang. Cross jobs set `CHOST`, cross `CC`, optional static flags, and `QEMU_RUN`.

Control flow: installs cross toolchains/QEMU as needed, creates the build directory, invokes `${src-dir}/configure --warn`, runs `make -j2`, then `make test` with optional QEMU wrappers. Uploads `configure.log` on failure.

State and persistence: writes configure/build outputs either in the checkout or `../build`. Artifact retention keeps configure diagnostics for failed jobs.

Dependencies and integration: depends on GNU make, shell configure script, cross compilers, QEMU user emulation, and zlib's `QEMU_RUN` Makefile variable.

Risks: static cross-builds depend on correct libc cross packages and QEMU paths. `chost` for PPC64 is set to `powerpc-linux-gnu` in the matrix while the compiler is `powerpc64-linux-gnu-gcc`, which deserves scrutiny if cross-prefix tools are used.

Test signals: validates the non-CMake path, large platform spread, out-of-source operation, and runtime examples under emulation.
