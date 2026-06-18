# Research: subset-b-000894

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/mmu.c -->
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

SPTE mutation helpers are deliberately layered:

- `mmu_spte_set()` installs a nonpresent-to-present SPTE.
- `mmu_spte_update()` updates a present SPTE without changing PFN and reports whether a TLB flush is needed.
- `mmu_spte_clear_track_bits()` clears a leaf SPTE and updates page accounting.
- `mmu_spte_clear_no_track()` clears non-leaf or metadata SPTEs without leaf accounting.
- `mmu_spte_get_lockless()` reads SPTEs safely for lockless walks, with special split-write sequencing on 32-bit builds.

Reverse-map and page tracking APIs include `pte_list_add()`, `pte_list_remove()`, `pte_list_count()`, `gfn_to_rmap()`, `rmap_add()`, `drop_spte()`, `rmap_write_protect()`, `__rmap_clear_dirty()`, `kvm_mmu_slot_gfn_write_protect()`, `kvm_age_gfn()`, `kvm_test_age_gfn()`, and `kvm_unmap_gfn_range()`. These connect SPTEs back to memslot GFNs so KVM can write-protect, clear dirty/accessed state, age mappings, and zap ranges.

Shadow-page lifecycle functions include `kvm_mmu_find_shadow_page()`, `kvm_mmu_alloc_shadow_page()`, `kvm_mmu_get_shadow_page()`, `link_shadow_page()`, `mmu_page_zap_pte()`, `kvm_mmu_prepare_zap_page()`, `kvm_mmu_commit_zap_page()`, `kvm_mmu_zap_oldest_mmu_pages()`, and `kvm_mmu_change_mmu_pages()`. These maintain `active_mmu_pages`, hash buckets, parent links, root counts, unsync state, NX hugepage lists, and accounting counters.

Page-fault handling centers on:

- `kvm_handle_page_fault()` as the architecture entry point from VM exits.
- `kvm_mmu_page_fault()` as the common shadow/TDP dispatch and emulation decision point.
- `kvm_mmu_do_page_fault()` in `mmu_internal.h`, which constructs `struct kvm_page_fault` and calls the current MMU's `page_fault` method.
- `direct_page_fault()`, `kvm_tdp_mmu_page_fault()`, and template-generated `paging32_page_fault()`, `paging64_page_fault()`, and `ept_page_fault()`.
- `fast_page_fault()` for lockless direct-SPTE repairs.
- `kvm_mmu_faultin_pfn()` and `__kvm_mmu_faultin_pfn()` for PFN lookup through host memory, guest_memfd, async page fault setup, and mmu-notifier race checks.
- `direct_map()` and `mmu_set_spte()` for installing final mappings.

MMU context and root management APIs include `kvm_configure_mmu()`, `kvm_init_mmu()`, `kvm_init_shadow_npt_mmu()`, `kvm_init_shadow_ept_mmu()`, `kvm_mmu_reset_context()`, `kvm_mmu_load()`, `kvm_mmu_unload()`, `kvm_mmu_free_roots()`, `kvm_mmu_new_pgd()`, and `kvm_mmu_free_obsolete_roots()`.

VM/vCPU lifecycle hooks include `kvm_mmu_create()`, `kvm_mmu_destroy()`, `kvm_mmu_init_vm()`, `kvm_mmu_uninit_vm()`, `kvm_mmu_post_init_vm()`, `kvm_mmu_pre_destroy_vm()`, `kvm_mmu_x86_module_init()`, `kvm_mmu_vendor_module_init()`, and `kvm_mmu_vendor_module_exit()`.

Invalidation and memory-management entry points include `kvm_zap_gfn_range()`, `kvm_arch_flush_shadow_all()`, `kvm_arch_flush_shadow_memslot()`, `kvm_mmu_invalidate_mmio_sptes()`, `kvm_mmu_invlpg()`, `kvm_mmu_invpcid_gva()`, `kvm_mmu_slot_remove_write_access()`, `kvm_mmu_try_split_huge_pages()`, `kvm_mmu_slot_try_split_huge_pages()`, `kvm_mmu_recover_huge_pages()`, `kvm_mmu_slot_leaf_clear_dirty()`, and generic memory-attribute callbacks under `CONFIG_KVM_GENERIC_MEMORY_ATTRIBUTES`.

