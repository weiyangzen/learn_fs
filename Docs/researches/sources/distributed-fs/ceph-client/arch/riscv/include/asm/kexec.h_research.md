<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kexec.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kexec.h

## Purpose
Declares RISC-V kexec/crash-dump image limits, relocation hooks, and crash register capture.

## Important APIs, Types, And Functions
types `pt_regs`, `kimage_arch`, `kexec_file_ops`, `purgatory_info`, `kimage`; functions/prototypes `riscv_crash_save_regs`, `crash_setup_regs`, `arch_kexec_apply_relocations_add`, `arch_kimage_file_post_load_cleanup`, `load_extra_segments`, `riscv_kexec_relocate_size`, `riscv_kexec_norelocate`, `elf_kexec_ops`, `image_kexec_ops`; macros/constants `_RISCV_KEXEC_H`, `KEXEC_SOURCE_MEMORY_LIMIT`, `KEXEC_DESTINATION_MEMORY_LIMIT`, `KEXEC_CONTROL_MEMORY_LIMIT`, `KEXEC_CONTROL_PAGE_SIZE`, `KEXEC_ARCH`, `ARCH_HAS_KIMAGE_ARCH`, `arch_kexec_apply_relocations_add`, `arch_kimage_file_post_load_cleanup`.

## Control Flow
Runtime flow is reached through generic MM, page-table, fault, TLB, and mapping callbacks. The header supplies inline conversions and declarations that the implementation files call during context switch, map/unmap, and flush paths. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is carried in `mm_struct`, page tables, ASIDs, fixed mappings, folios, cache/TLB state, or architecture context fields; this header defines how those state holders are interpreted.

## Dependencies And Integration Points
Direct includes are `asm/page.h`. Integrates with Linux MM, page-table helpers, TLB shootdown, cache maintenance, hugetlb, KASAN/KFENCE, EFI mapping, kexec, and architecture fault handling.

## Risks And Edge Cases
Risks include stale cache/TLB state, wrong virtual/physical conversions, ASID/version reuse bugs, fixed-map overlap, hugepage PTE corruption, and ABI changes in ELF or image headers.

## Test Signals
Test signals include MM selftests, mmap/mprotect/fork/exec stress, hugetlb tests, KASAN/KFENCE boot, kexec/crashkernel boot, EFI boot, cacheflush tests, and TLB shootdown stress.

Source read size: 78 lines, 2130 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kexec.h -->
