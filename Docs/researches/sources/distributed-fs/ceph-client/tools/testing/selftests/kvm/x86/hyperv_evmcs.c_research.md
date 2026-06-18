# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_evmcs.c

Purpose: Provides broad regression coverage for Hyper-V enlightened VMCS, including nested state save/restore, eVMCS pointer behavior, invalid revision handling, NMI exits, enlightened MSR bitmap behavior, direct nested TLB flush hypercalls, synthetic exits, and invalid enlightened `vmptrld`.

Important APIs/types/functions: `guest_ud_handler()` counts invalid-opcode traps for bad eVMCS use; `guest_nmi_handler()` consumes injected NMI; `l2_guest_code()` issues syncs, `VMCALL`, `RDMSR`, and Hyper-V flush hypercalls; `guest_code()` sets up VMX/eVMCS and performs nested checks; `inject_nmi()` manipulates `KVM_SET_VCPU_EVENTS`; `save_restore_vm()` exercises `KVM_GET/SET_NESTED_STATE` via full vCPU save/load. It uses Hyper-V VP assist, partition assist, direct hypercall controls, and VMX MSR bitmaps.

Control flow: The guest enables Hyper-V guest OS ID/hypercall page, x2APIC, VP assist, and eVMCS, then launches L2. The host runs through numbered sync stages and after each stage saves VM/vCPU state, recreates the VM, reloads state, and verifies registers match. At stage 8 it injects NMI before L2 resumes; at stage 9 it performs an extra nested-state save/restore. L1 then tests invalid eVMCS revision, NMI exit reason, MSR bitmap clean-field behavior, direct nested flush handling, synthetic trap-after-flush exit, and invalid eVMCS pointer behavior.

State and persistence behavior: The test deliberately persists nested state through save/restore cycles. Critical state includes eVMCS GPA/content, VP assist page, partition assist page, Hyper-V synthetic MSRs, NMI pending state, MSR bitmaps, and L2 RIP. State must survive `kvm_vm_release()` and recreation.

Dependencies and integration points: Requires VMX, `KVM_CAP_NESTED_STATE`, `KVM_CAP_HYPERV_ENLIGHTENED_VMCS`, Hyper-V nested direct flush, selftest VMX and Hyper-V helpers, and correct `KVM_GET/SET_NESTED_STATE` serialization.

Risks and maintenance notes: This test is dense and sensitive to eVMCS clean-field semantics. Guest code notes that L1 does not preserve all GPRs during vmexits, so inline assembly clobbers broadly. The stage protocol must remain in lockstep with host save/restore expectations.

Test signals: Passing demonstrates eVMCS nested execution remains correct across state migration, NMI delivery, MSR bitmap updates, and nested flush hypercalls. Failures are high-signal for eVMCS state serialization or Hyper-V nested enlightenment regressions.
