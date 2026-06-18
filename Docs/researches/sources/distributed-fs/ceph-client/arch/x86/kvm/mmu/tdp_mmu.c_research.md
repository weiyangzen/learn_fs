# sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/tdp_mmu.c

## Purpose
Implements KVM's two-dimensional paging MMU for x86. It owns TDP root lifetime, page-table allocation/freeing, SPTE mutation bookkeeping, TDP fault mapping, zapping, invalidation, aging, dirty logging, hugepage splitting/recovery, write protection, lockless walks, and mirrored TDP support for private memory/TDX-like external page tables.

## Important APIs, Types, and Functions
- VM lifecycle: `kvm_mmu_init_tdp_mmu()`, `kvm_mmu_uninit_tdp_mmu()`, `kvm_tdp_mmu_alloc_root()`, `kvm_tdp_mmu_put_root()`.
- Root iteration and invalidation: `tdp_mmu_next_root()`, `kvm_tdp_mmu_invalidate_roots()`, `kvm_tdp_mmu_zap_invalidated_roots()`, `kvm_tdp_mmu_zap_all()`.
- SPTE bookkeeping: `handle_changed_spte()`, `handle_removed_pt()`, `tdp_mmu_set_spte_atomic()`, `tdp_mmu_set_spte()`, and external mirrored helpers.
- Fault handling: `kvm_tdp_mmu_map()`, `tdp_mmu_map_handle_target_level()`, `tdp_mmu_link_sp()`, `tdp_mmu_split_huge_page()`.
- Range operations: `kvm_tdp_mmu_zap_leafs()`, `kvm_tdp_mmu_unmap_gfn_range()`, `kvm_tdp_mmu_age_gfn_range()`, `kvm_tdp_mmu_test_age_gfn()`, `kvm_tdp_mmu_wrprot_slot()`, dirty clear helpers, hugepage split/recovery, and `kvm_tdp_mmu_write_protect_gfn()`.
- Walk helpers: `kvm_tdp_mmu_get_walk()` and `kvm_tdp_mmu_fast_pf_get_last_sptep()`.

## Control Flow
Root allocation searches for an existing valid root under read lock, rechecks under `tdp_mmu_pages_lock`, allocates and links a root with two references, then stores its HPA in the vCPU MMU root or mirror root. Mapping handles a TDP violation by adjusting hugepage goals, walking from the root to the GFN, splitting huge SPTEs or linking child pages when needed, and installing a final leaf/MMIO SPTE atomically under read `mmu_lock`. SPTE changes funnel through `handle_changed_spte()`, which validates no present leaf is replaced by a different PFN, updates stats, and recursively frees removed child page tables. Zapping walks TDP roots with RCU protection, optional yielding, and SHADOW_NONPRESENT/FROZEN transitions to safely detach leaves or subtrees. Dirty, aging, write-protect, split, and recover paths use the same iterator and SPTE helpers with lock mode dependent atomicity.

## State and Persistence
Persistent VM state includes `kvm->arch.tdp_mmu_roots`, `tdp_mmu_pages_lock`, per-root `tdp_mmu_root_count`, invalid/scheduled-zap flags, page table pages, `struct kvm_mmu_page` metadata, possible NX hugepage tracking, page stats, and mirrored external SPT pointers. Freed TDP pages are RCU-deferred to protect lockless/reader walks. Dirty/accessed state is stored in SPTE bits and memslot dirty state, while invalid root references persist until zapping puts the TDP MMU's root reference.

## Dependencies and Integration Points
Depends on `mmu.h`, `mmu_internal.h`, `mmutrace.h`, `tdp_iter.h`, `tdp_mmu.h`, `spte.h`, tracepoints, cmpxchg, RCU, and vendor hooks for mirrored/external page tables (`set_external_spte`, `link_external_spt`, `remove_external_spte`, `free_external_spt`). Integrates with MMU notifiers, memslot invalidation, fast page faults, dirty logging/PML policy, NX hugepage mitigation, private/shared GFN filtering, TLB flushing, and page fault return codes.

## Risks
This is highly concurrency-sensitive. Bugs in refcounting, invalid-root zapping, RCU freeing, or flush ordering can cause use-after-free or stale translations. Replacing present leaf SPTEs with different PFNs is treated as fatal because it implies a missed notifier. Mirrored roots require special ordering with external page tables and can intentionally leak external pages on unrecoverable free failure. Yielding must preserve forward progress and flush when required. Atomic update failures must retry without leaking newly allocated shadow pages.

## Test Signals
Coverage should include concurrent vCPU faults, memslot deletion/unmap, invalid-root fast zap, VM teardown, lockless walks, fast page faults, TDX/private mirrored root mapping and zapping, dirty logging with A/D enabled and write-protect-only modes, aging/test-young notifiers, hugepage split/recovery, NX hugepage zap, write-track GFN protection, and TLB flush expectations for leaf/non-leaf changes.
