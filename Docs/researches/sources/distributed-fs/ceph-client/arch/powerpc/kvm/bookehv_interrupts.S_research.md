<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/bookehv_interrupts.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/bookehv_interrupts.S

Purpose: Provides BookE HV/GS-mode low-level KVM guest entry and exit handlers for e500mc/e6500-style hardware virtualization, derived from the PR-mode assembly but using PACA exception save areas, guest state registers, and HV-specific MAS handling.

Important APIs/types/functions: Defines common handler macro `kvm_handler_common`, 64-bit and 32-bit `kvm_handler`/`kvm_lvl_handler` variants, exception handlers named `kvmppc_handler_<int>_<srr1>`, `kvmppc_resume_host`, and `__kvmppc_vcpu_run`. It uses flags `NEED_EMU`, `NEED_DEAR`, and `NEED_ESR` to decide what state each exception must preserve.

Control flow: HV exception stubs retrieve the current vCPU from PACA or thread state, save clobbered volatile registers and SRR/CSRR/MCSRR/GSRR/DSRR state, restore host stack/PID, optionally collect ESR/DEAR or mark last instruction fetch failed, then branch to `kvmppc_resume_host`. The resume path saves guest SPRGs, VRSAVE, MAS registers, XER/LR, restores host MAS4/MAS6 and EPCR behavior, calls `kvmppc_handle_exit()`, and either reloads guest state for another `rfi` or returns to C. Guest entry saves host state, loads guest PID, MAS registers, SPRGs, VRSAVE, volatile/nonvolatile GPRs, MSR/PC, and enters the guest.

State and persistence: Manages guest and host GPRs, CR, CTR, LR, XER, PID, MAS0-7, MAS4/MAS6 host backups, EPCR DMIUH, SPRG4-9, VRSAVE, shared MSR, PC, DEAR, ESR, last instruction sentinel, timing fields, and host stack/nonvolatile registers. It also contains guest doorbell, critical, machine-check, debug, TLB, LRAT, HV-privilege, and HV-syscall exit paths.

Dependencies and integration points: Depends on BookE HV asm ABI, PACA exception layouts, `asm-offsets`, 64e exception definitions, KVM BookE C exit handling, e500 MMU/MAS emulation, and guest doorbell pending-interrupt support.

Risks: The code is highly sensitive to 32-bit versus 64-bit save-area differences, PACA offset correctness, MAS register ordering, and EPCR DMIUH toggling. Missing state save on an exception class can break emulation or corrupt guest TLB state. Branch-target-buffer flush sections are security-sensitive.

Test signals: e500mc/e6500 HV guest boot, TLB miss and LRAT tests, MAS register stress, guest doorbells, HV privileged instruction exits, debug/critical/machine-check paths, 32-bit and 64-bit BookE HV builds, and objdump validation against asm-offset changes are key signals.

Source read size: 673 lines, 19481 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/bookehv_interrupts.S -->
