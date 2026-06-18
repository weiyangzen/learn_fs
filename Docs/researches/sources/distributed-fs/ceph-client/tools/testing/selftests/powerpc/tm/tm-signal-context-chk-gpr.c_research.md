# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-context-chk-gpr.c

Purpose: validates that nonvolatile GPR checkpoint and speculative states are placed in the correct signal contexts for TM signal delivery.

Important APIs/types/functions: expected `gprs[]` covers r14-r31 for first and second contexts; `signal_usr1()` compares `gp_regs`; `tm_signal_context_chk_gpr()` drives repeated helper calls.

Control flow: after installing the signal handler and HTM skips, the test repeatedly calls `tm_signal_self_context_load(pid, gprs, NULL, NULL, NULL)`. The handler checks primary `ucontext` for checkpointed values and `uc_link` for speculative values.

State and persistence behavior: `broken` and `fail` are signal-visible globals. Expected data is static.

Dependencies and integration points: uses `tm-signal.S` and powerpc signal frame register indices.

Risks and test signals: mismatches are printed with GPR number and expected value. Helper return must equal pid or the test fails immediately.
