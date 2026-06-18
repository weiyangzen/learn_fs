# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_nested.c

## Purpose

`book3s_hv_nested.c` implements nested virtualization support for Book3S HV KVM on POWER9 and later, mainly the nested v1 path plus shared nested partition-table and shadow radix-MMU management. It lets an L1 guest run an L2 guest through `H_ENTER_NESTED`, translates L1 LPIDs into L0 shadow LPIDs, mirrors L1 partition/process table state into L0-visible partition table entries, handles nested TLB invalidation hcalls, and services nested radix page faults by installing mappings in per-nested-guest shadow page tables.

## Important APIs, Types, And Functions

Key exported or externally used entry points are `kvmhv_enter_nested_guest()`, `kvmhv_nested_init()`, `kvmhv_nested_exit()`, `kvmhv_flush_lpid()`, `kvmhv_set_ptbl_entry()`, `kvmhv_set_partition_table()`, `kvmhv_copy_tofrom_guest_nested()`, `kvmhv_vm_nested_init()`, `kvmhv_release_all_nested()`, `kvmhv_get_nested()`, `kvmhv_put_nested()`, `kvmhv_insert_nest_rmap()`, `kvmhv_update_nest_rmap_rc_list()`, `kvmhv_remove_nest_rmap_range()`, `kvmhv_do_nested_tlbie()`, `do_h_rpt_invalidate_pat()`, `kvmhv_nested_page_fault()`, and `kvmhv_nested_next_lpid()`.

Important data structures are `struct hv_guest_state` for the L2 HV register block passed by L1, `struct pt_regs` for L2 GPR/control state, `struct kvm_nested_guest` for L1 LPID to shadow LPID state, and `struct rmap_nested` for reverse mappings from host memslots back to nested shadow PTEs. The file also owns the pseries nested v1 partition table allocation through `pseries_partition_tb` and the global `nested_capabilities` negotiated with a parent hypervisor.

## Control Flow

`kvmhv_enter_nested_guest()` is the central L2 run path. It rejects missing L1 partition-table setup and transactional-mode misuse, reads `hv_guest_state` and `pt_regs` from L1 guest memory, performs endian conversion when needed, validates the state version and vcpu token, and checks that L1 and L2 transactional-state combinations are legal. It then obtains or creates a `struct kvm_nested_guest` for the L1 LPID, refreshes the cached L1 partition table entry when needed, saves L1 register/HV state, converts L2 timebase/decrementer values into host-relative values, installs L2 state into the current vcpu, filters LPCR and HFSCR, masks hypervisor DAWR/CIABR settings, and runs `kvmhv_run_single_vcpu()`. On exit it saves L2 return state, restores L1 state, accumulates PURR/SPURR/IC/VTB deltas into L1 accounting, writes the L2 state back to L1 memory, and maps MMIO completion state to nested GPR storage when needed.

Initialization has two modes. On pseries with radix enabled, `kvmhv_nested_init()` first probes `plpar_guest_get_capabilities()`. If nested v2 capability negotiation succeeds it enables the static branch `__kvmhv_is_nestedv2` and avoids the v1 partition table. Otherwise it allocates a nested v1 partition table, registers it with `H_SET_PARTITION_TABLE`, and uses `kvmhv_set_ptbl_entry()` to update pseries entries. On bare metal it writes the hardware partition table directly.

Nested guest lifecycle flows through the per-VM IDR. `kvmhv_get_nested()` validates the L1 LPID against L1's PTCR size, finds or allocates a `kvm_nested_guest`, allocates a shadow radix pgtable and shadow LPID, preallocates the IDR slot, installs with refcounts under `kvm->mmu_lock`, and releases unused races. `kvmhv_flush_nested()` frees shadow PTEs, flushes the shadow LPID, reloads L1 partition table state, and removes the nested guest if L1 no longer has a usable table entry. `kvmhv_release_all_nested()` removes all IDR entries and frees memslot nested rmaps when a VM is destroyed or switched away from radix nested mode.

