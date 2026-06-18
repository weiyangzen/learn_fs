# sources/distributed-fs/ceph-client/arch/parisc/include/asm/prefetch.h

Purpose: provides PA-RISC prefetch and prefetch-for-write hints.

Important APIs/types/functions: defines `ARCH_HAS_PREFETCH`, `prefetch()`, `ARCH_HAS_PREFETCHW`, and `prefetchw()` using PA-RISC load/prefetch-style instructions.

Control flow: generic and driver code emits hints before anticipated memory access; CPU may fetch cachelines earlier without changing program semantics.

State and persistence: no architectural state beyond cache effects. Dependencies and integration: included by processor and performance-sensitive kernel code.

Risks and test signals: hints must be safe for any valid kernel address and not fault unexpectedly. Test with build coverage and stress paths that use list/hash prefetching.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
