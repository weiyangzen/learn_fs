# sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/unistd.h

## Purpose
Defines the generic Linux syscall-number table and macro expansion hooks used by architectures that follow the generic syscall ABI layout.

## Important APIs, Types, and Functions
Includes `<asm/bitsperlong.h>`. Defines `__SYSCALL` default hook, selection helpers `__SC_3264`, `__SC_COMP`, and `__SC_COMP_3264`, hundreds of `__NR_*` syscall numbers from `io_setup` through `rseq_slice_yield`, `__NR_arch_specific_syscall`, `__NR_syscalls 472`, and 32/64-bit alias mappings such as `__NR_fcntl` versus `__NR_fcntl64`.

## Control Flow, State, and Persistence
This header has no executable runtime flow, but its preprocessor control flow is central: `__BITS_PER_LONG`, `__SYSCALL_COMPAT`, `__ARCH_WANT_*`, and `__ARCH_NOMMU` select time32/time64, compat, legacy, MMU-only, and architecture-reserved syscall entries.

## Dependencies and Integration
Depends on arch word-size definitions and on includers optionally redefining `__SYSCALL` to generate tables. It integrates with libc syscall numbers, seccomp/BPF tooling, syscall tracers, audit/perf decoders, and kernel syscall table generation.

## Risks and Test Signals
Risks are severe ABI breakage if numbers or aliases change, stale `__NR_syscalls`, incorrect time64 exposure on 32-bit ABIs, and accidental use of generic numbers on an architecture with overrides. Test signals include generated table diffs against kernel headers, seccomp compile tests, syscall smoke tests for selected numbers, and preprocessing under 32-bit, 64-bit, compat, and NOMMU configurations.
