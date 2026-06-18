# Research Group subset-b-000895

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/page_track.c -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/page_track.c

## Purpose
Implements KVM x86 guest page write tracking. The file maintains per-memslot write-track reference counts, write-protects tracked GFNs, blocks large-page mappings for tracked pages, and optionally exposes an external notifier API under `CONFIG_KVM_EXTERNAL_WRITE_TRACKING`. Its immediate consumers are the MMU write-protection paths and external users that need callbacks when guest memory writes are emulated or memslots are removed.

## Important APIs, Types, and Functions
- `kvm_page_track_write_tracking_enabled()` enables tracking if external tracking is active, a shadow root exists, or TDP is disabled.
- `kvm_page_track_create_memslot()`, `kvm_page_track_write_tracking_alloc()`, and `kvm_page_track_free_memslot()` allocate/free `slot->arch.gfn_write_track`.
- `__kvm_write_track_add_gfn()` and `__kvm_write_track_remove_gfn()` update per-GFN counters under `mmu_lock`, adjust large-page eligibility, and write-protect mappings on add.
- `kvm_gfn_is_write_tracked()` reads the per-slot count with `READ_ONCE`.
- External-tracking-only APIs include `kvm_page_track_init()`, `kvm_page_track_cleanup()`, `kvm_page_track_register_notifier()`, `kvm_page_track_unregister_notifier()`, `__kvm_page_track_write()`, `kvm_page_track_delete_slot()`, `kvm_write_track_add_gfn()`, and `kvm_write_track_remove_gfn()`.

## Control Flow
Memslot creation calls `kvm_page_track_create_memslot()`, which allocates tracking storage only when tracking can be used. External registration first validates the VM belongs to the current mm, enables external write tracking by allocating metadata for all slots, then inserts a notifier into an RCU hlist under `mmu_lock`. Adding a tracked GFN increments the slot counter, disallows large pages for that GFN, and invokes `kvm_mmu_slot_gfn_write_protect()`, flushing remote TLBs if SPTEs changed. Emulated writes call the header wrapper `kvm_page_track_write()`, which first dispatches external notifier callbacks through SRCU and then notifies KVM's internal MMU tracking.

## State and Persistence
The persistent VM state is `kvm->arch.external_write_tracking_enabled`, `kvm->arch.track_notifier_head`, and each slot's `arch.gfn_write_track` array. Counts are reference counts, not booleans, so multiple users can track the same GFN. Memory survives failed enablement attempts until the slot is freed, intentionally avoiding partial-allocation rollback complexity. State is protected by `slots_arch_lock`, `mmu_lock`, `slots_lock`/SRCU, notifier SRCU, and RCU list primitives.

## Dependencies and Integration Points
Depends on `linux/kvm_host.h`, RCU/SRCU hlist helpers, `mmu.h`, `mmu_internal.h`, and `page_track.h`. It integrates with memslot lifecycle, shadow/TDP MMU write protection, large-page disallow accounting, external notifier nodes from `asm/kvm_page_track.h`, TDX restrictions (`KVM_X86_TDX_VM` cannot enable external tracking), and exported GPL APIs for external modules.

## Risks
Counter overflow/underflow is guarded by `WARN_ON_ONCE`, but callers still must pair add/remove operations. Missing `mmu_lock` or slot/SRCU protection would corrupt counts or race memslot teardown. Enabling external tracking after VM creation allocates metadata for every memslot; failure leaves allocations behind intentionally, which is safe but can surprise resource accounting. Notifier callbacks run under SRCU and must not assume MMU locks.

## Test Signals
Useful tests include write-track add/remove refcount pairing, write-protection and TLB flush observation, large-page split/disallow behavior for tracked GFNs, external notifier registration/unregistration lifetime with concurrent writes, memslot removal callback delivery, failure on TDX VMs, and no-op behavior when `CONFIG_KVM_EXTERNAL_WRITE_TRACKING` is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/page_track.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/page_track.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/page_track.h

## Purpose
Declares the KVM x86 page-tracking interface used by MMU code and optional external write-tracking users. It also provides disabled-configuration stubs so callers can keep simple control flow when `CONFIG_KVM_EXTERNAL_WRITE_TRACKING` is absent.

