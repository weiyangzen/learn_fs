<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/tlb.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/tlb.h

Purpose: Adapts generic Linux TLB gather/mmu_gather behavior to RISC-V.

Important APIs/types/functions: Defines `tlb_flush()` integration and includes generic TLB helpers with RISC-V flush hooks.

Control flow: During unmap/free, generic MM gathers ranges and calls RISC-V flush functions before freeing page tables.

State and persistence: State is transient `mmu_gather` range/batch state.

Dependencies and integration points: Used by memory unmap, page-table freeing, THP split/collapse, and `tlbflush.h` implementations.

Risks: Incorrect batching can free page tables before remote CPUs stop using stale translations.

Test signals: munmap/mprotect stress, THP split, swap reclaim, SMP TLB shootdown, and mmu_gather debug.

Source read size: 27 lines, 582 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/tlb.h -->
