<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/xstate.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/xstate.c

## Purpose

`xstate.c` is a generic userspace x86 extended-state regression suite. For selected xfeatures such as AVX, AVX-512, AMX tile data, and APX, it tests context switching, ptrace injection, and signal-frame exposure of XSAVE state.

## Important APIs, Types, and Functions

Key helpers are `xgetbv()`, `load_rand_xstate()`, `load_init_xstate()`, `copy_xstate()`, `validate_xstate_same()`, and `validate_xregs_same()`. Context switching uses `struct futex_info`, pthreads, mutex handoff, CPU affinity, `test_context_switch()`, and randomized `xrstor/xsave`. Ptrace uses `PTRACE_GETREGSET/SETREGSET` and `NT_X86_XSTATE`. Signal testing uses `validate_sigfpstate()` to inspect the signal frame's `_fpx_sw_bytes` and saved xstate contents. `test_xstate()` orchestrates per-feature execution.

## Control Flow and State

For each supported feature, the code gets CPUID xstate metadata, validates the feature mask, forces context switches among threads with random register contents, forks a ptracee for state injection, and raises a signal after stashing expected state. Global `xstate` identifies the current feature, and per-test buffers hold aligned XSAVE images. State is process-local and randomized to avoid initial-state false positives.

## Dependencies and Integration Points

It depends on CPUID leaf 0xd, XCR0 feature enablement, XSAVE/XRSTOR instructions, pthreads, ptrace xstate regsets, signal frame layout, `helpers.h`, and `xstate.h`. It complements feature-specific selftests like PKRU by focusing on generic kernel save/restore ABI.

## Risks and Test Signals

Risks include lost xstate during context switch, ptrace format mismatch, signal-frame feature-bit errors, dynamic xstate allocation bugs, or unsupported feature mishandling. Passing output reports no incorrect context-switch cases and successful ptrace and signal checks for each tested feature.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/xstate.c -->
