# sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/spte.h

## Purpose
Defines SPTE bit layout, global mask declarations, inline predicates, conversion helpers, writable-state invariants, reserved-bit checks, and exported constructors used by shadow MMU and TDP MMU code.

## Important APIs, Types, and Functions
- Defines `SPTE_MMU_PRESENT_MASK`, `SPTE_TDP_AD_*`, address/permission masks, EPT read/execute masks, MMIO generation fields, `SPTE_MMIO_ALLOWED_MASK`, `SHADOW_NONPRESENT_VALUE`, and `FROZEN_SPTE`.
- Declares global mask variables set in `spte.c`.
- Provides helpers for `spte_index()`, dummy roots, `to_shadow_page()`, `spte_to_child_sp()`, `sptep_to_sp()`, `root_to_sp()`, and `is_mirror_sptep()`.
- Inline state predicates include `is_mmio_spte()`, `is_shadow_present_pte()`, `is_ept_ve_possible()`, `spte_ad_enabled()`, `is_access_track_spte()`, `is_last_spte()`, `is_executable_pte()`, `spte_to_pfn()`, `is_accessed_spte()`, and `is_rsvd_spte()`.
- Writable-state helpers include `is_writable_pte()`, `check_spte_writable_invariants()`, `is_mmu_writable_spte()`, `is_access_allowed()`, and `leaf_spte_change_needs_tlb_flush()`.

## Control Flow
The header is mostly inline logic consumed by fault handlers and TDP mutation paths. Code reads SPTEs, classifies whether they are KVM-present, leaf/non-leaf, MMIO, frozen, access-tracked, or writable, then selects atomic update paths and TLB flush policy. For access tracking, `restore_acc_track_spte()` restores saved EPT R/X bits before permission modification.

## State and Persistence
The header describes the persistent encoding of SPTEs. Software-only bits track KVM-present state, host/MMU writable state, TDP A/D mode, access-tracking saved bits, MMIO generations, and non-present reserved-bit masks. `FROZEN_SPTE` is a transient but persistent-in-memory sentinel used by TDP MMU shared updates.

## Dependencies and Integration Points
Includes VMX constants, `mmu.h`, and `mmu_internal.h`. It is included by SPTE construction, TDP iteration, TDP MMU mutation, shadow paging, fast page fault, MMIO caching, dirty logging, aging, hugepage splitting, and mirrored TDP/TDX paths.

## Risks
Bit allocation pressure is high, especially for EPT and 32-bit/PAE reserved bits. Any overlap among A/D type bits, saved access bits, writable bits, MMIO generation, or L1TF masks can cause hardware faults or security bugs. Flush policy is deliberately narrow; callers must only use `leaf_spte_change_needs_tlb_flush()` for shadow-present leaf changes and separately reason about non-leaf updates.

## Test Signals
Compile-time static asserts, runtime WARNs for writable invariants, tests for MMIO/frozen false positives, A/D-disabled access tracking, EPT #VE suppression checks, fast page fault updates, TLB flush behavior for MMU-writable clearing, and reserved-bit validation across levels.
