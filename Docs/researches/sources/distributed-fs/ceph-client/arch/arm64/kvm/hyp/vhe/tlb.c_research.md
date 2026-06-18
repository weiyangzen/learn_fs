# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vhe/tlb.c

## Purpose
This file implements VHE TLB invalidation helpers for guest VMID contexts and nested virtualization TLBI emulation. Since VHE host execution normally uses EL2/EL0 translation, it temporarily changes HCR_EL2.TGE and stage-2 state so TLBI instructions target the guest EL1/EL0 regime.

## Important APIs, Types, and Functions
- `struct tlb_inv_context` saves previous MMU, IRQ flags, and erratum-protected TCR/SCTLR state.
- `enter_vmid_context()` and `exit_vmid_context()` switch into and out of the target VMID context.
- Flush APIs include `__kvm_tlb_flush_vmid_ipa()`, `__kvm_tlb_flush_vmid_ipa_nsh()`, `__kvm_tlb_flush_vmid_range()`, `__kvm_tlb_flush_vmid()`, `__kvm_flush_cpu_context()`, and `__kvm_flush_vm_context()`.
- `__kvm_tlbi_s1e2()` emulates guest EL2 stage-1 TLBI instructions by remapping them to EL1-equivalent operations.

## Control Flow
For VMID-specific operations, the helper saves IRQ state, records any currently running vCPU MMU that differs from the target, applies erratum protection by blocking speculative EL1 walks when required, loads the target stage-2 context, clears HCR.TGE, issues the relevant TLBI, synchronizes, restores host HCR, reloads the previous stage-2 context if needed, restores erratum-protected sysregs, and restores IRQ state.

IPA flushes invalidate stage-2 for the IPA and then all stage-1 entries to avoid refills from stale combined walks. Range flushes use range TLBI with worst-case page stride. Full VMID flush uses `vmalls12e1is`. CPU context flush also invalidates I-cache. The nested TLBI emulator maps EL2, non-shareable, outer-shareable, and nXS encodings onto inner-shareable EL1 XS operations and returns `-EINVAL` for unsupported encodings.

## State and Persistence
State is transient but highly sensitive: HCR_EL2, stage-2 MMU context, IRQ mask state, TCR_EL1/SCTLR_EL1 under erratum workarounds, and TLB/cache hardware state. It may also restore the running vCPU's previous hardware MMU after flushing a different target.

## Dependencies and Integration Points
It depends on `__load_stage2()`, ARM64 TLBI macros, erratum feature caps, hyp TLB synchronization helpers, and nested virtualization instruction decoders. It is called by page-table code, MMU invalidation code, and VHE fast sysreg trap handling.

## Risks and Edge Cases
The core risks are targeting the host TLB instead of guest TLB, failing to restore HCR.TGE or the previous stage-2 context, and insufficient ordering between stage-2 and stage-1 invalidations. Nested TLBI emulation also risks accepting an unsupported encoding or under-invalidating by preserving non-shareable/nXS semantics that are unsafe for KVM.

## Test Signals
Stress KVM MMU notifier invalidations, VMID rollover, nested EL2 TLBI traps, range TLBI capability on/off, erratum-affected CPU configurations, and concurrent vCPU execution during remote TLB flushes. Failures often manifest as stale translations, data corruption, or host instability after guest TLBI.
