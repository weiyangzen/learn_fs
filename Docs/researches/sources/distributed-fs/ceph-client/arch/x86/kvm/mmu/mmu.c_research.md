# sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/mmu.c

## Purpose

`mmu.c` is the central x86 KVM MMU implementation. It owns shadow page table allocation, SPTE mutation, reverse-map maintenance, guest page-fault handling, MMU context initialization, root caching, invalidation, dirty/access tracking, hugepage splitting/recovery, NX hugepage mitigation, and private/shared memory attribute handling. It bridges common KVM memory-slot and MMU-notifier infrastructure with x86-specific paging modes, TDP/EPT/NPT support, nested virtualization, and architecture hooks in `kvm_x86_ops`.

The file supports both legacy shadow MMU and direct/TDP modes. When TDP hardware is available, it delegates many direct-root operations to `tdp_mmu.c`; otherwise it builds and maintains shadow page tables directly. Even with TDP enabled, this file remains responsible for nested shadow MMU paths, common page-fault orchestration, module parameters, and VM/vCPU lifecycle hooks.

## Important APIs, Types, And Functions

Key global configuration and module parameters:

- `nx_huge_pages`, `nx_huge_pages_recovery_ratio`, and `nx_huge_pages_recovery_period_ms` control the iTLB multihit mitigation and background recovery of zapped hugepage opportunities.
- `force_flush_and_sync_on_reuse` optionally forces sync and TLB flushes when reusing cached roots.
- `tdp_enabled`, `tdp_mmu_allowed`, `tdp_mmu_enabled`, `tdp_root_level`, `max_tdp_level`, and `max_huge_page_level` capture runtime MMU mode and hardware limits.

Important local structures:

- `struct pte_list_desc` is a compact custom list for SPTE pointers in rmaps and parent-PTE lists. It optimizes the common one-or-few SPTE case while allowing many aliases.
- `struct kvm_shadow_walk_iterator` walks shadow page tables from root to leaf.
- `struct kvm_mmu_role_regs` snapshots CR0, CR4, and EFER fields used to derive `union kvm_cpu_role` and `union kvm_mmu_page_role`.
- `struct kvm_mmu_pages` and `struct mmu_page_path` batch unsync-child walks.
- `struct shadow_page_caches` passes the per-vCPU or per-VM memory caches needed to allocate shadow pages.

SPTE mutation helpers are deliberately layered: `mmu_spte_set()` installs a nonpresent-to-present SPTE, `mmu_spte_update()` updates a present SPTE without changing PFN and reports whether a TLB flush is needed, `mmu_spte_clear_track_bits()` clears a leaf SPTE and updates page accounting, `mmu_spte_clear_no_track()` clears metadata/non-leaf entries, and `mmu_spte_get_lockless()` reads SPTEs safely for lockless walks.

Reverse-map and page tracking APIs include `pte_list_add()`, `pte_list_remove()`, `pte_list_count()`, `gfn_to_rmap()`, `rmap_add()`, `drop_spte()`, `rmap_write_protect()`, `__rmap_clear_dirty()`, `kvm_mmu_slot_gfn_write_protect()`, `kvm_age_gfn()`, `kvm_test_age_gfn()`, and `kvm_unmap_gfn_range()`. These connect SPTEs back to memslot GFNs so KVM can write-protect, clear dirty/accessed state, age mappings, and zap ranges.

Shadow-page lifecycle functions include `kvm_mmu_find_shadow_page()`, `kvm_mmu_alloc_shadow_page()`, `kvm_mmu_get_shadow_page()`, `link_shadow_page()`, `mmu_page_zap_pte()`, `kvm_mmu_prepare_zap_page()`, `kvm_mmu_commit_zap_page()`, `kvm_mmu_zap_oldest_mmu_pages()`, and `kvm_mmu_change_mmu_pages()`. Page-fault handling centers on `kvm_handle_page_fault()`, `kvm_mmu_page_fault()`, `kvm_mmu_do_page_fault()`, `direct_page_fault()`, `kvm_tdp_mmu_page_fault()`, `fast_page_fault()`, `kvm_mmu_faultin_pfn()`, `direct_map()`, and `mmu_set_spte()`.

MMU context and lifecycle APIs include `kvm_configure_mmu()`, `kvm_init_mmu()`, `kvm_init_shadow_npt_mmu()`, `kvm_init_shadow_ept_mmu()`, `kvm_mmu_reset_context()`, `kvm_mmu_load()`, `kvm_mmu_unload()`, `kvm_mmu_free_roots()`, `kvm_mmu_new_pgd()`, `kvm_mmu_free_obsolete_roots()`, `kvm_mmu_create()`, `kvm_mmu_destroy()`, `kvm_mmu_init_vm()`, `kvm_mmu_uninit_vm()`, and module init/exit functions.

## Control Flow

VM setup initializes `kvm->arch.active_mmu_pages`, NX hugepage lists, split caches, TDP MMU state if enabled, and the shadow-page hash otherwise. vCPU setup initializes the per-vCPU MMU caches and root/guest MMU contexts, including PAE root pages when needed.

MMU mode selection starts in `kvm_init_mmu()`. It snapshots CR0/CR4/EFER, derives `union kvm_cpu_role`, then chooses nested MMU, TDP MMU, or software shadow MMU initialization. The initialization path sets function pointers for `page_fault`, `gva_to_gpa`, `sync_spte`, `get_guest_pgd`, and exception injection, and refreshes reserved-bit, permission, PKRU, and zero-bit masks.

