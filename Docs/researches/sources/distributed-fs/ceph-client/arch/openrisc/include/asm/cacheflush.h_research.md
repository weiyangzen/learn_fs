# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/cacheflush.h

Purpose: declares and wraps OpenRISC D-cache/I-cache page and range flush helpers, including SMP icache
invalidation and folio dirty-cache state.

Important APIs/types/functions: functions: `sync_icache_dcache`, `flush_dcache_folio`, `flush_dcache_page`; prototypes: `Copyright`,
`dcache_page_flush`, `sync_icache_dcache`; macros: `__ASM_CACHEFLUSH_H`, `dcache_page_flush(page)`,
`icache_page_inv(page)`, `local_dcache_block_flush(addr)`, `local_dcache_block_inv(addr)`,
`local_icache_block_inv(addr)`, `PG_dc_clean`, `flush_dcache_folio`,
`ARCH_IMPLEMENTS_FLUSH_DCACHE_PAGE`, `flush_icache_user_page(vma, page, addr, len)`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State is mostly hardware cache contents, folio dirty-cache flags, DMA-visible memory coherency, and
instruction-cache visibility after code or user-page updates.

Dependencies and integration points: Dependencies include `linux/mm.h`, `asm-generic/cacheflush.h`. Integration points include generic
asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex, ELF, and
Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under the
vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are boot under an emulator or board, page-fault and fork/exec stress, mmap/mprotect,
swap where enabled, vmalloc/ioremap users, DMA drivers, module loading, and cache/TLB debug output.
