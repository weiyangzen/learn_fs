# sources/distributed-fs/ceph-client/arch/parisc/include/asm/pgalloc.h

Purpose: supplies PA-RISC page-table allocation and freeing helpers for generic memory management.

Important APIs/types/functions: defines `pgd_alloc/free`, `pmd_alloc_one/free`, `pte_alloc_one`, `pte_free`, and page-table constructor/destructor behavior based on configured page-table levels.

Control flow: mm creates page-table pages during process creation and faults, initializes them, and frees them during unmap/exit.

State and persistence: allocated page-table pages persist in process address spaces. Dependencies and integration: uses `pgtable.h`, generic page allocator, and TLB/cache flushing.

Risks and test signals: wrong allocation order or missing initialization corrupts page walks. Test with fork/exit stress, mmap/munmap, page-table debug, and 2-level/3-level builds.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
