# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-context-force-tm.c

Purpose: stress-tests sigreturn handling when a signal handler forces MSR[TS] in the saved context and induces page faults/segfault recovery.

Important APIs/types/functions: `usr_signal_handler()` allocates and installs a `uc_link`, copies mcontext, sets `MSR_TS_S`, and forks; `seg_signal_handler()` increments `count` and restores `init_context`; `tm_trap_test()` loops through `COUNT_MAX`.

Control flow: each iteration allocates a fresh alternate signal stack, marks it cold with `madvise`, installs handlers, raises SIGUSR1, and either continues or recovers from SIGSEGV through `setcontext()`. The test is designed to reveal kernel crashes, not return semantic failures.

State and persistence behavior: intentionally leaks mmap'd contexts/stacks to force heap growth and page faults. `init_context` and volatile `count` preserve loop progress across segfault recovery.

Dependencies and integration points: requires HTM and ppc64le; uses signal alt stacks, `mmap`, `madvise`, `fork`, and `ucontext_t`.

Risks and test signals: the test returns success unless the kernel crashes/hangs or process setup calls fail. It skips non-64-bit LE environments.