## Important APIs, Types, and Functions
- Declares memslot tracking allocation/free APIs and internal add/remove/query helpers.
- Under `CONFIG_KVM_EXTERNAL_WRITE_TRACKING`, declares VM init/cleanup, external write callback dispatch, and memslot delete notification.
- `kvm_page_track_has_external_user()` tests the notifier hlist.
- `kvm_page_track_write()` is the key inline integration point: it calls `__kvm_page_track_write()` for external users and always calls `kvm_mmu_track_write()` for internal shadow-MMU tracking.

## Control Flow
The header separates external-notifier support from core write tracking. When external tracking is disabled, `kvm_page_track_init()`, cleanup, write notification, deletion notification, and external-user detection compile to no-ops, while internal MMU write tracking through `kvm_page_track_write()` remains active.

## State and Persistence
No direct state is stored in the header, but it exposes `struct kvm_memory_slot` tracking storage and the VM notifier head used by `page_track.c`. The inline wrapper persists the contract that every tracked write reaches internal MMU logic regardless of external configuration.

## Dependencies and Integration Points
Includes `linux/kvm_host.h` and `asm/kvm_page_track.h`. Integrates with x86 MMU write emulation, memslot setup/teardown, and external notifier node definitions.

## Risks
The split between external tracking and always-on internal tracking means callers must use the wrapper `kvm_page_track_write()` rather than directly calling only the external hook. The disabled stubs intentionally hide external callbacks, so tests must cover both build configurations.

## Test Signals
Build coverage with and without `CONFIG_KVM_EXTERNAL_WRITE_TRACKING`, write-emulation paths invoking internal `kvm_mmu_track_write()`, notifier presence detection, and static analysis that memslot allocation/free declarations match implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/page_track.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/paging_tmpl.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/paging_tmpl.h

## Purpose
Macro template for KVM's non-TDP guest page-table walker and shadow paging fault path. It is compiled for 64-bit paging, 32-bit paging, and nested EPT by varying `PTTYPE`, generating mode-specific `paging64_*`, `paging32_*`, and `ept_*` functions over common logic.

## Important APIs, Types, and Functions
- Defines per-mode `pt_element_t`, `guest_walker*`, `FNAME()`, level geometry, A/D semantics, and PSE36 handling.
- `struct guest_walker` records guest PTEs, PTE GPAs/HVAs, table GFNs, permissions, prefetched PTEs, resulting GFN, and pending exception.
- `FNAME(walk_addr_generic)()` emulates hardware page-table walking and produces a translated GPA or page fault state.
- `FNAME(update_accessed_dirty_bits)()` atomically sets guest A/D bits when the mode supports them.
- `FNAME(fetch)()` installs shadow page tables and final SPTEs for a resolved fault.
- `FNAME(page_fault)()` is the generated page-fault entry for shadow paging.
- `FNAME(gva_to_gpa)()` translates GVA or nested L2 GPA to GPA without installing SPTEs.
- `FNAME(sync_spte)()` resynchronizes a shadow SPTE from a changed guest PTE.

## Control Flow
`walk_addr_generic()` begins from guest CR3/EPTP or PAE PDPTRs, translates guest page-table GPAs through the nested MMU when needed, reads guest PTEs through userspace HVAs, validates present/reserved bits, folds NX and permission bits into `ACC_*`, handles PKEY checks, computes the target real GPA, and updates guest A/D bits with cmpxchg. `page_fault()` injects a guest page fault on failed walks; otherwise it fills `struct kvm_page_fault`, handles page-track write faults, faults in the host PFN, adjusts CR0.WP semantics for supervisor writes, takes `mmu_lock`, checks stale faults, tops up MMU caches, and calls `fetch()`. `fetch()` verifies guest PTEs did not change, allocates/links indirect shadow pages, adjusts hugepage size, installs direct child pages as needed, sets the final SPTE via `mmu_set_spte()`, and opportunistically prefetches sibling PTEs.

## State and Persistence
Persistent state lives in shadow pages, shadowed translation metadata, guest A/D bits, dirty markers, and MMU page caches. The walker itself is temporary per fault, but it stores enough snapshots to detect races between the initial walk and SPTE installation. Synchronization uses guest PTE atomic cmpxchg, `mmu_lock`, memslot dirty marking, shadow-page unsync state, and retry returns.

## Dependencies and Integration Points
Depends on mode constants from x86 paging headers, `spte.h` helpers, MMU internals such as `kvm_mmu_get_child_sp()`, `link_shadow_page()`, `mmu_set_spte()`, `mmu_sync_children()`, `page_fault_handle_page_track()`, `kvm_mmu_faultin_pfn()`, and nested translation via `kvm_translate_gpa()`. It integrates with tracepoints, PKEY/SMEP/NX/CR0.WP logic, EPT violation qualification construction, dirty logging, MMIO SPTE sync, and prefetch.