## Control Flow

VM setup initializes `kvm->arch.active_mmu_pages`, NX hugepage lists, split caches, TDP MMU state if enabled, and the shadow-page hash otherwise. vCPU setup initializes the per-vCPU MMU caches and root/guest MMU contexts, including PAE root pages when needed.

MMU mode selection starts in `kvm_init_mmu()`. It snapshots CR0/CR4/EFER through `vcpu_to_role_regs()`, derives `union kvm_cpu_role` in `kvm_calc_cpu_role()`, then chooses nested MMU, TDP MMU, or software shadow MMU initialization. The initialization path sets function pointers for `page_fault`, `gva_to_gpa`, `sync_spte`, `get_guest_pgd`, and exception injection, and refreshes reserved-bit, permission, PKRU, and zero-bit masks.

`kvm_mmu_load()` tops up allocation caches, allocates special roots when required, allocates direct or shadow roots, synchronizes unsync roots, loads the hardware PGD, and flushes the current TLB. Root allocation differs by mode: TDP roots can delegate to `kvm_tdp_mmu_alloc_root()`, direct non-TDP roots allocate shadow pages with direct roles, and indirect shadow roots read guest CR3/PDPTRs and shadow the guest page tables.

The primary page-fault flow is:

1. `kvm_handle_page_fault()` handles host async-PF flags and calls `kvm_mmu_page_fault()`.
2. `kvm_mmu_page_fault()` handles MMIO reserved-bit faults first, applies SW-protected private-memory flags if needed, and calls `kvm_mmu_do_page_fault()`.
3. `kvm_mmu_do_page_fault()` builds `struct kvm_page_fault`, fills fields such as access type, TDP/private status, hugepage defaults, GFN/slot for direct roots, then calls the current MMU's `page_fault` method.
4. Direct/TDP faults first try `fast_page_fault()`, then top up caches, fault in the PFN, take `mmu_lock`, reject stale faults via root and mmu-notifier sequence checks, and map through `direct_map()` or `kvm_tdp_mmu_map()`.
5. `mmu_set_spte()` installs the final SPTE or MMIO SPTE, handles replacement/unlinking of existing mappings, reverse maps new leaves, accounts page stats, and requests range TLB flushes when needed.
6. `kvm_mmu_page_fault()` converts write-protected results into emulation or retry decisions and updates vCPU fault statistics.

The fast-fault path is intentionally narrow. `fast_page_fault()` does a lockless walk, identifies a direct leaf SPTE, determines whether the fault is already spurious, and uses `try_cmpxchg64()` to restore access-tracked or MMU-writable SPTE permissions. It avoids private/shared mismatch cases and large dirty-logged pages where fast dirty accounting would miss 4 KiB granularity.

Invalidation flows preserve ordering through `mmu_lock`, `slots_lock`, mmu-notifier sequence numbers, remote TLB flushes, and vCPU requests. Range zaps call `kvm_mmu_invalidate_begin()`, add the range, zap rmaps and TDP leaves, flush if required, and end invalidation. Fast global zaps flip `mmu_valid_gen`, request all vCPUs to free obsolete roots, zap obsolete pages in batches, and then zap invalidated TDP roots.

## State And Persistence Behavior

This file keeps only in-kernel runtime state. Persistent on-disk state is not involved.

Main VM-level state lives under `kvm->arch`: `active_mmu_pages`, `mmu_page_hash`, `n_used_mmu_pages`, `n_max_mmu_pages`, `indirect_shadow_pages`, `mmu_valid_gen`, split allocation caches, possible NX hugepage lists, and the NX recovery vhost task. Memslot architecture state stores rmaps and `lpage_info` disallow/mixed flags.

