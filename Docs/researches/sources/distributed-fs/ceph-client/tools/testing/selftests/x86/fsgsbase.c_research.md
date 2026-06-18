# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/fsgsbase.c

## Purpose

`fsgsbase.c` is a 64-bit stress/regression test for GS base and selector semantics across `arch_prctl`, direct FSGSBASE instructions, context switches, futex-coordinated threads, LDT/GDT selector loads, and ptrace reads/writes.

## Important APIs, Types, and Functions

The test uses `ARCH_SET_GS`, `ARCH_GET_GS`, `modify_ldt`, 32-bit `set_thread_area` via `int $0x80`, futex syscalls, pthreads, ptrace `PTRACE_PEEKUSER`/`PTRACE_POKEUSER`, and signal-based base discovery. Important functions include `sigsegv()`, `sigill()`, `rdgsbase()`, `rdfsbase()`, `wrgsbase()`, `read_base()`, `check_gs_value()`, `mov_0_gs()`, `load_gs()`, `test_wrbase()`, `threadproc()`, `set_gs_and_switch_to()`, `test_unexpected_base()`, `test_ptrace_write_gs_read_base()`, and `test_ptrace_write_gsbase()`.

## Control Flow

The test first prepares shared scratch memory, runs ptrace GS/GSBASE read behavior before LDT setup, probes whether FSGSBASE instructions are enabled by catching SIGILL, and installs a SIGSEGV handler for base discovery. It verifies several `ARCH_SET_GS` values, behavior after loading selector zero, and optional scheduling. It pins to CPU 0, starts a helper thread, and runs combinations of local GS base, forced selector, and remote helper-thread GS base to verify context-switch preservation. It checks a remote unexpected-base scenario, optionally tests `wrgsbase()` preservation across switches, stops the helper thread, and finally tests ptrace writing GSBASE while preserving selector state.

## State and Persistence Behavior

State includes GS selector/base, LDT/GDT entries, futex variables, helper thread state, shared scratch mapping, ptrace child state, and CPU affinity. It is all process-local except temporary descriptor table entries owned by the process.

## Dependencies and Integration Points

It requires x86_64, signal handling, pthread/futex support, `modify_ldt` or `set_thread_area`, ptrace, and optional FSGSBASE CPU/kernel enablement. It integrates with kernel context-switch and ptrace register save/restore paths.

## Risks and Edge Cases

The test intentionally loads unusual selectors and bases, including `0xffffffffffffffff`, and relies on signal faults to infer bases. It pins to CPU 0 and assumes affinity succeeds. Behavior differs between older/newer kernels and AMD behavior around null selectors; the test accounts for some historical differences but can still expose platform-specific behavior.

## Test Signals

Pass signals are matching `ARCH_GET_GS` and fault-inferred bases, preserved GS selector/base across helper-thread scheduling, zero GSBASE after unexpected remote manipulation, successful `wrgsbase()` preservation when enabled, and expected ptrace selector/base behavior.
