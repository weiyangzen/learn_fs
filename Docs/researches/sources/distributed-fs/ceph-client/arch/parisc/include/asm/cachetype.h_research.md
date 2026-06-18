# sources/distributed-fs/ceph-client/arch/parisc/include/asm/cachetype.h

Purpose: exposes the PA-RISC cache aliasing property to generic memory-management code.

Important APIs/types/functions: defines `cpu_dcache_is_aliasing()` as `true`.

Control flow: generic mm/cache code queries this helper to decide whether extra alias management is required for mappings and page-cache transitions.

State and persistence: no state is stored. Dependencies and integration: consumed by generic cache-management paths and architecture-neutral memory code.

Risks and test signals: reporting non-aliasing on PA-RISC would permit stale or incoherent aliases. Test through mmap alias writeback, executable mapping transitions, and cacheflush selftests.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