Main vCPU-level state lives under `vcpu->arch`: `root_mmu`, `guest_mmu`, `nested_mmu`, current `mmu` and `walk_mmu` pointers, root cache entries, PAE/PML4/PML5 special roots, MMIO cache, async-PF token state, fault counters, and memory caches.

Shadow pages are keyed by role and GFN in `mmu_page_hash`, linked in FIFO order on `active_mmu_pages`, and may be referenced by parent-PTE lists and memslot rmaps. Root pages carry `root_count`; non-root invalid pages move to an invalid list and are freed after a remote TLB flush. TDP MMU pages use separate root/reference and RCU behavior in `tdp_mmu.c`.

Dirty/access persistence is reflected in SPTE state, memslot dirty bitmaps, PML interaction, and page dirtying through `mark_page_dirty_in_slot()` and page release helpers. Private/shared memory attributes are consulted via `kvm_mem_is_private()` and reflected in hugepage mixed tracking bits.

## Dependencies And Integration Points

Internal KVM dependencies include `mmu.h`, `mmu_internal.h`, `tdp_mmu.h`, `spte.h`, `paging_tmpl.h`, `page_track.h`, `kvm_cache_regs.h`, `x86.h`, nested VMX/SVM hooks, `kvm_x86_ops`, and the generic KVM memory-slot/MMU-notifier APIs.

Linux dependencies include module parameters, slab and page allocators, SRCU/RCU, rwlocks/spinlocks, memory-management page-table walking helpers, GUP/fault-in helpers, signals, vhost task workers, and tracepoints.

The file integrates with userspace-visible behavior through KVM_RUN page-fault exits, `KVM_EXIT_MEMORY_FAULT` preparation for private/shared mismatches, dirty logging ioctls, memory attributes, memslot changes, APIC access page handling, and prefault APIs.

Trace integration is through `mmutrace.h` and generic KVM trace events. Many paths emit tracepoints for MMU page allocation/zap/sync, SPTE changes, page faults, MMIO SPTEs, hugepage splits, and fast global zaps.

## Risks And Edge Cases

The highest-risk areas are concurrency and ordering. SPTE writes must maintain architecture-visible atomicity, especially on 32-bit hosts. Lockless walks rely on `vcpu->mode`, IRQ disabling or TDP lockless walk guards, remote TLB flush ordering, and acquire/release semantics on rmap locks.

Race handling with mmu-notifier invalidations is subtle. Fault paths snapshot `mmu_invalidate_seq`, check before and after PFN fault-in, then recheck under `mmu_lock`. Incorrect ordering can install stale SPTEs after host mappings or private/shared attributes changed.

Shadow-page unsync handling is correctness-critical. `mmu_try_to_unsync_pages()` uses barriers so that write-enabled SPTEs do not become visible before the shadow page is marked unsync; root synchronization relies on the matching read barrier in `is_unsync_root()`.

Hugepage logic has several constraints: dirty logging requires 4 KiB granularity, NX hugepage mitigation disallows executable hugepages in vulnerable configurations, guest_memfd/private memory can impose lower maximum mapping levels, and mixed memory attributes must prevent shared/private hugepage coalescing.

Nested virtualization increases risk because a direct MMU can still be walking guest/NPT/EPT structures and because L1 and L2 page-table formats can differ. Several paths explicitly avoid retry/unprotect behavior for nested guests or handle guest-mode roots separately.

Resource exhaustion is handled by cache topups, `make_mmu_pages_available()`, and oldest-page zapping, but page-fault paths may still return `-ENOMEM`, `-ENOSPC`, or retry. The comments note deliberately soft page-limit enforcement to avoid killing guests unnecessarily.

## Test Signals

Useful runtime signals include KVM selftests that cover page faults, dirty logging, access tracking, memslot updates, MMU notifier races, guest_memfd/private memory, memory attributes, nested EPT/NPT, INVLPG/INVPCID, and prefault APIs. Tracepoints from `mmutrace.h` can confirm SPTE creation, fast page fault outcomes, MMIO SPTE generation checks, shadow-page sync/unsync/zap, and hugepage splitting.

