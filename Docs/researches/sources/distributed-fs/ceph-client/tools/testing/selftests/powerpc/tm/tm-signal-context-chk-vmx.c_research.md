# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-context-chk-vmx.c

Purpose: verifies VMX/Altivec nonvolatile register state is split correctly between checkpointed and speculative signal contexts under TM.

Important APIs/types/functions: `vms[]` holds expected `vector int` values for vr20-vr31 in both contexts; `signal_usr1()` compares `uc_mcontext.v_regs->vrregs`; `tm_signal_context_chk()` invokes `tm_signal_self_context_load()`.

Control flow: the assembly helper loads first and second VMX values around a suspended transaction and sends SIGUSR1. The handler compares primary context VMX20-31 against first half of `vms[]` and `uc_link` VMX20-31 against the second half.

State and persistence behavior: static vector expectations and global `broken` carry state. No external persistence.

Dependencies and integration points: requires VMX signal frame layout, Altivec compiler support, real HTM, and `tm-signal.S`.

Risks and test signals: mismatch diagnostics print actual and expected vector hex. The printed second-context label uses `NV_VMX_REGS + i` instead of `VMX20 + i`, a diagnostic-only numbering issue.
