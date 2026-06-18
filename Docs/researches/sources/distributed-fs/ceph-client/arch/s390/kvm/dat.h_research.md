# sources/distributed-fs/ceph-client/arch/s390/kvm/dat.h

## Purpose
Defines the s390 KVM guest dynamic-address-translation table model used by the newer gmap code. It provides typed overlays for guest page-table entries, CRST entries, page-table adjunct PGSTEs, storage keys, ASCE helpers, DAT walkers, guest-fault descriptors, vSIE reverse mappings, and a small MMU allocation cache.

## Important APIs, Types, And Functions
Core exported types are `union pte`, `union pgste`, `union pmd`, `union pud`, `union p4d`, `union pgd`, `union crste`, `union skey`, `struct crst_table`, `struct page_table`, `struct dat_walk`, `struct dat_walk_ops`, `struct kvm_s390_mmu_cache`, `struct guest_fault`, and `struct vsie_rmap`. Entry constructors include `_pte`, `_crste_fc0`, `_crste_fc1`, token constructors such as `_CRSTE_HOLE`, `_CRSTE_EMPTY`, and `_PTE_EMPTY`, and ucontrol page-table-value helpers `PTVAL_PGT_ADDR` and `PTVAL_VMADDR`.

The header declares the implementation hooks used by `gmap.c`, `gaccess.c`, and `faultin.c`: `dat_entry_walk`, `_dat_walk_gfn_range`, `dat_set_asce_limit`, `dat_set_slot`, storage-key operations, CMMA/ESSA helpers, `dat_ptep_xchg`, `dat_crstep_xchg`, `dat_crstep_xchg_atomic`, `dat_free_level`, `dat_alloc_crst_sleepable`, and `kvm_s390_mmu_cache_topup`. Inline helpers cover ASCE sizing, table dereference, CRSTE/PTE origin extraction, large-page translation, pgste locking, IDTE/CRDTE invalidation, and MMU cache allocation/free.

## Control Flow
Callers usually start with an ASCE and a guest frame number. `dat_entry_walk` locates or creates the requested table level using flags such as `DAT_WALK_ALLOC`, `DAT_WALK_SPLIT`, `DAT_WALK_LEAF`, and `DAT_WALK_USES_SKEYS`. Mutations pass through `dat_ptep_xchg` or CRSTE exchange wrappers, which update table entries while preserving s390 invalidation and optional storage-key behavior. Higher-level users allocate from `struct kvm_s390_mmu_cache` first and fall back to atomic GFP allocations only when a cache is empty.

## State And Persistence
State is in-memory KVM MMU state: guest DAT tables, PGSTEs, storage-key bits, CMMA soft state, notification flags, and cached allocations. No filesystem state is persisted. PGSTE fields such as PCL, usage, CMMA dirty, prefix notification, and vSIE notification are intentionally persistent across individual faults until later aging, unmap, dirty-log, or shadow invalidation paths consume them.

## Dependencies And Integration Points
Depends on Linux KVM core types, radix trees, refcounts, page allocation, `asm/dat-bits.h`, `asm/tlbflush.h`, and s390 low-level instructions such as `idte`, `crdte`, and `cspg`. It is the shared contract for `gmap.c` guest address spaces, `gaccess.c` guest access and vSIE shadow faults, `faultin.c` host-page fault resolution, and s390 storage-key/CMMA emulation.

## Risks And Edge Cases
Bitfield layout must match s390 hardware formats exactly. PGSTE PCL locking is spin-based and correctness-sensitive. Wrong invalidation scope can leave stale guest translations. Large-page helpers return sentinel values on non-large entries, so callers must check leaf/table type. `gmap` notification flags embedded in entries must be cleared or propagated correctly to avoid stale prefix mappings or vSIE shadows. Allocation helpers use atomic/accounted GFP flags and can fail in fault paths, requiring callers to top up caches and retry.

## Test Signals
Useful signals include s390 KVM boot tests, guest memory fault tests, storage-key tests, CMMA/ESSA tests, dirty-log and aging tests, huge-page mapping/splitting tests, ucontrol tests, vSIE nested virtualization tests, protected-virtualization teardown tests, and lockdep/KCSAN coverage for pgste and mmu-lock interactions.