Kernel lockdep, `CONFIG_KVM_PROVE_MMU`, `KVM_BUG_ON_DATA_CORRUPTION`, and WARN paths are important validation signals for rmap integrity, root state, SPTE reserved bits, and unexpected invalid pages. Dirty logging tests should watch for lost dirty bits after hugepage splits, PML interaction, and fast write-fault repairs. Private memory tests should validate that shared/private mismatches produce memory-fault exits instead of indefinite page-fault loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/mmu_internal.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/mmu_internal.h

## Purpose

`mmu_internal.h` defines private contracts shared by x86 KVM MMU implementation files. It provides common page-table geometry macros, the core `struct kvm_mmu_page` shadow/TDP page descriptor, the normalized `struct kvm_page_fault` object passed through page-fault handlers, return codes for page-fault outcomes, and declarations for cross-file helpers used by `mmu.c`, TDP MMU code, paging templates, and SPTE code.

## Important APIs, Types, And Functions

Page-table helper macros include `__PT_BASE_ADDR_MASK`, `__PT_LEVEL_SHIFT()`, `__PT_INDEX()`, `__PT_LVL_ADDR_MASK()`, `__PT_LVL_OFFSET_MASK()`, and `__PT_ENT_PER_PAGE()`. They abstract x86 page-table indexing for both guest PTEs and shadow/host PTEs.

`INVALID_PAE_ROOT` and `IS_VALID_PAE_ROOT()` encode the special PAE root/PDPTE rule: a valid PAE root has a hardware-present bit and cannot use `INVALID_PAGE` as the invalid sentinel because that value could look present with reserved bits.

`struct kvm_mmu_page` is the central descriptor for a shadow page or TDP MMU page. It records hash/list membership, TDP status, valid generation, NX hugepage state, role, base GFN, SPTE page pointer, optional `shadowed_translation` metadata, root reference count, MMIO presence, unsync/write-flooding state or external TDX page table pointer, parent links or TDP parent pointer, unsync-child bitmap, possible NX hugepage list node, 32-bit lockless clear counter, and RCU head for 64-bit TDP freeing.

Small helpers expose role/address-space behavior: `kvm_mmu_role_as_id()`, `kvm_mmu_page_as_id()`, `is_mirror_sp()`, `kvm_mmu_alloc_external_spt()`, `kvm_gfn_root_bits()`, `kvm_mmu_page_ad_need_write_protect()`, `gfn_round_for_level()`, and `kvm_flush_remote_tlbs_gfn()`.

`struct kvm_page_fault` normalizes page-fault handling. It stores immutable inputs (`addr`, `error_code`, `prefetch`), decoded error-code bits (`exec`, `write`, `present`, `rsvd`, `user`), MMU/global flags (`is_tdp`, `is_private`, `nx_huge_page_workaround_enabled`), hugepage decision fields (`huge_page_disallowed`, `max_level`, `req_level`, `goal_level`), translated `gfn` and `slot`, PFN lookup outputs (`mmu_seq`, `pfn`, `refcounted_page`, `map_writable`), and `write_fault_to_shadow_pgtable`.

The `RET_PF_*` enum defines nonnegative outcomes for MMU page-fault helpers: continue internally, retry, emulate, write-protected, invalid, fixed, and spurious. The comment explicitly ties new enum values to tracepoint exports in `mmutrace.h`.

`kvm_mmu_do_page_fault()` is the main inline dispatcher. It builds a `struct kvm_page_fault`, precomputes direct-root GFN/slot, calls the current MMU page-fault function, handles unexpected emulation requests on private memory by preparing a memory-fault exit, propagates emulation type and mapping level to callers, and returns the `RET_PF_*` or errno result.

Declarations at the end expose hugepage and NX helpers implemented elsewhere: `kvm_mmu_max_mapping_level()`, `kvm_mmu_hugepage_adjust()`, `disallowed_hugepage_adjust()`, `track_possible_nx_huge_page()`, and `untrack_possible_nx_huge_page()`.

## Control Flow