## Risks
This file is highly race-sensitive. Guest PTEs can change after the walk, page tables may be write-protected or unsynced, and retries must avoid installing stale translations. A/D updates on read-only or MMIO-backed page tables are intentionally skipped or retried; incorrect behavior can break guest paging semantics. EPT and regular paging reuse permission fields differently, especially execute-only EPT repurposing `ACC_USER_MASK` for readability. PSE36, CR0.WP, SMEP, NX, and nested fault reporting are mode-specific edge cases.

## Test Signals
Tests should cover shadow paging for 32-bit, PAE/64-bit, and nested EPT; guest page faults for not-present, permission, reserved-bit, NX, SMEP, PKEY, and EPT misconfiguration cases; A/D-bit setting and retries on cmpxchg failure; write faults to guest page tables; MMIO SPTE sync; CR0.WP=0 supervisor writes; prefetch correctness during invalidation; and shadow-page sync after guest PTE edits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/paging_tmpl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/spte.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/spte.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/spte.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/spte.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/tdp_iter.c -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/tdp_iter.c

## Purpose
Implements the pre-order iterator over TDP MMU page tables. The iterator abstracts page-table descent, side-stepping, ascent, restart-after-yield, and SPTE refresh for code that zaps, maps, ages, write-protects, or scans TDP mappings.

## Important APIs, Types, and Functions
- `tdp_iter_start()` initializes a walk from a root, minimum level, start GFN, and root GFN mask bits.
- `tdp_iter_restart()` restarts the walk at the root after yielding.
- `tdp_iter_next()` advances to the next SPTE in pre-order.
- `spte_to_child_pt()` converts a present non-leaf SPTE to the child table virtual address.
- Internal helpers `tdp_iter_refresh_sptep()`, `try_step_down()`, `try_step_side()`, and `try_step_up()` implement traversal.

## Control Flow
Initialization validates the root level, records root metadata, stores the root page table in `pt_path`, and calls restart. Each advance first restarts if the walk yielded. Otherwise it attempts to descend into a present non-leaf SPTE, then moves sideways within the current page table, and finally walks up until a sideways move is possible. If no move remains, the iterator becomes invalid.

## State and Persistence
The iterator state is transient: current `sptep`, `old_spte`, `gfn`, level, root level, minimum level, ASID, path of page-table pointers, yielded markers, and optional GFN mask bits. Persistent state is only read through RCU-safe SPTE loads.

## Dependencies and Integration Points
Depends on `mmu_internal.h`, `tdp_iter.h`, and `spte.h`. It is the traversal core for `tdp_mmu.c` macros and functions such as mapping, zapping, aging, dirty clearing, hugepage split/recovery, and lockless walks.

## Risks
The iterator deliberately rereads SPTEs before descent to avoid walking into unlinked page tables. Incorrect `gfn_bits` or rounding can break mirrored/private address-space walks. Yield/restart semantics require callers to skip the current loop body after `tdp_mmu_iter_cond_resched()` sets `iter->yielded`.

## Test Signals
Validate traversal order across sparse and populated page tables, range boundaries, min-level stopping, huge leaf handling, restart-after-yield progress, root-level validation warnings, and lockless scans under concurrent SPTE changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/tdp_iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/tdp_iter.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/tdp_iter.h

## Purpose
Declares the TDP MMU iterator and low-level RCU-aware SPTE read/write helpers. It is the contract between generic TDP MMU code and the traversal implementation.

## Important APIs, Types, and Functions
- `kvm_tdp_mmu_read_spte()`, `kvm_tdp_mmu_write_spte_atomic()`, `tdp_mmu_clear_spte_bits_atomic()`, and `__kvm_tdp_mmu_write_spte()` wrap RCU dereference and atomic/plain SPTE writes.
- `kvm_tdp_mmu_spte_need_atomic_update()`, `kvm_tdp_mmu_write_spte()`, and `tdp_mmu_clear_spte_bits()` select atomic updates when volatile leaf bits can be modified outside `mmu_lock`.
- `struct tdp_iter` stores traversal state.
- `for_each_tdp_pte_min_level()`, `for_each_tdp_pte_min_level_all()`, and `for_each_tdp_pte()` provide range-walk macros.

