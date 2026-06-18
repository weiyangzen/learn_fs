# sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/spte.c

## Purpose
Implements construction and global configuration of KVM x86 shadow page table entries. It centralizes SPTE bit masks, MMIO SPTE encoding, memory-encryption bits, A/D tracking behavior, huge/small SPTE conversion, host-MMIO mapping tracking, and reset/init of architecture-specific PTE masks.

## Important APIs, Types, and Functions
- Global masks such as `shadow_present_mask`, `shadow_accessed_mask`, `shadow_dirty_mask`, `shadow_mmio_value`, `shadow_me_value`, writable masks, and L1TF mitigation masks.
- `kvm_mmu_spte_module_init()` snapshots MMIO caching policy and host MAXPHYADDR.
- `make_mmio_spte()` encodes a non-present MMIO SPTE with memslot generation, access bits, GPA, and L1TF relocation.
- `spte_needs_atomic_update()` decides whether a shadow-present leaf SPTE must be modified atomically.
- `make_spte()` builds a leaf SPTE for a PFN and returns whether write emulation is needed due to write protection.
- `make_small_spte()` and `make_huge_spte()` convert between huge leaf and lower-level leaf encodings.
- `make_nonleaf_spte()` builds a child-page-table SPTE.
- `mark_spte_for_access_track()` and `restore_acc_track_spte()` support A/D-disabled access tracking.
- `kvm_mmu_set_mmio_spte_mask()`, `kvm_mmu_set_mmio_spte_value()`, `kvm_mmu_set_me_spte_mask()`, `kvm_mmu_set_ept_masks()`, and `kvm_mmu_reset_all_pte_masks()` configure runtime masks.

## Control Flow
SPTE generation starts with global mask configuration from module/vendor initialization. `make_spte()` applies A/D mode, present/accessed bits, NX hugepage mitigation, user/read and execute permissions, huge-page bit, vendor memory-type mask, host/MMU writable bits, memory encryption bit, PFN, unsync/write-protect decisions, optional prefetch access tracking, reserved-bit validation, dirty logging, and host-MMIO buffer-clearing tracking. MMIO SPTE setup validates the vendor-provided mask for collisions with generation bits, frozen SPTEs, L1TF relocation, and allowed MMIO bit ranges, disabling caching on unsafe configuration.

## State and Persistence
Most state is `__read_mostly` global mask configuration shared by all VMs plus per-VM `kvm->arch.shadow_mmio_value`. SPTEs themselves persist in shadow/TDP page tables and encode host-writable/MMU-writable, A/D mode, MMIO generation, PFN, and mitigation bits. `root->has_mapped_host_mmio` and `kvm->arch.has_mapped_host_mmio` record whether CPUs need outside-guest requests for host MMIO exposure.

## Dependencies and Integration Points
Uses `mmu.h`, `mmu_internal.h`, `x86.h`, `spte.h`, E820 memory-range queries, PAT/memtype helpers, VMX EPT constants, vendor `get_mt_mask`, memslot dirty logging, NX hugepage mitigation, L1TF mitigation, CLEAR_CPU_BUF_VM_MMIO mitigation, and KVM request delivery.

## Risks
Mask overlap mistakes can create MMIO cache false positives, reserved-bit faults, or L1TF exposure; the file contains many `WARN_ON`/`BUG_ON` guards for these invariants. Dropping dirty bits or writable bits non-atomically can lose guest state. `make_spte()` relies on callers not replacing PFNs without first zapping old mappings. Memory type classification of reserved PFNs is performance-sensitive and must avoid treating DAX-like reserved RAM as MMIO.

## Test Signals
Cover SPTE construction across shadow paging and EPT, A/D enabled/disabled/write-protect-only modes, MMIO cache hit generation wrapping, L1TF mask behavior, NX hugepage mitigation, dirty logging, host writable versus MMU writable combinations, memory encryption masks, host-MMIO detection, hugepage split/recover conversions, and vendor EPT mask setup.
