<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgalloc.h

Purpose: Provides RISC-V page-table page allocation and population helpers for the Linux MMU, including PMD/PUD/P4D/PGD population, kernel mapping synchronization, and TLB-free hooks.

Important APIs/types/functions: `pmd_populate_kernel()`, `pmd_populate()`, `pud_populate()`, `p4d_populate()`, `pgd_populate()`, `p4d_populate_safe()`, `pgd_populate_safe()`, `pgd_alloc()`, `pud_free()`, `__pud_free_tlb()`, `__p4d_free_tlb()`, `__pmd_free_tlb()`, `__pte_free_tlb()`, and `sync_kernel_mappings()`.

Control flow: Population helpers convert child table virtual addresses or pages into PFNs and install entries with table protections. `pgd_alloc()` allocates a PGD, copies/synchronizes kernel mappings, and returns it to generic MM. TLB free helpers hand page-table pages to `tlb_remove_ptdesc()` only when the relevant levels are not folded.

State and persistence: State is page-table memory owned by each `mm_struct`; no persistent data is stored in the header. The important persistence behavior is keeping each process PGD synchronized with global kernel mappings.

Dependencies and integration points: Depends on Linux generic pgalloc, `asm/tlb.h`, `asm/sbi.h`, RISC-V pgtable types, folded level configuration, and mmu_gather teardown.

Risks: Wrong PFN/protection encoding, missing kernel mapping sync, or freeing a folded level would corrupt address spaces. Safe population helpers rely on callers only installing non-present or identical entries.

Test signals: Boot, fork/exec stress, vmalloc/module mapping, page-table debug, KASAN/KFENCE, THP on RV64, and TLB gather teardown tests are relevant.

Source read size: 140 lines, 3250 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgalloc.h -->