## Control Flow
Callers begin RCU protection, initialize an iterator with one of the macros, inspect `iter.old_spte`, modify SPTEs through the write helpers, and call `tdp_iter_next()` automatically through the loop macro. Update helpers choose `xchg`/atomic fetch-and or `WRITE_ONCE` depending on whether an SPTE is a shadow-present leaf with volatile dirty/writable/access-tracking state.

## State and Persistence
The header encodes the concurrency contract for persistent TDP page tables: non-leaf page tables are RCU-protected; zapping flows must flush pending TLBs before dropping RCU protection where needed; volatile leaf bits require atomic writes to preserve CPU/fast-fault updates.

## Dependencies and Integration Points
Includes KVM host headers, `mmu.h`, and `spte.h`. Used by TDP MMU mutation, fast page fault lookup, lockless walks, aging, dirty logging, and zapping code.

## Risks
Plain writes to SPTEs that need atomic updates can lose Dirty or writable transitions. Atomic writes warn on EPT #VE-possible encodings. The returned `old_spte` from write helpers may differ from the caller's snapshot and must be used for bookkeeping.

## Test Signals
Exercise atomic versus plain write selection, dirty-bit preservation, access-tracking restoration, clear-bit behavior, RCU walk contracts, and compile/runtime checks for EPT #VE-suppression invariants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/tdp_iter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/tdp_mmu.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/tdp_mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/tdp_mmu.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/tdp_mmu.h

## Purpose
Declares the public TDP MMU interface used by KVM x86 MMU, memslot, notifier, dirty logging, fast page fault, and vendor code. It also defines root-type filters for direct versus mirrored/private roots.

## Important APIs, Types, and Functions
- Lifecycle declarations: `kvm_mmu_init_tdp_mmu()`, `kvm_mmu_uninit_tdp_mmu()`, `kvm_tdp_mmu_alloc_root()`, `kvm_tdp_mmu_get_root()`, and `kvm_tdp_mmu_put_root()`.
- `enum kvm_tdp_mmu_root_types` distinguishes invalid, direct, mirror, valid, and all roots.
- `kvm_gfn_range_filter_to_root_types()` maps memslot notifier private/shared filters to root classes.
- `tdp_mmu_get_root_for_fault()` and `tdp_mmu_get_root()` select normal or mirror root for a fault or operation.
- Declares zap, invalidate, map, unmap, age, write-protect, dirty clear, hugepage split/recovery, lockless walk, and fast-PF lookup APIs.
- `is_tdp_mmu_page()` is architecture-gated.

## Control Flow
Callers use the header to route operations by root type and address privacy. Fault handlers select the mirror root if the address is not direct; range invalidators use private/shared filters to process mirror and/or direct roots; lockless walkers must bracket with `kvm_tdp_mmu_walk_lockless_begin/end()`.

## State and Persistence
The header exposes root references via refcount increment/decrement and relies on implementation-managed RCU lifetime. No state is stored here, but the APIs define which operations require persistent root references and which can use current vCPU root pointers.

## Dependencies and Integration Points
Includes `linux/kvm_host.h` and `spte.h`. Integrated by x86 MMU core, memslot/MMU notifier code, dirty logging, fast page fault, TDX/private memory handling, and vendor modules.

## Risks
Misclassifying root filters can skip private or shared mappings, leaving stale translations. Lockless walk callers must obey the RCU lifetime contract and not use returned SPTE pointers after `walk_lockless_end`. Root references from `tdp_mmu_get_root_for_fault()` are raw page metadata pointers and depend on vCPU-held root lifetime.

## Test Signals
Exercise direct versus mirror root selection, GFN range filter mapping, lockless walk bracketing, root refcount get/put, invalidated-root processing, and build coverage on non-64-bit configurations where TDP pages are always false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/tdp_mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mtrr.c -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/mtrr.c

## Purpose
Implements virtual MTRR MSR get/set handling for KVM x86. It stores guest MTRR state in `vcpu->arch.mtrr_state` and validates guest writes against architectural type and reserved-bit rules.

## Important APIs, Types, and Functions
- `find_mtrr()` maps an MSR number to the correct field in the vCPU MTRR state.
- `valid_mtrr_type()` accepts architectural memory types 0, 1, 4, 5, and 6.
- `kvm_mtrr_valid()` validates default, fixed, and variable MTRR MSR payloads.
- `kvm_mtrr_set_msr()` validates and stores a writable MTRR MSR.
- `kvm_mtrr_get_msr()` returns `MSR_MTRRcap` or stored MTRR state.

