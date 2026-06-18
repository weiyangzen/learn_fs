<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/asm_pure_loop/Makefile -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/asm_pure_loop/Makefile

## Purpose

This Makefile builds and installs the `asm_pure_loop` CoreSight workload from raw arm64 assembly.

## Research

It includes `../Makefile.miniconfig`, sets `BIN=asm_pure_loop`, and compiles `asm_pure_loop.S` with `-nostdlib -static` only when `CORESIGHT` is defined and `ARCH=arm64`. `install-tests` creates the perf exec test subdirectory and installs the binary under its own named directory. `clean` removes the binary. State is the built static executable and installed copy. Dependencies are arm64 compiler support, install variables from perf's make system, and CoreSight build configuration. Integration supplies a deterministic no-libc workload for `asm_pure_loop.sh`. Risks are no target produced on non-arm64 builds, static link/toolchain failures, and install path variable quoting complexity. Test signal is existence of an executable binary for the shell wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/asm_pure_loop/Makefile -->
