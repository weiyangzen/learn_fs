<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/fixmap.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/fixmap.h

## Purpose
Defines RISC-V fixed virtual-address slots for early ioremap, fixmap bitmap slots, and late fixmap updates.

## Important APIs, Types, And Functions
types `fixed_addresses`; functions/prototypes `__set_fixmap`; macros/constants `_ASM_RISCV_FIXMAP_H`, `NR_FIX_BTMAPS`, `FIX_BTMAPS_SLOTS`, `TOTAL_FIX_BTMAPS`, `__early_set_fixmap`, `__late_set_fixmap`, `__late_clear_fixmap(idx) __set_fixmap((idx), 0, FIXMAP_PAGE_CLEAR)`.

## Control Flow
Runtime flow is reached through generic MM, page-table, fault, TLB, and mapping callbacks. The header supplies inline conversions and declarations that the implementation files call during context switch, map/unmap, and flush paths. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is carried in `mm_struct`, page tables, ASIDs, fixed mappings, folios, cache/TLB state, or architecture context fields; this header defines how those state holders are interpreted.

## Dependencies And Integration Points
Direct includes are `linux/kernel.h`, `linux/sizes.h`, `linux/pgtable.h`, `asm/page.h`, `asm-generic/fixmap.h`. Integrates with Linux MM, page-table helpers, TLB shootdown, cache maintenance, hugetlb, KASAN/KFENCE, EFI mapping, kexec, and architecture fault handling.

## Risks And Edge Cases
Risks include stale cache/TLB state, wrong virtual/physical conversions, ASID/version reuse bugs, fixed-map overlap, hugepage PTE corruption, and ABI changes in ELF or image headers.

## Test Signals
Test signals include MM selftests, mmap/mprotect/fork/exec stress, hugetlb tests, KASAN/KFENCE boot, kexec/crashkernel boot, EFI boot, cacheflush tests, and TLB shootdown stress.

Source read size: 67 lines, 1789 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/fixmap.h -->