## Control Flow
Set handling resolves the target MSR, rejects unknown MSRs, validates type fields and reserved physical address bits, then writes the value into per-vCPU state. Get handling synthesizes `MSR_MTRRcap` with fixed MTRRs, WC, and `KVM_NR_VAR_MTRR`, or returns the stored field for recognized writable MSRs.

## State and Persistence
State persists in `vcpu->arch.mtrr_state`: variable MTRR array, fixed 64K/16K/4K fields, and default type. The implementation does not itself recompute SPTE memory types; other MMU/vendor code consumes MTRR/PAT state when building mappings.

## Dependencies and Integration Points
Uses `asm/mtrr.h`, `cpuid.h`, and `x86.h`. Integrates with KVM MSR dispatch, CPUID physical-address restrictions via `kvm_vcpu_reserved_gpa_bits_raw()`, and memory-type logic in vendor MMU code.

## Risks
Reserved-bit validation depends on the vCPU GPA width. Incorrect fixed-range indexing or type validation can let guests program impossible MTRRs. The code returns `1` for guest-visible MSR errors, matching KVM's MSR convention rather than Linux errno.

## Test Signals
MSR tests for all fixed MTRRs, variable base/mask pairs, default type reserved bits, invalid memory types, GPA-width reserved bits, `MSR_MTRRcap` synthesis, and migration/save-restore preserving `mtrr_state`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mtrr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/pmu.c -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/pmu.c

## Purpose
Implements common x86 virtual PMU support for KVM across Intel and AMD backends. It manages host/KVM PMU capabilities, perf-backed virtual counters, mediated PMU pass-through, PMIs, event filtering, RDPMC, global control/status MSRs, emulated instruction/branch events, cleanup, and guest PMU load/put.

## Important APIs, Types, and Functions
- Global capability state: `kvm_host_pmu`, exported `kvm_pmu_cap`, and emulated event selectors.
- `kvm_pmu_ops_update()` wires vendor PMU ops into static calls.
- `kvm_init_pmu_capability()` derives KVM-exposed PMU caps from host perf caps and module policy.
- Perf event lifecycle: `pmc_reprogram_counter()`, `pmc_pause_counter()`, `pmc_resume_counter()`, `pmc_release_perf_event()`, `pmc_stop_counter()`, and `pmc_write_counter()`.
- Event filtering: filter validation/conversion/sorting, `pmc_is_event_allowed()`, and `kvm_vm_ioctl_set_pmu_event_filter()`.
- Runtime handling: `kvm_pmu_handle_event()`, `kvm_pmu_rdpmc()`, `kvm_pmu_get_msr()`, `kvm_pmu_set_msr()`, `kvm_pmu_refresh()`, `kvm_pmu_init()`, `kvm_pmu_cleanup()`, `kvm_pmu_destroy()`.
- Emulated events: `kvm_pmu_instruction_retired()` and `kvm_pmu_branch_retired()`.
- Mediated PMU: `kvm_handle_guest_mediated_pmi()`, `kvm_mediated_pmu_load()`, and `kvm_mediated_pmu_put()`.

## Control Flow
Initialization reads perf PMU capabilities unless PMU is disabled or the host is hybrid, clamps capability exposure, records raw event encodings, and disables mediated PMU if unsupported. Guest writes to PMU MSRs update common state or delegate to vendor ops, then request counter reprogramming. `kvm_pmu_handle_event()` consumes the reprogram bitmap, reprograms or resumes perf events, performs cleanup, and refreshes emulation bitmaps. Perf overflows set PMU global status and request PMI/PMU handling. RDPMC validates PMU presence, VMware pseudo-PMCs, backend PMC lookup, CR4.PCE/CPL permissions, then reads the virtual counter. Event filters are copied from userspace, validated, converted to masked filters if needed, sorted into include/exclude ranges, installed with RCU, and all vCPUs are forced to reprogram.

## State and Persistence
Per-vCPU PMU state includes GP/fixed PMCs, counters, `eventsel`, `eventsel_hw`, `fixed_ctr_ctrl`, `global_ctrl`, `global_status`, reserved masks, PEBS masks, reprogram bitmaps, in-use bitmaps, emulated event bitmaps, and perf-event pointers. VM-wide filter state persists in `kvm->arch.pmu_event_filter` under RCU/SRCU. Mediated PMU state is loaded into hardware on vCPU entry and read back on exit.

