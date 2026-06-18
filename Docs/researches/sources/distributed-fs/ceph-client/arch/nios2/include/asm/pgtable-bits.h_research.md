# sources/distributed-fs/ceph-client/arch/nios2/include/asm/pgtable-bits.h

Purpose: names the Nios II hardware and software PTE bit assignments for global, execute, read, write, cache,
present, accessed, dirty, and swap-exclusive state.

Important APIs/types/functions: macros: `_ASM_NIOS2_PGTABLE_BITS_H`, `_PAGE_GLOBAL`, `_PAGE_EXEC`, `_PAGE_WRITE`, `_PAGE_READ`,
`_PAGE_CACHED`, `_PAGE_PRESENT`, `_PAGE_ACCESSED`, `_PAGE_DIRTY`, `_PAGE_SWP_EXCLUSIVE`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State includes page tables, PTE permission/cache bits, ASID or context identifiers, TLB entries,
vmalloc/ioremap mappings, swap PTE encodings, and boot-time memory reservations.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks include stale TLB/cache state, wrong access permissions, corrupted page tables, bad ASID
reuse, kernel faults without fixups, DMA coherency loss, or ABI-visible memory corruption.

Test signals: Test signals are boot under an emulator or board, page-fault and fork/exec stress, mmap/mprotect,
swap where enabled, vmalloc/ioremap users, DMA drivers, module loading, and cache/TLB debug output.
