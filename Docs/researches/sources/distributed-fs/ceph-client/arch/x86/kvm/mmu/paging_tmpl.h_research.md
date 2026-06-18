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
