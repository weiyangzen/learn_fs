# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/hyp/sysreg-sr.h

## Purpose

This header defines inline system-register save/restore routines for host and guest CPU contexts during hyp world switch.

## Important APIs, Types, And Functions

Key helpers are `ctxt_to_vcpu()`, `ctxt_is_guest()`, `ctxt_mdscr_el1()`, `ctxt_midr_el1()`, `__sysreg_save_common_state()`, `__sysreg_save_user_state()`, `__sysreg_save_el1_state()`, `__sysreg_save_el2_return_state()`, matching restore functions, `to_hw_pstate()`, and AArch32 `__sysreg32_{save,restore}_state()`.

## Control Flow

Save functions snapshot common debug/POE, user TPIDR, EL1 translation/control/fault/timer/thread state, optional MTE/TCR2/PIE/POE/SCTLR2 state, return ELR/PSTATE, and RAS DISR/VDISR. Restore functions write VPIDR/VMPIDR and EL1 state, handle speculative AT workaround ordering, translate virtual EL2 PSTATE to hardware EL1 PSTATE, and restore RAS virtual-disrupt state.

## State And Persistence Behavior

The file moves state between live sysregs and `struct kvm_cpu_context::sys_regs`, plus banked AArch32 fields. Feature availability gates optional state fields.

## Dependencies And Integration Points

It is used by VHE/nVHE switch code and depends on KVM feature filtering, writable IMP ID regs, MTE, RAS, S1PIE/S1POE/TCR2/SCTLR2, and speculative AT erratum handling.

## Risks And Test Signals

Risks are restoring host and guest contexts in the wrong order, missing optional feature state, unsafe POR_EL0 timing affecting uaccess, and wrong virtual EL2 PSTATE translation. Test signals include guest sysreg persistence across exits, MTE/TCR2/POE/PIE guests, writable MIDR exposure, AArch32 banked register tests, and speculative-AT workaround platforms.