The primary page-fault flow is: `kvm_handle_page_fault()` handles async-PF flags and calls `kvm_mmu_page_fault()`; `kvm_mmu_page_fault()` handles MMIO reserved-bit faults and calls `kvm_mmu_do_page_fault()`; `kvm_mmu_do_page_fault()` builds a normalized `struct kvm_page_fault` and dispatches to the current MMU handler; direct/TDP faults try `fast_page_fault()`, fault in the PFN, take `mmu_lock`, reject stale faults, and map through `direct_map()` or `kvm_tdp_mmu_map()`; `mmu_set_spte()` installs the final SPTE or MMIO SPTE and updates rmap/accounting.

Invalidation flows preserve ordering through `mmu_lock`, `slots_lock`, mmu-notifier sequence numbers, remote TLB flushes, and vCPU requests. Range zaps call `kvm_mmu_invalidate_begin()`, add the range, zap rmaps and TDP leaves, flush if required, and end invalidation. Fast global zaps flip `mmu_valid_gen`, request all vCPUs to free obsolete roots, zap obsolete pages in batches, and then zap invalidated TDP roots.

## State And Persistence Behavior

This file keeps only in-kernel runtime state. Main VM-level state lives under `kvm->arch`: `active_mmu_pages`, `mmu_page_hash`, `n_used_mmu_pages`, `n_max_mmu_pages`, `indirect_shadow_pages`, `mmu_valid_gen`, split allocation caches, possible NX hugepage lists, and the NX recovery vhost task. Memslot architecture state stores rmaps and `lpage_info` disallow/mixed flags.

Main vCPU-level state lives under `vcpu->arch`: `root_mmu`, `guest_mmu`, `nested_mmu`, current `mmu` and `walk_mmu` pointers, root cache entries, PAE/PML4/PML5 special roots, MMIO cache, async-PF token state, fault counters, and memory caches.

Shadow pages are keyed by role and GFN in `mmu_page_hash`, linked FIFO on `active_mmu_pages`, and may be referenced by parent-PTE lists and memslot rmaps. Root pages carry `root_count`; non-root invalid pages move to an invalid list and are freed after a remote TLB flush. TDP MMU pages use separate root/reference and RCU behavior in `tdp_mmu.c`.

## Dependencies And Integration Points

Internal KVM dependencies include `mmu.h`, `mmu_internal.h`, `tdp_mmu.h`, `spte.h`, `paging_tmpl.h`, `page_track.h`, `kvm_cache_regs.h`, `x86.h`, nested VMX/SVM hooks, `kvm_x86_ops`, and generic KVM memory-slot/MMU-notifier APIs. Linux dependencies include module parameters, slab/page allocators, SRCU/RCU, rwlocks/spinlocks, memory-management page-table walking helpers, GUP/fault-in helpers, signals, vhost task workers, and tracepoints.

The file integrates with userspace-visible behavior through KVM_RUN page-fault exits, `KVM_EXIT_MEMORY_FAULT` preparation for private/shared mismatches, dirty logging ioctls, memory attributes, memslot changes, APIC access page handling, and prefault APIs.

## Risks And Edge Cases

The highest-risk areas are concurrency and ordering. SPTE writes must maintain architecture-visible atomicity, especially on 32-bit hosts. Lockless walks rely on `vcpu->mode`, IRQ disabling or TDP lockless walk guards, remote TLB flush ordering, and acquire/release semantics on rmap locks.

Race handling with mmu-notifier invalidations is subtle. Fault paths snapshot `mmu_invalidate_seq`, check before and after PFN fault-in, then recheck under `mmu_lock`. Incorrect ordering can install stale SPTEs after host mappings or private/shared attributes changed.

Shadow-page unsync handling is correctness-critical. `mmu_try_to_unsync_pages()` uses barriers so that write-enabled SPTEs do not become visible before the shadow page is marked unsync; root synchronization relies on the matching read barrier in `is_unsync_root()`.

Hugepage logic has several constraints: dirty logging requires 4 KiB granularity, NX hugepage mitigation disallows executable hugepages in vulnerable configurations, guest_memfd/private memory can impose lower maximum mapping levels, and mixed memory attributes must prevent shared/private hugepage coalescing.

## Test Signals

Useful runtime signals include KVM selftests that cover page faults, dirty logging, access tracking, memslot updates, MMU notifier races, guest_memfd/private memory, memory attributes, nested EPT/NPT, INVLPG/INVPCID, and prefault APIs. Tracepoints from `mmutrace.h` can confirm SPTE creation, fast page fault outcomes, MMIO SPTE generation checks, shadow-page sync/unsync/zap, and hugepage splitting.

Kernel lockdep, `CONFIG_KVM_PROVE_MMU`, `KVM_BUG_ON_DATA_CORRUPTION`, and WARN paths are important validation signals for rmap integrity, root state, SPTE reserved bits, and unexpected invalid pages. Dirty logging tests should watch for lost dirty bits after hugepage splits, PML interaction, and fast write-fault repairs. Private memory tests should validate that shared/private mismatches produce memory-fault exits instead of indefinite page-fault loops.
