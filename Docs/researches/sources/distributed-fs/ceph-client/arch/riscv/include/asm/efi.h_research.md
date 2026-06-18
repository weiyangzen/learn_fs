<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/efi.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/efi.h

## Purpose
Declares RISC-V EFI mapping, virtual-call setup, kernel-image placement, initrd limit, and icache-sync helpers.

## Important APIs, Types, And Functions
types `mm_struct`; functions/prototypes `efi_init`, `efi_create_mapping`, `efi_set_mapping_permissions`, `efi_get_max_initrd_addr`, `efi_get_kimg_min_align`, `arch_efi_call_virt_setup`, `arch_efi_call_virt_teardown`, `stext_offset`, `efi_icache_sync`; macros/constants `_ASM_EFI_H`, `efi_init()`, `ARCH_EFI_IRQ_FLAGS_MASK`, `EFI_KIMG_PREFERRED_ADDRESS`.

## Control Flow
Runtime flow is reached through generic MM, page-table, fault, TLB, and mapping callbacks. The header supplies inline conversions and declarations that the implementation files call during context switch, map/unmap, and flush paths. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is carried in `mm_struct`, page tables, ASIDs, fixed mappings, folios, cache/TLB state, or architecture context fields; this header defines how those state holders are interpreted.

## Dependencies And Integration Points
Direct includes are `asm/csr.h`, `asm/io.h`, `asm/mmu_context.h`, `asm/ptrace.h`, `asm/tlbflush.h`, `asm/pgalloc.h`. Integrates with Linux MM, page-table helpers, TLB shootdown, cache maintenance, hugetlb, KASAN/KFENCE, EFI mapping, kexec, and architecture fault handling.

## Risks And Edge Cases
Risks include stale cache/TLB state, wrong virtual/physical conversions, ASID/version reuse bugs, fixed-map overlap, hugepage PTE corruption, and ABI changes in ELF or image headers.

## Test Signals
Test signals include MM selftests, mmap/mprotect/fork/exec stress, hugetlb tests, KASAN/KFENCE boot, kexec/crashkernel boot, EFI boot, cacheflush tests, and TLB shootdown stress.

Source read size: 50 lines, 1209 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/efi.h -->
