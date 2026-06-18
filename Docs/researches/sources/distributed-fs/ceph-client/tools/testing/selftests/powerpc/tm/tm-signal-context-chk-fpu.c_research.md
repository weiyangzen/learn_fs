# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-context-chk-fpu.c

Purpose: verifies signal frame placement of checkpointed and speculative nonvolatile FPR state when a signal is delivered during TM.

Important APIs/types/functions: `tm_signal_self_context_load()` assembly helper seeds contexts; `signal_usr1()` checks `uc_mcontext.fp_regs`; `tm_signal_context_chk_fpu()` loops until `MAX_ATTEMPT` or mismatch.

Control flow: the helper loads first-context FPR14-FPR31 values, begins/suspends a transaction, loads second-context values, and sends SIGUSR1. The handler expects checkpointed values in the primary context and speculative values in `uc_link`.

State and persistence behavior: static `fps[]` contains expected first and second context values. `broken` persists the first detected mismatch.

Dependencies and integration points: depends on `tm-signal.S`, HTM, signal frame `ucontext_t`, and FPU register layout.

Risks and test signals: hardware aborts before suspend can make helper delivery intermittent, so the test loops many times. Mismatches print register names and expected/actual values.
