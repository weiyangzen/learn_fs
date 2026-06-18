<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/kmap.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/kmap.h

## Purpose
`kmap.h` exposes m68k I/O remapping and port mapping helpers, primarily for MMU-enabled systems.

## Important APIs, Types, and Functions
It defines cache modes `IOMAP_FULL_CACHING`, `IOMAP_NOCACHE_SER`, `IOMAP_NOCACHE_NONSER`, and `IOMAP_WRITETHROUGH`. MMU builds declare `__ioremap()` and `iounmap()`, and provide `ioremap()`, `ioremap_wt()`, `memset_io()`, `memcpy_fromio()`, and `memcpy_toio()`. `ioport_map()` returns a direct cast and `ioport_unmap()` is a no-op.

## Control Flow, State, and Persistence
Mapping state is owned by `arch/m68k/mm/kmap.c`; inline helpers only choose cache flags or perform direct copies through forced pointers.

## Dependencies and Integration Points
MMIO drivers use these helpers to map physical device ranges and copy to/from I/O memory. `io_mm.h` and `io_no.h` include this header for generic I/O compatibility.

## Risks
Wrong cache flags can break device coherency. `memcpy_*io` uses compiler builtins, so callers must ensure the target region is safe for normal-width accesses. `ioport_map()` does not allocate a special mapping.

## Test Signals
Driver probe and MMIO access on MMU systems, cache-mode validation for framebuffers and device registers, and build coverage for non-MMU configs where the MMU-only block is omitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/kmap.h -->
