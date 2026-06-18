# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/crosstests.conf

Purpose: example `ktest.pl` configuration for cross-compiling many architectures with downloaded kernel.org crosstool toolchains.

Important APIs, types, and functions: defines ktest variables/options such as `THIS_DIR`, `BUILD_DIR`, `OUTPUT_DIR`, `BUILD_OPTIONS`, `DIE_ON_FAILURE`, `LOG_FILE`, `CLEAR_LOG`, `DO_FAILED`, `DO_DEFAULT`, `RUN`, `GCC_VER`, `MAKE_CMD`, `TEST_TYPE`, `BUILD_TYPE`, `TEST_NAME`, `CROSS`, and `ARCH`. It contains many `TEST_START IF ...` sections for alpha, arm, ia64, m68k, mips, parisc, powerpc, s390, sh, sparc, xtensa, UML, i386, x86_64, and a bisect example.

Control flow: ktest parses the file, expands variables, and creates build-only tests. Default tests run when `${DO_DEFAULT}` is true; known-failing tests are gated by `${DO_FAILED}` unless explicitly selected by `${RUN}`. Each section sets `CROSS` and `ARCH`, and the common `MAKE_CMD` uses the selected toolchain path. The final `DEFAULTS` block supplies required but unused boot/install/power options so ktest accepts build-only tests.

State and persistence: ktest writes builds under `OUTPUT_DIR`, logs to `cross.log`, and optionally stores failures if configured. The config itself is read-only input.

Dependencies and integration points: assumes a Linux source tree at `BUILD_DIR`, crosstools installed under `/usr/local/gcc-<ver>-nolibc/<cross>/bin`, and ktest option semantics. The bisect section integrates with ktest's bisect mode.

Risks: the documented toolchain versions are old and paths are environment-specific. `DO_DEFAULT=1` runs many builds by default, which can be expensive. Some architectures are marked failed and may need updating. Comments note that option assignment form matters for ktest persistence.

Test signals: ktest should generate build tests named by architecture and cross compiler, run `make ARCH=...` with the right `CROSS_COMPILE`, and produce a cross.log summarizing build results.
