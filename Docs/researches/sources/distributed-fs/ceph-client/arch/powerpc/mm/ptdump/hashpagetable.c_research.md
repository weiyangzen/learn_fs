# sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/hashpagetable.c

## Purpose
This file implements the Book3S64 hash page-table debugfs dump. It walks kernel virtual areas, searches native or pSeries hash page-table entries, decodes HPTE V/R flags, base and actual page sizes, RPN, and prints mappings found in the hardware hash table.

## Important APIs, Types, And Functions
Key functions include `native_find()`, `pseries_find()`, `base_hpte_find()`, `hpte_find()`, `decode_r()`, `dump_hpte_info()`, `walk_pte()`, `walk_pmd()`, `walk_pud()`, `walk_p4d()`, `walk_pagetables()`, `walk_linearmapping()`, `walk_vmemmap()`, `populate_markers()`, `ptdump_show()`, and `ptdump_init()`. It defines local `flag_info` arrays for HPTE V and R fields.

## Control Flow
`ptdump_init()` registers `kernel_hash_pagetable` only when radix is disabled. On read, `ptdump_show()` walks the linear map by `mmu_linear_psize`, kernel page tables from `KERN_VIRT_START`, and vmemmap backing entries. `hpte_find()` checks primary and secondary hash groups through `native_find()` or `pseries_find()`, decodes large-page LP/RPN fields, validates actual page size, and prints the entry. `walk_pte()` also warns when a hardware HPTE exists but the Linux PTE lacks `H_PAGE_HASHPTE`, suggesting a bolted pre-Linux mapping.

## State And Persistence
No state is modified. The output is a live view of hash table contents, memblock DRAM size, vmemmap backing list, and Linux page tables.

## Dependencies And Integration Points
It depends on hash MMU globals such as `htab_address`, `htab_hash_mask`, `mmu_psize_defs`, `mmu_kernel_ssize`, `mmu_*_psize`, pSeries `plpar_pte_read_4()`, firmware feature flags, memblock, and debugfs.

## Risks And Test Signals
Risks include wrong AVPN/hash calculation, architecture 3.0 HPTE old/new format conversion mistakes, LP decoding errors, and racing against mapping changes during debugfs reads. Test signals include hash-only Book3S64 boots, pSeries LPAR and native modes, large pages, vmemmap, bolted mappings, and no file registration under radix.
