# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal.S

Purpose: shared assembly helper that loads first and second register contexts and sends SIGUSR1 while in a suspended transaction for signal-frame validation tests.

Important APIs/types/functions: exports `tm_signal_self_context_load(pid,gprs,fps,vms,vss)` and uses `load_gpr`, `load_fpu`, `load_vmx`, and `load_vsx` helpers from included assembly headers.

Control flow: the routine saves nonvolatile/vector state, loads non-transactional expected context from non-NULL arrays, starts a transaction, suspends, loads transactional/speculative expected context from the second half of each array, performs raw `kill(SIGUSR1)`, aborts/resumes to force cleanup, then restores saved state and returns.

State and persistence behavior: uses stack storage for parameters and saved registers. It mutates CPU register files only for the duration of the test.

Dependencies and integration points: linked into TM signal-context tests and depends on `basic_asm.h`, `gpr_asm.h`, `fpu_asm.h`, `vmx_asm.h`, and `vsx_asm.h`.

Risks and test signals: hardware may abort before the signal is sent; callers therefore loop and validate the returned pid. Stack-frame offsets and vector save/restore must remain consistent.