The header is mostly declarative, but its inline `kvm_mmu_do_page_fault()` establishes the canonical control shape for page faults. A VM-exit handler eventually passes CR2/GPA and error code into this helper. The helper decodes the fault once, fills defaults for 4 KiB mapping and `KVM_PFN_ERR_FAULT`, strips direct GFN alias bits for direct roots, then dispatches to either `kvm_tdp_page_fault()` or the current MMU function pointer. A retpoline mitigation branch directly calls the TDP fault handler in the common case to avoid indirect-call overhead.

After dispatch, it enforces private-memory behavior: if a private fault asks for emulation, KVM prepares a memory-fault exit and returns `-EFAULT` because private memory cannot be MMIO-emulated in the usual way. It then annotates write faults to shadow page tables and returns the selected hugepage level to optional callers such as prefault logic.

## State And Persistence Behavior

The header defines in-memory state only. `struct kvm_mmu_page` instances are allocated and freed by MMU code and represent page-table pages, their reverse/parent relationships, and mitigation bookkeeping. `struct kvm_page_fault` is per-fault stack state and is not persisted after the fault completes, except for side effects in SPTEs, stats, dirty logs, refcounted pages, and user exits managed by implementation code.

The header also encodes which fields are expected to be accessed under specific locks: TDP scheduled-root state under `slots_lock`, TDP roots through reference counts/RCU, unsync state under MMU locking, and TDX `external_spt` as memory owned by the TDX module rather than by KVM's SPTE accessors.

## Dependencies And Integration Points

The file depends on Linux/KVM host headers, x86 KVM architecture structures, and `mmu.h`. It is consumed by `mmu.c`, `tdp_mmu.c`, paging templates, SPTE helpers, and trace headers. It integrates with memory attributes through `is_private`, guest_memfd/private fault handling, and `kvm_mmu_prepare_memory_fault_exit()`. It integrates with TDX through mirror shadow pages, direct GFN alias-bit behavior, and external secure page-table allocation.

## Risks And Edge Cases

`struct kvm_mmu_page` is cache-sensitive and heavily overloaded. Several unions reuse storage depending on page type; consumers must respect role and mode before reading fields. Confusing TDP pages, mirror pages, direct shadow pages, and indirect shadow pages can corrupt reverse maps or root accounting.

The PAE root sentinel is subtle and architecture-specific. Replacing `INVALID_PAE_ROOT` with a generic invalid HPA would create reserved-bit hardware behavior.

`kvm_mmu_do_page_fault()` assumes direct-root faults can derive `gfn` and `slot` immediately; indirect MMUs rely on template walkers to fill translation state later. Private memory handling intentionally treats unexpected emulation as fatal to avoid spinning or exposing private memory through MMIO emulation.

## Test Signals

Compilation with `CONFIG_KVM_PROVE_MMU` turns `KVM_MMU_WARN_ON()` into runtime checks; otherwise invalid expressions are compile-checked only. Tracepoint ABI should stay synchronized with `RET_PF_*` values. Tests should cover direct and indirect page-fault dispatch, private-memory faults, TDX alias-bit stripping, PAE roots, dirty-log write-protection decisions, NX hugepage tracking, and TDP/non-TDP root lifetimes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/mmu_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/mmutrace.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/mmutrace.h

## Purpose

`mmutrace.h` defines the `kvmmmu` tracepoint subsystem for x86 KVM MMU internals. It provides compact trace events for page-table walks, shadow page lifecycle, MMIO SPTE caching, fast page faults, SPTE changes, TDP MMU changes, and hugepage splitting. The file is included by `mmu.c` with `CREATE_TRACE_POINTS`, so it both declares the event formats and generates their tracepoint definitions.

## Important APIs, Types, And Functions

Shared formatting macros:

