<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500_emulate.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500_emulate.c

Purpose: Implements e500-specific privileged instruction and SPR emulation on top of the generic BookE emulator, including e500 TLB operations, doorbells, cache-lock behavior, thread-management reads, EHPRIV debug exits, and Freescale SPRs.

Important APIs/types/functions: Provides `kvmppc_core_emulate_op_e500()`, `kvmppc_core_emulate_mtspr_e500()`, and `kvmppc_core_emulate_mfspr_e500()`. Internal helpers cover doorbell priority mapping, `msgsnd`, `msgclr`, `ehpriv`, `dcbtls`, and `mftmr`. It dispatches TLB instructions to `kvmppc_e500_emul_tlbre/tlbwe/tlbsx/tlbilx/tlbivax()` and MMUCSR0 writes to `kvmppc_e500_emul_mt_mmucsr0()`.

Control flow: Opcode emulation handles primary opcode 31 e500 extensions first, computes effective addresses for TLB instructions, and falls back to `kvmppc_booke_emulate_op()` on failure. SPR write emulation updates PR-mode PID/MAS backing state, cache/HID registers, MMUCSR0 side effects, power-management state, extra IVORs, and falls back to generic BookE SPR writes. SPR read emulation returns PID/MAS, TLB config/page-size, cache/HID/SVR/MMUCFG/EPTCFG, power-management, and extra IVOR state, again falling back to generic BookE reads.

State and persistence: Updates vCPU shared MAS registers, e500 private PID array, L1CSR0/1, HID0/1, SVR, guest TLB configuration fields, EP/TLB page-size state, power management control, pending doorbell exceptions, and extra IVOR vectors for SPE, AltiVec, performance monitor, and HV doorbell interrupts.

Dependencies and integration points: Depends on BookE generic emulation, e500 TLB emulation, PowerPC disassembly helpers, doorbell constants, e500 private state, and KVM exit accounting/debug ABI.

Risks: Doorbell emulation contains a suspicious call to `dbell2prio(rb)` in `kvmppc_e500_emul_msgsnd()` rather than using the decoded parameter, which can misclassify message type. SPR handling differs under `CONFIG_KVM_BOOKE_HV`, so PR/HV coverage matters. Cache and branch-predictor SPRs are approximated and may not match hardware side effects exactly.

Test signals: e500 guest TLB instruction tests, Linux guest boot with MAS/PID activity, doorbell send/clear tests on e500mc, EHPRIV debug-exit tests, SPR get/set migration round trips, cache-control instruction tests, and config-matrix builds for SPE/AltiVec/HV are relevant.

Source read size: 452 lines, 9851 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500_emulate.c -->
