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
