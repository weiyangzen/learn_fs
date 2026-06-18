<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cacheflush.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/cacheflush.h

## Purpose
Declares cache and instruction-cache flush helpers, DMA-cache alignment setup, CBO support discovery, and the userspace icache-flush syscall flags.

## Important APIs, Types, And Functions
types `folio`, `page`, `mm_struct`; functions/prototypes `local_flush_icache_all`, `local_flush_icache_range`, `flush_dcache_folio`, `flush_dcache_page`, `flush_cache_vmap`, `flush_icache_all`, `flush_icache_mm`, `flush_icache_range`, `riscv_init_cbo_blocksizes`, `riscv_noncoherent_supported`, `riscv_set_dma_cache_alignment`, `sizeof`, plus 3 more; macros/constants `_ASM_RISCV_CACHEFLUSH_H`, `PG_dcache_clean`, `flush_dcache_folio`, `ARCH_IMPLEMENTS_FLUSH_DCACHE_PAGE`, `flush_icache_user_page(vma, pg, addr, len)`, `flush_cache_vmap`, `flush_cache_vmap_early(start, end) local_flush_tlb_kernel_range(start, end)`, `flush_icache_all() local_flush_icache_all()`, `flush_icache_mm(mm, local) flush_icache_all()`, `flush_icache_range`, `SYS_RISCV_FLUSH_ICACHE_LOCAL`, `SYS_RISCV_FLUSH_ICACHE_ALL`.

## Control Flow
Runtime flow is reached through generic MM, page-table, fault, TLB, and mapping callbacks. The header supplies inline conversions and declarations that the implementation files call during context switch, map/unmap, and flush paths. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is carried in `mm_struct`, page tables, ASIDs, fixed mappings, folios, cache/TLB state, or architecture context fields; this header defines how those state holders are interpreted.

## Dependencies And Integration Points
Direct includes are `linux/mm.h`, `asm-generic/cacheflush.h`. Integrates with Linux MM, page-table helpers, TLB shootdown, cache maintenance, hugetlb, KASAN/KFENCE, EFI mapping, kexec, and architecture fault handling.

## Risks And Edge Cases
Risks include stale cache/TLB state, wrong virtual/physical conversions, ASID/version reuse bugs, fixed-map overlap, hugepage PTE corruption, and ABI changes in ELF or image headers.

## Test Signals
Test signals include MM selftests, mmap/mprotect/fork/exec stress, hugetlb tests, KASAN/KFENCE boot, kexec/crashkernel boot, EFI boot, cacheflush tests, and TLB shootdown stress.

Source read size: 107 lines, 2780 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cacheflush.h -->
