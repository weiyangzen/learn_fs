# sources/distributed-fs/ceph-client/arch/parisc/include/asm/page.h

Purpose: defines PA-RISC page size, page alignment, physical/virtual conversion, page table entry base types, and memory layout constants.

Important APIs/types/functions: exports `PAGE_SHIFT`, `PAGE_SIZE`, `PAGE_MASK`, `__PAGE_OFFSET`, `PAGE_OFFSET`, `__pa`, `__va`, `virt_to_page`, `clear_page`, `copy_page`, and typedefs for PTE/PMD/PGD-related values.

Control flow: MM code uses these macros for address translation, page allocation, page-table construction, and low-level copying/clearing.

State and persistence: no private state, but constants define every process and kernel mapping. Dependencies and integration: used by boot, pgtable, cache, DMA, and virtually all mm code.

Risks and test signals: address conversion errors are catastrophic. Test with memory map validation, high-memory/64-bit builds, page allocator tests, and boot with varied RAM sizes.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
