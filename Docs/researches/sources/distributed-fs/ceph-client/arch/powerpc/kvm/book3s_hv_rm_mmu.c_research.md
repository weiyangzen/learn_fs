# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_rm_mmu.c

## Purpose

`book3s_hv_rm_mmu.c` implements real-mode and low-level hash page table MMU support for Book3S HV KVM. It services HPT hypercalls, maintains reverse mappings between guest HPTEs and memslots, performs TLB invalidation with POWER9 errata workarounds, initializes pages in real mode, and triages HPTE faults into guest reflection, retry, MMIO emulation, or virtual-mode handling.

## Important APIs, Types, And Functions

Exported functions include `kvmppc_add_revmap_chain()`, `kvmppc_update_dirty_map()`, `kvmppc_do_h_enter()`, `kvmppc_h_enter()`, `kvmppc_do_h_remove()`, `kvmppc_h_remove()`, `kvmppc_h_bulk_remove()`, `kvmppc_h_protect()`, `kvmppc_h_read()`, `kvmppc_h_clear_ref()`, `kvmppc_h_clear_mod()`, `kvmppc_rm_h_page_init()`, `kvmppc_invalidate_hpte()`, `kvmppc_clear_ref_hpte()`, `kvmppc_hv_find_lock_hpte()`, and `kvmppc_hpte_hv_fault()`.

Important local helpers are `real_vmalloc_addr()`, `global_invalidates()`, `kvmppc_set_dirty_from_hpte()`, `revmap_for_hpte()`, `remove_revmap_chain()`, `is_mmio_hpte()`, `fixup_tlbie_lpid()`, `do_tlbies()`, `kvmppc_get_hpa()`, page-zero/copy helpers, and the MMIO HPTE cache helpers. Core state lives in `kvm->arch.hpt`, `struct revmap_entry`, memslot `arch.rmap`, `vcpu->arch.mmio_cache`, and `vcpu->arch.pgfault_*`.

## Control Flow

`kvmppc_do_h_enter()` validates HPT mode, page-size encoding, storage size bits, and target HPTE slot. It locates the backing memslot, obtains a host PTE under the raw MMU lock, computes the real HPTE from host PA and guest-requested protection, marks emulated MMIO as absent with storage key 31, finds or locks an HPTEG slot, records the guest RPTE in the revmap entry, links the HPTE into the memslot rmap unless an invalidation raced, converts HPTE format on POWER9, writes the second HPTE word, then unlocks by writing the first word.

Remove/protect/read/clear hypercalls operate directly on locked HPTEs. `kvmppc_do_h_remove()` invalidates valid HPTEs, performs TLB invalidation, rereads R/C bits, removes the revmap chain, returns guest-format HPTE values, and bumps `mmio_update` for MMIO HPTEs. `kvmppc_h_bulk_remove()` batches up to four removals before issuing TLB invalidations. `kvmppc_h_protect()` updates guest-visible protection and invalidates before changing a valid HPTE. `kvmppc_h_clear_ref()` and `kvmppc_h_clear_mod()` clear R/C bits while preserving dirty logging and rmap reference state.

`kvmppc_hpte_hv_fault()` is called from real-mode HDSI/HISI handlers. It searches the HPT, optionally using the per-vcpu MMIO HPTE cache, checks whether a not-found fault should retry because the HPTE became valid, validates read/write/execute and storage-key permissions against the guest RPTE and SLB key, saves HPTE metadata for virtual-mode handling, caches MMIO HPTEs, returns `-2` when instruction fetch is needed for MMIO data emulation, returns `-1` for host handling, `0` for retry, or a modified DSISR/SRR1 value to reflect to the guest.

## State And Persistence Behavior

The HPT and revmap structures persist guest translations. `rev->guest_rpte` stores the guest's view of the HPTE low word independent of host-enforced read-only or absent bits. Memslot rmap entries store the head of HPTE reverse chains plus accumulated R/C/reference state. Dirty logging is persisted in memslot dirty bitmaps. `kvm->arch.mmio_update` invalidates cached MMIO HPTE entries when MMIO HPTEs are changed. `kvm->arch.need_tlb_flush` records CPUs that need local flushes when `tlbiel` is used instead of global `tlbie`.

## Dependencies And Integration Points

This file backs the real-mode hcall table in `book3s_hv_rmhandlers.S` and virtual-mode paths in `book3s_hv.c`. It depends on HPT helpers from `asm/book3s/64/mmu-hash.h`, KVM memslot APIs, host PTE lookup, raw MMU locks, POWER tlbie/tlbiel instructions, HPTE old/new format conversion for POWER9, and guest fault reflection code in the assembly handlers.

## Risks

Risks include real-mode access to vmalloc-backed arrays, HPTE locking races, lost R/C bits, dirty-log omissions, stale local TLB entries, MMIO cache staleness, and incorrect HPTE format conversion on POWER9. `global_invalidates()` trades global flushes for per-core flush debt only when a single vcore is running; mistakes there can leave stale translations. `kvmppc_get_hpa()` and page-init helpers run under raw locks and must not fault or sleep.

## Test Signals

Signals include HPT guests issuing `H_ENTER`, `H_REMOVE`, `H_BULK_REMOVE`, `H_PROTECT`, `H_READ`, `H_CLEAR_REF`, `H_CLEAR_MOD`, and `H_PAGE_INIT`, dirty logging with HPT mappings, MMIO through absent key-31 HPTEs, hugepage and base-page combinations, concurrent memslot invalidation, local versus global TLB invalidation, POWER9 HPTE format systems, and guest storage-key faults.
