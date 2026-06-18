# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-context-chk-vsx.c

Purpose: validates VSX state reconstruction from FP and VMX-reserve parts of the signal frame for checkpointed and speculative TM contexts.

Important APIs/types/functions: `vsxs[]` holds expected vsr20-vsr31 values; `signal_usr1()` reconstructs each VSX register from `fp_regs` high doubleword and the least-significant VSX slots after `v_regs`; `tm_signal_context_chk()` drives helper calls.

Control flow: the helper seeds VSX values before and during a suspended transaction, then sends SIGUSR1. The handler rebuilds and compares primary-context VSX values and `uc_link` values separately.

State and persistence behavior: global `broken/fail` signal test outcome; expected vectors are static.

Dependencies and integration points: depends on powerpc UAPI signal frame layout, VSX/Altivec compiler support, real HTM, and `tm-signal.S`.

Risks and test signals: the test encodes detailed assumptions about `mcontext_t.v_regs` and VSX/FPR overlap. Mismatches print compact byte dumps and expected vector words.
