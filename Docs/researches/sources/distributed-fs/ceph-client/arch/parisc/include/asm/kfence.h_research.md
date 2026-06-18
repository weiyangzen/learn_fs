# sources/distributed-fs/ceph-client/arch/parisc/include/asm/kfence.h

Purpose: supplies PA-RISC KFENCE integration, especially page protection/cache behavior for guarded allocations.

Important APIs/types/functions: defines architecture hooks for KFENCE pool setup and PTE protection changes.

Control flow: KFENCE allocates guarded pages and uses PA-RISC page-table operations to protect/unprotect guard regions around sampled allocations.

State and persistence: guard-page PTE state persists while KFENCE objects are active. Dependencies and integration: uses pgtable/cacheflush behavior and generic KFENCE.

Risks and test signals: missing TLB/cache flushes can let invalid accesses pass or fault incorrectly. Test with KFENCE selftests, sampled allocation faults, and SMP TLB shootdown coverage.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
