# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/sigfuz.c

Purpose: TM-aware signal and sigreturn fuzzer that mutates signal contexts, TM state, and MSR transaction-state bits to catch kernel crashes or hangs.

Important APIs/types/functions: option bits `ARG_MESS_WITH_TM_AT`, `ARG_MESS_WITH_TM_BEFORE`, `ARG_MESS_WITH_MSR_AT`, `ARG_FOREVER`; `mess_with_tm()`, `trap_signal_handler()`, `seg_signal_handler()`, `sigfuz_test()`, and `signal_fuzzer()`.

Control flow: multiple pthreads repeatedly fork children. Each child optionally enters or suspends TM, raises `SIGUSR1`, and lets the handler randomize `ucontext_t` and `uc_link` fields, including MSR, NIP, trap, DSISR, DAR, and other mcontext slots. SIGSEGV exits cleanly so fuzz iterations can continue.

State and persistence behavior: global arguments control mode, `tmp_uc` is per-process mutable heap state, and random context mutations are intentionally not reproducible unless the seed path is controlled.

Dependencies and integration points: uses HTM instructions inline, pthreads, signal APIs, `ucontext_t`, and powerpc register constants from `utils.h`.

Risks and test signals: this is a crash-resilience test, not a semantic validator. Success means no kernel crash under the fuzz run; user-space segfaults are expected and handled.