- `KVM_MMU_PAGE_FIELDS` declares common trace fields for `struct kvm_mmu_page`: valid generation, GFN, role word, root count, and unsync state.
- `KVM_MMU_PAGE_ASSIGN(sp)` copies those fields from a shadow page into a trace entry.
- `KVM_MMU_PAGE_PRINTK()` decodes `union kvm_mmu_page_role` and formats generation, GFN, level, guest PTE size, quadrant, direct flag, access bits, invalid state, NX/A-D mode, root count, and sync state.
- `kvm_mmu_trace_pferr_flags` maps page-fault error-code bits to readable flag names.

The file exports `TRACE_DEFINE_ENUM()` entries for every `RET_PF_*` value so trace consumers can decode page-fault outcomes consistently.

Trace events include:

- `kvm_mmu_pagetable_walk` and `kvm_mmu_paging_element` for guest/shadow walk progress.
- `kvm_mmu_set_accessed_bit` and `kvm_mmu_set_dirty_bit` from a shared event class for guest PTE A/D updates.
- `kvm_mmu_walker_error` for page-walk error-code reporting.
- `kvm_mmu_get_page`, `kvm_mmu_sync_page`, `kvm_mmu_unsync_page`, and `kvm_mmu_prepare_zap_page` for shadow-page allocation/reuse and lifecycle transitions.
- `mark_mmio_spte`, `handle_mmio_page_fault`, and `check_mmio_spte` for MMIO SPTE creation, use, and generation validation.
- `fast_page_fault` for lockless fast-fault repair attempts and outcomes.
- `kvm_mmu_zap_all_fast` for generation-flip global invalidation.
- `kvm_mmu_set_spte` and `kvm_mmu_spte_requested` for leaf mapping decisions.
- `kvm_tdp_mmu_spte_changed` for TDP MMU SPTE modifications.
- `kvm_mmu_split_huge_page` for hugepage split attempts and errno results.

## Control Flow

The header is passive until tracepoints are enabled by the kernel tracing framework. MMU code calls `trace_*` helpers at important transitions. The tracepoint macros snapshot event fields in `TP_fast_assign` and format them in `TP_printk`. Many event payloads intentionally store raw role words or SPTE values and decode them at print time, keeping call-site overhead low.

The final `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `#include <trace/define_trace.h>` section follows the kernel tracepoint convention and must remain outside the include guard so the trace generator can re-read the header.

## State And Persistence Behavior

Tracepoints do not own MMU state. They snapshot selected fields at the call site into the tracing ring buffer. The events can expose transient states such as an SPTE old/new pair, a shadow page becoming unsync, or a stale MMIO SPTE generation. Persistent behavior depends on the kernel tracing backend, not on this file.

## Dependencies And Integration Points

The header depends on Linux tracepoint/trace-events APIs and on x86 KVM MMU types/macros visible from its includer, including `struct kvm_mmu_page`, `struct kvm_page_fault`, `union kvm_mmu_page_role`, `RET_PF_*`, SPTE permission masks, PFERR masks, `get_mmio_spte_generation()`, `is_executable_pte()`, and `shadow_*` masks.

The event namespace is `kvmmmu`. Users can consume it through ftrace/perf/tracefs tooling to correlate MMU behavior with KVM page faults, dirty logging, memslot invalidation, and TDP MMU changes.

## Risks And Edge Cases

Tracepoint formats are a user-visible debugging ABI in practice. Renaming fields or changing enum exposure can break scripts. `KVM_MMU_PAGE_PRINTK()` decodes the role word, so it must stay synchronized with `union kvm_mmu_page_role` layout. `kvm_mmu_set_spte` computes read/execute/user display bits using global shadow masks and SPTE helpers; changes in SPTE encoding need matching trace updates.

The header assumes its includer has already included the right MMU/SPTE definitions. It should not be included as a standalone public API header.

## Test Signals

Build tests should verify trace generation with and without multiple reads of the header. Runtime tests can enable `kvmmmu:*` tracepoints while exercising page faults, MMIO, dirty logging, TDP maps, global zaps, and hugepage splits. Useful sanity checks include matching `RET_PF_*` names in `fast_page_fault`, seeing MMIO generation mismatch events after memslot updates, and confirming `kvm_mmu_split_huge_page` errno values during dirty-log eager splitting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/mmutrace.h -->