## Dependencies and Integration Points
Depends on Linux perf events, bsearch/sort, CPU model matching, LAPIC delivery, KVM static-call vendor ops, CPUID/feature state, module params such as `enable_pmu`, `enable_mediated_pmu`, and `enable_vmware_backdoor`, and userspace ioctls for PMU filtering. Integrates with KVM requests (`KVM_REQ_PMU`, `KVM_REQ_PMI`), APIC LVTPC, perf guest context APIs, MSR dispatch, emulator instruction accounting, and vendor Intel/AMD PMU implementations.

## Risks
Counter and overflow handling is race-prone: asynchronous perf overflow can race reprogramming, and emulated counts must not be lost when guests write counters. Event filters use RCU and must reprogram all vCPUs to avoid stale allow/deny decisions. Mediated PMU directly touches hardware PMCs and global control; load/put ordering with perf guest context and LAPIC state is critical. Hybrid PMUs are disabled because capability reporting is insufficient. PEBS precise levels are CPU-model sensitive.

## Test Signals
Tests should cover capability initialization on Intel/AMD/no-PMU/hybrid hosts, RDPMC privilege and VMware backdoor paths, guest MSR read/write semantics, perf event creation failure recovery, PMI delivery, PEBS overflow status, event filter allow/deny/masked/exclude behavior, reprogram bitmap races, vCPU cleanup of unused counters, emulated instruction/branch counting, mediated PMU load/put, and migration of PMU state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/pmu.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/pmu.h

## Purpose
Defines common PMU helpers, vendor operation table, counter indexing conventions, inline counter read/enabled logic, and public common PMU APIs for KVM x86.

## Important APIs, Types, and Functions
- `struct kvm_pmu_ops` abstracts vendor differences for PMC lookup, MSR handling, refresh/init/reset, PMI delivery, mediated PMU hooks, and register layout constants.
- Index helpers map vCPU/PMU/PMC relationships and fixed counter fields.
- `kvm_pmu_has_perf_global_ctrl()` determines v2+ global-control exposure.
- `kvm_vcpu_has_mediated_pmu()` gates mediated PMU usage.
- `kvm_pmc_idx_to_pmc()` and `kvm_for_each_pmc()` iterate common GP/fixed counter bitmaps.
- `pmc_read_counter()`, `pmc_bitmask()`, `pmc_is_gp()`, `pmc_is_fixed()`, `pmc_is_locally_enabled()`, `pmc_is_globally_enabled()`, and `kvm_pmu_is_fastpath_emulation_allowed()` provide shared inline state checks.
- Declares common PMU lifecycle, MSR, RDPMC, filtering, emulated event, mediated PMU, and intercept-decision functions.

## Control Flow
Backend modules provide a `kvm_pmu_ops` table, common code updates static calls, and generic PMU paths use inline helpers to select counters, test local/global enablement, request reprogramming, and decide if hardware intercepts can be disabled. `pmc_read_counter()` reads from mediated state directly or combines stored offset, emulated count, and perf event count for perf-backed PMUs.

## State and Persistence
The header defines interpretation of persistent per-vCPU `struct kvm_pmu` and `struct kvm_pmc` state: bitmaps use indices 0-31 for GP counters and 32+ for fixed counters, counters are masked by type bit width, reprogram requests persist in bitmaps, and mediated PMU state is distinguished from perf-backed emulation.

## Dependencies and Integration Points
Includes `linux/nospec.h` for speculation-safe array indexing and `asm/kvm_host.h` for PMU structs. Integrated by Intel/AMD PMU backends, common PMU code, MSR dispatch, RDPMC intercept policy, emulator instruction accounting, perf-backed counters, and mediated PMU vendor code.

## Risks
Counter-index conventions are subtle: internal fixed counters use index 32+, while guest RDPMC uses bit 30 encoding. Misusing `kvm_pmc_idx_to_pmc()` for raw guest ECX would be wrong. Fastpath emulation decisions must account for mediated PMU hardware counting to avoid double-counting. Vendor ops are required for most paths; missing static-call functions trigger WARNs.

