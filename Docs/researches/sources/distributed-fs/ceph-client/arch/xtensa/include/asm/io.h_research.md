<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/io.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/io.h

## Purpose
Defines Xtensa I/O address mapping constants and MMU-aware `ioremap` shortcuts for statically mapped KIO regions.

## Important APIs, Types, And Functions
Defines `IOADDR`, `IO_SPACE_LIMIT`, `PCI_IOBASE`, `ioremap_prot`, `ioremap`, and `ioremap_cache`, then includes generic I/O accessors.

## Control Flow
On MMU builds, `ioremap` and `ioremap_cache` return direct KIO bypass/cached virtual addresses when the physical address falls inside `XCHAL_KIO_PADDR..+XCHAL_KIO_SIZE`; otherwise they call `ioremap_prot` with noncached or cached protection.

## State And Persistence
State is vmalloc/ioremap mappings managed by the MM subsystem. Direct KIO translations are fixed by MMU initialization.

## Dependencies And Integration Points
Depends on byteorder, page and KIO layout, pgtable protections, generic I/O helpers, PCI, and device drivers.

## Risks And Edge Cases
KIO physical base can be device-tree derived on some configurations, so early users must see initialized `xtensa_kio_paddr`. Cached mapping of device memory is unsafe unless the caller explicitly asks for it.

## Test Signals
Probe MMIO drivers in KIO and non-KIO ranges, PCI I/O access, `ioremap_cache` users, and OF-derived KIO base configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/io.h -->
