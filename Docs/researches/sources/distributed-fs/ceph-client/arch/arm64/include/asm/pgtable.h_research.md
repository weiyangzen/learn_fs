# sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgtable.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgtable.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgtable.h` Implements the arm64 core page-table API: PTE/PMD/PUD/PGD construction, permission mutation, page-table walking, lazy MMU barriers, MTE tag/cache synchronization, swap encoding, runtime page-table level folding, and contiguous-PTE management. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
VMALLOC_START/END, emit_pte_barriers(), arch_flush_lazy_mmu_mode(), pte_* predicates and mutators, por_el0_allows_pkey(), __set_ptes_anysz(), pgprot_* modifiers, pmd/pud/p4d/pgd offset/fixmap helpers, pte_modify(), ptep_set_access_flags(), ptep_get_and_clear(), wrprotect_ptes(), swap-entry macros, update_mmu_cache_range(), contpte_* wrappers. The file is 1954 lines / 58033 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Setters write entries with WRITE_ONCE/xchg/cmpxchg, run page_table_check, synchronize I-cache/D-cache and MTE tags for user executable/tagged mappings, then queue or emit DSB/ISB barriers. Page-table walking chooses folded or real levels at runtime for LPA2/VA52. Contiguous PTE paths unfold before modifying a contig range and refold when a range becomes aligned and eligible.

### State, Persistence, And Dependencies
Owns no persistent storage but mutates page tables, TIF_LAZY_MMU_PENDING, hardware access/dirty state, MTE tag side effects, and swap/MTE metadata. Extern page directories include swapper_pg_dir, idmap_pg_dir, tramp_pg_dir, reserved_pg_dir. Depends on bug.h, proc-fns.h, memory.h, mte.h, pgtable-hwdef.h, pgtable-prot.h, tlbflush.h, cmpxchg.h, fixmap.h, por.h, mmdebug, mm_types, sched, page_table_check; integrates directly with Linux core-mm, fork/COW, mprotect, fault handling, THP, hugetlb, swap, KVM, perf page-size reporting, and Ceph indirectly through page cache and network memory correctness.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Most risks are ordering and concurrency bugs: missing DSB/ISB can leave walkers using stale entries, unsafe valid-to-valid changes can race hardware AF/DBM updates, wrong contpte unfolding can corrupt adjacent entries, and pkey/POR/MTE handling can expose or lose access rights.

### Test Signals
Run arm64 mm selftests, mprotect/userfaultfd/THP/hugetlb/swap/MTE tests, page_table_check, KASAN/KMSAN configs, fork/COW stress, LKDTM W^X, ptdump, and TLB/cache coherency stress on 4K/16K/64K and LPA2/VA52 builds.