## Test Signals
Build tests for Intel and AMD ops, fixed/GP counter mapping, RDPMC guest index conversion in backends, global-control gating by PMU version, mediated PMU enablement, fastpath emulation disablement when hardware counts instructions, and speculation-safe PMC MSR lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/reverse_cpuid.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/reverse_cpuid.h

## Purpose
Maps Linux/KVM `X86_FEATURE_*` feature numbers back to CPUID leaf/index/register/bit locations for KVM guest CPUID construction and feature manipulation. It also defines KVM-only feature numbers for hardware CPUID bits not represented directly in generic cpufeatures words.

## Important APIs, Types, and Functions
- `KVM_X86_FEATURE(w, f)` encodes feature word and bit.
- Defines KVM-only or KVM-aligned feature numbers for SGX, AVX/AMX/AVX10 subleaves, speculation-control bits, constant TSC, AMD PerfMonV2, TSA bits, and MSR immediate.
- `struct cpuid_reg` describes a CPUID function, subleaf index, and output register.
- `reverse_cpuid[]` is the lookup table indexed by CPUID word.
- `reverse_cpuid_check()` compile-time validates that a feature word is hardware-defined and present in the table.
- `__feature_translate()` maps scattered kernel feature values into KVM feature words.
- `__feature_leaf()`, `__feature_bit()`, `feature_bit()`, `x86_feature_cpuid()`, and `cpuid_entry_*()` helpers get, set, clear, or change bits in `struct kvm_cpuid_entry2`.

## Control Flow
Callers pass an `X86_FEATURE_*` value. Translation normalizes scattered features, leaf/bit helpers validate the CPUID word at compile time, lookup the CPUID register tuple, and then operate on the matching field in a `kvm_cpuid_entry2`. `cpuid_entry_change()` open-codes set/clear to allow branchless code generation when possible.

## State and Persistence
No runtime mutable state exists. The persistent contract is the static mapping table and feature-number definitions, which must remain aligned with `NR_CPUID_WORDS`, `NCAPINTS`, and KVM's CPUID word enum.

## Dependencies and Integration Points
Includes UAPI KVM CPUID structs and Linux x86 cpufeature headers. Integrated by KVM CPUID filtering, feature exposure, vendor capability code, and guest CPUID manipulation helpers.

## Risks
Adding a scattered or KVM-only feature without updating translation or `reverse_cpuid[]` can make KVM manipulate the wrong guest CPUID bit. `reverse_cpuid_check()` intentionally rejects Linux-defined software feature words. Alias features need careful handling so user-visible CPUID leaves remain correct.

## Test Signals
Compile-time build coverage after adding CPUID words, unit-style tests for `cpuid_entry_set/clear/change/has`, guest CPUID exposure tests for new features, and negative build assertions for Linux-only feature words.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/reverse_cpuid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/smm.c -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/smm.c

## Purpose
Implements KVM x86 System Management Mode entry, exit via RSM, SMRAM state-save/load, SMI request processing, SMM hflag transitions, and compile-time validation of emulated SMRAM layouts.

## Important APIs, Types, and Functions
- `check_smram_offsets()` asserts 32-bit and 64-bit SMRAM field offsets and union size.
- `kvm_smm_changed()` toggles SMM hflags, resets MMU context, clears nested NMI/SMM state on exit, and requests event processing.
- `process_smi()` latches pending SMI and requests event handling.
- Save helpers: `enter_smm_save_seg_32()`, `enter_smm_save_seg_64()`, `enter_smm_save_state_32()`, and `enter_smm_save_state_64()`.
- `enter_smm()` writes SMRAM, invokes vendor entry, masks NMI, switches to SMM real-mode-like state, resets control registers/segments, and clears EFER for long-mode guests.
- Load helpers: `rsm_load_seg_32()`, `rsm_load_seg_64()`, `rsm_enter_protected_mode()`, `rsm_load_state_32()`, and `rsm_load_state_64()`.
- `emulator_leave_smm()` implements RSM by reading SMRAM, leaving SMM/vendor state, restoring control/segment/register state, and handling nested-mode failure cases.

## Control Flow
An SMI is latched with `process_smi()`. On entry, KVM builds a zeroed 512-byte SMRAM image, saves 32-bit or 64-bit state, gives vendor code a chance to leave guest mode or adjust state, marks SMM active, writes SMRAM at `smbase + 0xfe00`, handles NMI mask state, sets SMM entry RIP/rflags/interrupt shadow/control registers/IDT/DR7/segments, clears EFER for long-mode guests, marks dynamic CPUID bits dirty, and resets MMU context. RSM reads SMRAM, unmasks NMI if appropriate, clears SMM hflags, transitions to a safe real-mode state to load CR0/CR3/CR4/EFER, invokes vendor `leave_smm`, restores 32-bit or 64-bit saved state, and forces nested guest exit if failed restoration would otherwise deliver shutdown to the wrong level.

