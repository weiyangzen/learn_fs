<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kasan.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kasan.h

## Purpose
Defines RISC-V KASAN shadow address layout and initialization hooks.

## Important APIs, Types, And Functions
functions/prototypes `kasan_init`, `kasan_early_init`, `kasan_swapper_init`; macros/constants `__ASM_KASAN_H`, `KASAN_SHADOW_SCALE_SHIFT`, `KASAN_SHADOW_SIZE`, `KASAN_SHADOW_START`, `KASAN_SHADOW_END`, `KASAN_SHADOW_OFFSET`.

## Control Flow
Runtime flow is reached through generic MM, page-table, fault, TLB, and mapping callbacks. The header supplies inline conversions and declarations that the implementation files call during context switch, map/unmap, and flush paths. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is carried in `mm_struct`, page tables, ASIDs, fixed mappings, folios, cache/TLB state, or architecture context fields; this header defines how those state holders are interpreted.

## Dependencies And Integration Points
It has no direct includes. Integrates with Linux MM, page-table helpers, TLB shootdown, cache maintenance, hugetlb, KASAN/KFENCE, EFI mapping, kexec, and architecture fault handling.

## Risks And Edge Cases
Risks include stale cache/TLB state, wrong virtual/physical conversions, ASID/version reuse bugs, fixed-map overlap, hugepage PTE corruption, and ABI changes in ELF or image headers.

## Test Signals
Test signals include MM selftests, mmap/mprotect/fork/exec stress, hugetlb tests, KASAN/KFENCE boot, kexec/crashkernel boot, EFI boot, cacheflush tests, and TLB shootdown stress.

Source read size: 45 lines, 1590 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kasan.h -->
