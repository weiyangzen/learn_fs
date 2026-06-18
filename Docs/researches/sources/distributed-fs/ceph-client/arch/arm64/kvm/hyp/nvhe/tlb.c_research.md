<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/tlb.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/tlb.c

## Purpose
`tlb.c` implements nVHE TLB and instruction-cache maintenance for host and guest stage-2 contexts. It temporarily switches VMID/stage-2 context when needed, applies architecture workarounds for speculative address translation, and issues shareable or non-shareable invalidation sequences.

## Important APIs, Types, and Functions
`struct tlb_inv_context` records the previous MMU context and workaround register state. `enter_vmid_context()` switches from host or guest context into the target MMU’s VMID, with required barriers and optional TCR/SCTLR manipulation for `ARM64_WORKAROUND_SPECULATIVE_AT`. `exit_vmid_context()` restores the prior context. Public operations include `__kvm_tlb_flush_vmid_ipa()`, `__kvm_tlb_flush_vmid_ipa_nsh()`, `__kvm_tlb_flush_vmid_range()`, `__kvm_tlb_flush_vmid()`, `__kvm_flush_cpu_context()`, and `__kvm_flush_vm_context()`.

## Control Flow, State, and Persistence
Each targeted flush enters the requested VMID, performs TLBI operations, executes required DSB/ISB synchronization, and restores the previous stage-2. IPA flushes also invalidate stage-1 because only IPA is known. CPU-context flush invalidates local stage-1 and I-cache. VM-context flush invalidates all EL1 inner-shareable TLBs without a VMID switch.

## Dependencies and Integration Points
It depends on `host_mmu` from `mem_protect.c`, `kvm_host_data.__hyp_running_vcpu`, stage-2 load helpers, arm64 TLBI macros, speculative-AT alternatives, and host hypercall wrappers in `hyp-main.c`.

## Risks and Test Signals
Risks include leaving the wrong VMID loaded, insufficient barriers leading to stale complete walks, mishandling guest context when called outside `__kvm_vcpu_run()`, and workaround register restore bugs. Test signals are dirty-log/unmap permission-change correctness, host and guest TLB shootdown stress, nested calls from host vs guest context, non-shareable flush users, and CPUs affected by ARM 1319367/1319537 style workarounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/tlb.c -->
