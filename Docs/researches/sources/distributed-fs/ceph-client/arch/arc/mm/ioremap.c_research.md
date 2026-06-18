# sources/distributed-fs/ceph-client/arch/arc/mm/ioremap.c

Purpose: implements ARC I/O remapping policy.

Important APIs/functions: `ioremap()`, `ioremap_prot()`, `iounmap()`, and helper `arc_uncached_addr_space()`.

Control flow: `ioremap()` returns a direct cast for physical addresses that already live in ARC hardware uncached space; otherwise it creates a noncached generic MMU mapping. `ioremap_prot()` always goes through the MMU but forces noncached attributes while preserving caller access-control intent. `iounmap()` skips direct uncached addresses and delegates mapped addresses to `generic_iounmap()`.

State and persistence: no owned state. It reads `perip_base`/`perip_end` from cache discovery and ARCompact `ARC_UNCACHED_ADDR_SPACE`.

Dependencies and integration: integrates with generic ioremap/vmalloc mappings, cache code peripheral aperture discovery, ARC ISA distinctions, and driver I/O resource mapping.

Risks: direct-cast optimization assumes the uncached region is within 32-bit addressable space. Incorrect peripheral aperture detection can skip required MMU mappings or unmap direct addresses. `ioremap_prot()` intentionally bypasses the direct optimization for access-control use cases.

Test signals: driver MMIO mapping on ARCompact and ARCv2, peripheral aperture logs, iounmap of direct versus vmalloc mappings, and access permission tests with `ioremap_prot()`.
