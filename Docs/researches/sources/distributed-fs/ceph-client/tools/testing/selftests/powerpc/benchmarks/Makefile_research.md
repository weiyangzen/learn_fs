# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/Makefile

## Purpose
Builds PowerPC microbenchmark binaries for syscall, context-switch, fork, futex, mmap, and time-call costs.

## Important APIs, Types, and Functions
Defines `TEST_GEN_PROGS := gettimeofday context_switch fork mmap_bench futex_bench null_syscall`, `TEST_GEN_FILES := exec_target`, includes kselftest lib.mk and flags.mk, and applies pthread/no-pie/nostdlib/linker options where needed.

## Control Flow
Compilation is delegated to lib.mk; `exec_target` is a support binary for fork+exec workloads, while benchmark programs are executable selftest artifacts.

## State and Persistence
Build output state is under `$(OUTPUT)`; no runtime state here.

## Dependencies and Integration Points
Integrates benchmarks with the PowerPC selftest target while preserving special compile flags such as `-nostdlib` for `exec_target` and `-pthread` for threaded benchmarks.

## Risks and Test Signals
Risks are toolchain flag support and forgetting support-file generation. Test signal is successful build and runnable benchmark binaries.