The nested fault path is `kvmhv_nested_page_fault()` -> `__kvmhv_nested_page_fault()`. It refreshes L1 partition-table cache, translates the nested GPA through L1's partition-scoped radix tree with `kvmppc_mmu_walk_radix_tree()`, forwards missing/protection/table faults back to L1 when appropriate, handles DSISR_SET_RC by setting reference/change bits in both L0 and shadow page tables, locates the L1 GPA memslot, emulates MMIO when no memslot backs the target, finds or instantiates the L0 host PTE, combines L0 and L1 permissions, chooses a page size not larger than either mapping, allocates a nested rmap entry, and inserts the shadow PTE with `kvmppc_create_pte()`.

TLB invalidation comes through `kvmhv_do_nested_tlbie()` and `do_h_rpt_invalidate_pat()`. The file decodes private radix `tlbie` fields, rejects invalid encodings, invalidates individual nested addresses, one LPID, or all LPIDs, and uses whole-LPID flushes for large ranges above `tlb_range_flush_page_ceiling`.

## State And Persistence Behavior

Persistent VM state includes `kvm->arch.l1_ptcr`, the nested guest IDR, each nested guest's `l1_lpid`, `shadow_lpid`, `shadow_pgtable`, cached L1 guest-real-to-host-real root `l1_gr_to_hr`, process table, `need_tlb_flush`, and refcount. Memslot `arch.rmap` entries persist nested reverse mappings so host page invalidations and dirty/reference changes can propagate into nested shadow page tables. L2 run state is persisted by writing the updated `hv_guest_state` and `pt_regs` back into L1 memory.

The file is careful about lock domains: IDR/refcounts and shadow PTE lookup require `kvm->mmu_lock`, while per-nested-guest page-table and partition-cache operations use `gp->tlb_lock`. SRCU protects reads and writes into guest memory and memslot traversal. Shadow LPID flushing is explicit because stale nested translations can otherwise outlive L1 table changes.

## Dependencies And Integration Points

This file integrates with `book3s_hv.c` for nested fault dispatch, nested vcpu entry, LPCR/HFSCR filtering, and VM teardown; `book3s_64_mmu_radix.c` for radix PTE creation, teardown, and host PTE lookup; pseries firmware hcalls through `plpar_wrappers.h`; nested v2 helpers in `book3s_hv_nestedv2.c`; and KVM memslot/mmu notifier infrastructure through rmap and `mmu_invalidate_seq`. It also depends on POWER radix MMU helpers such as `radix__flush_all_lpid()`, `kvmppc_radix_tlbie_page()`, `__find_linux_pte()`, and `kvmppc_book3s_instantiate_page()`.

## Risks

The highest-risk areas are state filtering on L2 entry, nested rmap lifetime, stale shadow PTE invalidation, and timebase/decrementer conversion. Incorrect LPCR/HFSCR/DAWR/CIABR filtering can expose host or L1-only facilities to L2. Missing rmap cleanup can leave dangling `rmap_nested` entries in memslots; over-aggressive cleanup can lose reference/dirty propagation. The fault path must recheck `mmu_invalidate_seq` and PFN identity to avoid installing stale mappings. The nested MMIO path rewrites `io_gpr` to `KVM_MMIO_REG_NESTED_GPR`, so regressions there can corrupt L1's saved L2 register image.

## Test Signals

Useful signals include booting an L1 KVM guest that can run L2 guests with radix enabled, exercising `H_ENTER_NESTED` with big and little endian L1s, nested MMIO loads and stores, L2 migration-like state save/restore, L1 `H_SET_PARTITION_TABLE` changes, L2 page faults across 4K/PMD/PUD backed mappings, memslot deletion while nested mappings exist, `H_TLB_INVALIDATE` and `H_RPT_INVALIDATE` range/all flushes, and dirty-log/reference-bit tests that confirm updates propagate through nested rmap entries.