## State and Persistence
Persistent state includes `vcpu->arch.hflags` SMM bits, `smbase`, `smi_pending`, interrupt shadow, NMI mask state, saved guest state in guest SMRAM memory, control registers, EFER, DR6/DR7, segment descriptors, descriptor tables, GPRs, optional shadow stack pointer, and MMU context. State is externally visible through guest memory at SMRAM save area and through vCPU architecture state.

## Dependencies and Integration Points
Uses KVM x86 vendor hooks (`enter_smm`, `leave_smm`, control register setters, descriptor table accessors, interrupt/NMI mask operations, EFER writes), emulator context, register cache helpers, CPUID capabilities, nested virtualization helpers, tracepoints, MMU context reset, and optional CET shadow stack MSR storage.

## Risks
SMM transitions are architecturally delicate. Wrong SMRAM layout corrupts guest restore; compile-time offset checks mitigate this. Control register ordering for PCID, PAE, long mode, and EFER.LMA must be preserved. Failure during entry kills the VM because state may be undefined. Nested virtualization RSM ordering is acknowledged as flawed and has explicit cleanup if restoration fails in guest mode. Guest SMRAM memory read/write failures make RSM unhandleable.

## Test Signals
Tests should cover SMI injection and pending-event delivery, 32-bit and 64-bit SMRAM save/restore, long-mode entry/exit, PCID/PAE/EFER ordering, NMI masking across SMM, interrupt shadow preservation, CET SSP save/restore, nested VMX/SVM SMM transitions, bad SMRAM causing unhandleable RSM, and migration preserving `smbase` and SMM hflags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/smm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/smm.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/smm.h

## Purpose
Defines KVM's emulated SMRAM layouts and public SMM helpers. It provides exact 32-bit and 64-bit state-save structures, the 512-byte union, SMI injection helper, SMM-state predicate, and declarations for SMM transition functions.

## Important APIs, Types, and Functions
- `struct kvm_smm_seg_state_32` and `struct kvm_smram_state_32` model the Intel P6-style 32-bit SMRAM layout.
- `struct kvm_smm_seg_state_64` and `struct kvm_smram_state_64` model the AMD64-style 64-bit SMRAM layout.
- `union kvm_smram` provides a 512-byte overlay for both layouts.
- `kvm_inject_smi()` checks emulated `MSR_IA32_SMBASE` support and requests `KVM_REQ_SMI`.
- `is_smm()` tests `HF_SMM_MASK`.
- Declares `kvm_smm_changed()`, `enter_smm()`, `emulator_leave_smm()`, and `process_smi()` when SMM is enabled; provides stubs when disabled.

## Control Flow
The header lets generic KVM code inject an SMI via a request rather than immediately entering SMM. Transition work is implemented in `smm.c`. When `CONFIG_KVM_SMM` is disabled, SMI injection returns `-ENOTTY` and `is_smm()` is false, while `emulator_leave_smm` is supplied elsewhere as a stub because it is used as a function pointer.

## State and Persistence
SMRAM structures define the persistent guest-visible save area for RSM. Fields include segment state, descriptor tables, GPRs, RIP/RFLAGS, CR0/3/4, DR6/7, EFER, SMBE/SMM revision, interrupt shadow, NMI-mask-related AMD field, SVM guest fields, and optional shadow stack pointer.

## Dependencies and Integration Points
Includes build-bug support and depends on KVM host/vendor calls for SMBASE support and request delivery. Integrated by x86 event injection, emulator RSM handling, vCPU hflag tests, migration/state save, and `smm.c` layout assertions.

## Risks
Packed layout and field ordering are architectural ABI. Any change must preserve exact offsets checked in `smm.c`. The helper `kvm_inject_smi()` depends on vendor support for `MSR_IA32_SMBASE`; unsupported VMs get `-ENOTTY`.

## Test Signals
Build with and without `CONFIG_KVM_SMM`, compile-time SMRAM size/offset assertions, SMI injection support detection, hflag state tests, migration of SMRAM-relevant state, and emulator RSM function-pointer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/smm.h -->
