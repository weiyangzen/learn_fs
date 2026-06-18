# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/pgtable.c

## Purpose
This file implements the standalone ARM64 KVM page-table engine used by hyp stage-1 mappings and guest stage-2 mappings. It provides a generic page-table walker, hyp mapping/unmapping helpers, VTCR construction, stage-2 map/unmap/attribute/age/flush/split logic, and destruction helpers. It is a core correctness boundary for guest isolation, hyp mappings, break-before-make ordering, cache maintenance, and TLB invalidation.

## Important APIs, Types, and Functions
- `struct kvm_pgtable_walk_data` carries walker state: current address, start/end range, and callback wrapper.
- `kvm_pgtable_walk()` and `kvm_pgtable_get_leaf()` are the generic traversal interfaces for all later operations.
- Hyp stage-1 APIs include `kvm_pgtable_hyp_init()`, `kvm_pgtable_hyp_map()`, `kvm_pgtable_hyp_unmap()`, `kvm_pgtable_hyp_destroy()`, and `kvm_pgtable_hyp_pte_prot()`.
- Stage-2 APIs include `kvm_get_vtcr()`, `kvm_pgtable_stage2_map()`, `kvm_pgtable_stage2_annotate()`, `kvm_pgtable_stage2_unmap()`, `kvm_pgtable_stage2_wrprotect()`, `kvm_pgtable_stage2_mkyoung()`, `kvm_pgtable_stage2_test_clear_young()`, `kvm_pgtable_stage2_relax_perms()`, `kvm_pgtable_stage2_flush()`, `kvm_pgtable_stage2_split()`, `kvm_pgtable_stage2_create_unlinked()`, `__kvm_pgtable_stage2_init()`, and stage-2 destroy/free helpers.
- The file relies on `struct kvm_pgtable_mm_ops` for allocation, refcounting, address conversion, cache maintenance, and deferred freeing.

## Control Flow
The generic walker aligns ranges to pages, descends from the PGD start level, and invokes callbacks for leaf, table pre-order, and table post-order visits. Callbacks may replace PTEs and request retries through `-EAGAIN`; callers outside fault handling can use `KVM_PGTABLE_WALK_IGNORE_EAGAIN`.

Hyp mapping builds leaf entries when block/page alignment allows it, allocates child tables otherwise, and stores new entries with release ordering. Hyp unmapping clears leaves and empty tables, performs stage-1 TLBI, syncs, and drops refcounts.

Stage-2 mapping first computes memory attributes and access/execute permissions, tries to install a leaf, and if needed breaks an existing PTE, performs cache/instruction maintenance, then makes the new PTE visible. Table pre-order callbacks allow replacing a table with a block mapping and freeing the detached table. Leaf callbacks allocate tables when the requested mapping cannot be represented at the current level.

Stage-2 unmap clears valid or counted invalid entries, optionally defers TLBI range invalidation, performs dcache maintenance when FWB is absent, and recursively frees empty tables. Attribute walkers update write protection, access flags, executable permissions, and access-age state without rebuilding the tree when possible. Split walkers replace block mappings with prepopulated lower-level tables from a memory cache.

## State and Persistence
Persistent state is the content of page-table pages plus refcounts held on containing table pages. Stage-2 can represent invalid but counted PTEs for nonzero ownership annotations and temporary locked PTEs for concurrent walkers. The code uses `smp_store_release()`, `READ_ONCE()`, `WRITE_ONCE()`, `cmpxchg()`, DSB/ISB barriers, and explicit TLB invalidation to preserve architectural ordering. The page table's `ia_bits`, `start_level`, `flags`, `mmu`, and optional `force_pte_cb` configure behavior for the lifetime of the table.

## Dependencies and Integration Points
This file depends on ARM64 page-table format macros from `asm/kvm_pgtable.h` and `asm/stage2_pgtable.h`, CPU feature checks such as LPA2, XNX, FWB, HAFDBS, BTI, and TLB range support, and hyp-call TLB helpers such as `__kvm_tlb_flush_vmid_ipa`. It is consumed heavily by `arch/arm64/kvm/mmu.c`, pKVM variants via `KVM_PGT_FN()`, nested virtualization shadow stage-2 code, dirty logging, memory-notifier aging, and hyp mapping setup.

## Risks and Edge Cases
The main risks are stale TLB entries after permission or table replacement, incorrect cache maintenance for noncoherent or non-FWB systems, refcount leaks on partial failures, races in shared walks, and block mappings that cover too much memory. The code mitigates these with locked invalid PTEs, break-before-make sequencing, `-EAGAIN` retry semantics, deferred table freeing through callbacks supplied by the caller, alignment checks, and explicit warnings on impossible levels or invalid permissions. Stage-2 permission relaxation preserves software bits carefully, while full remaps drop and reconstruct entries.

## Test Signals
Useful signals include KVM selftests that stress dirty logging, access-flag aging, hugepage split/collapse, memory slot moves/deletes, MTE guest memory, nested stage-2 translation, pKVM protected guests, and concurrent vCPU faults. Kernel test runs should also monitor lockdep, RCU warnings, KASAN/KCSAN, refcount underflow, TLB shootdown failures, and guest memory corruption under heavy MMU notifier churn.
