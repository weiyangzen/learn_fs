# sources/distributed-fs/ceph-client/arch/x86/kvm/svm/hyperv.h

## Purpose
`hyperv.h` defines SVM-specific inline helpers for Hyper-V nested enlightenment state. It bridges the enlightened VMCB fields in SVM's nested control cache to KVM's generic Hyper-V vCPU state and provides feature checks for direct L2 TLB flush hypercalls.

## Important APIs, types, and functions
- `nested_svm_hv_update_vm_vp_ids()` copies `partition_assist_page`, `hv_vm_id`, and `hv_vp_id` from `svm->nested.ctl.hv_enlightenments` into `hv_vcpu->nested`.
- `nested_svm_l2_tlb_flush_enabled()` checks the enlightened VMCB control bit and the Hyper-V VP assist direct-hypercall feature.
- `nested_svm_is_l2_tlb_flush_hcall()` combines guest CPUID exposure, the nested flush enablement check, and `kvm_hv_is_tlb_flush_hcall()`.
- `svm_hv_inject_synthetic_vmexit_post_tlb_flush()` is declared when `CONFIG_KVM_HYPERV` is enabled and stubbed otherwise.

## Control flow
Nested SVM copies enlightened VMCB control fields into its cache and then calls `nested_svm_hv_update_vm_vp_ids()` during nested guest entry. When L2 executes a VMMCALL, nested SVM's special-exit path consults `nested_svm_is_l2_tlb_flush_hcall()` so L0 can handle direct flush hypercalls instead of forwarding them to L1 as generic VMMCALL exits. If L0 must notify L1 after the flush, the implementation in `hyperv.c` injects a synthetic exit.

## State and persistence behavior
The helper persists Hyper-V nested VM/VP identifiers and the partition assist page GPA in `struct kvm_vcpu_hv`. It does not allocate memory. Its output remains tied to the currently cached vmcb12 control state and must be refreshed when L1 changes enlightened VMCB fields.

## Dependencies and integration points
The header depends on `asm/mshyperv.h`, KVM's generic x86 Hyper-V support (`../hyperv.h`), and SVM internals (`svm.h`). It is called from `nested.c` during guest entry and special-exit classification. The `#ifdef CONFIG_KVM_HYPERV` stubs keep the nested SVM code buildable without Hyper-V support.

## Risks and edge cases
The helpers must tolerate `to_hv_vcpu(vcpu)` returning NULL. TLB flush acceleration is allowed only when both L1's enlightened VMCB and L2's VP assist page opt in; missing either condition falls back to ordinary nested exit handling. Stale VM/VP IDs are possible if callers fail to refresh after vmcb12 changes.

## Test signals
Relevant tests exercise nested Hyper-V enlightened VMCB with and without VP assist direct hypercalls, verify fallback behavior when `CONFIG_KVM_HYPERV` is absent, and validate VM/VP ID propagation across VMRUN, migration, and clean-field optimizations.
