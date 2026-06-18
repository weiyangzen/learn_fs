# sources/distributed-fs/ceph-client/arch/xtensa/mm/ioremap.c

Purpose: Provides Xtensa `ioremap_prot()` and `iounmap()` wrappers around generic ioremap while preserving fixed KIO mappings.

Important APIs, types, and functions: `ioremap_prot()`, `iounmap()`, `generic_ioremap_prot()`, `generic_iounmap()`, `XCHAL_KIO_CACHED_VADDR`, `XCHAL_KIO_BYPASS_VADDR`, and `XCHAL_KIO_SIZE`.

Control flow: `ioremap_prot()` converts physical address to PFN, warns if it is normal RAM, and delegates to generic ioremap. `iounmap()` checks whether the address lies inside Xtensa's statically mapped cached/bypass KIO windows and returns without unmapping those; other addresses go to generic unmap.

State and persistence: Creates and destroys generic vmalloc/ioremap mappings; static KIO mappings persist and are intentionally not unmapped.

Dependencies and integration: Linux I/O mapping APIs, Xtensa KIO virtual windows, page table support, and cache attributes in `asm/io.h`.

Risks: Mapping normal RAM as I/O is warned but not blocked; address arithmetic must avoid false positives in KIO range checks; callers must choose correct cache attributes.

Test signals: Device driver ioremap/iounmap, warning on RAM PFNs, repeated iounmap of KIO window, and access to cached/bypass KIO addresses after attempted unmap.
