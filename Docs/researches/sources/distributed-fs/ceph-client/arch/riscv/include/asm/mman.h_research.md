<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/mman.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/mman.h

## Purpose
Maps RISC-V mmap protection bits to generic VM flags, including tagged-address/memory-type policy hooks.

## Important APIs, Types, And Functions
functions/prototypes `arch_calc_vm_prot_bits`; macros/constants `__ASM_MMAN_H__`, `arch_calc_vm_prot_bits(prot, pkey) arch_calc_vm_prot_bits(prot, pkey)`.

## Control Flow
Runtime flow is reached through generic MM, page-table, fault, TLB, and mapping callbacks. The header supplies inline conversions and declarations that the implementation files call during context switch, map/unmap, and flush paths.

## State And Persistence
State is carried in `mm_struct`, page tables, ASIDs, fixed mappings, folios, cache/TLB state, or architecture context fields; this header defines how those state holders are interpreted.

## Dependencies And Integration Points
Direct includes are `linux/compiler.h`, `linux/types.h`, `linux/mm.h`, `uapi/asm/mman.h`. Integrates with Linux MM, page-table helpers, TLB shootdown, cache maintenance, hugetlb, KASAN/KFENCE, EFI mapping, kexec, and architecture fault handling.

## Risks And Edge Cases
Risks include stale cache/TLB state, wrong virtual/physical conversions, ASID/version reuse bugs, fixed-map overlap, hugepage PTE corruption, and ABI changes in ELF or image headers.

## Test Signals
Test signals include MM selftests, mmap/mprotect/fork/exec stress, hugetlb tests, KASAN/KFENCE boot, kexec/crashkernel boot, EFI boot, cacheflush tests, and TLB shootdown stress.

Source read size: 26 lines, 623 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/mman.h -->
