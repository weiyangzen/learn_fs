<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memblock.h -->
# sources/distributed-fs/ceph-client/include/linux/memblock.h

## Purpose
This header defines the early-boot memblock allocator and memory-region registry used before the full page allocator is available.

## Important APIs, types, and functions
Core types are `enum memblock_flags`, `struct memblock_region`, `struct memblock_type`, and global `struct memblock memblock`. APIs cover adding/removing memory, reserving and freeing physical ranges, marking flags such as hotplug/nomap/mirror/driver-managed/noinit/kernel/kexec-handover scratch, iterating ranges, NUMA node assignment, physical and virtual early allocation, memory limits, size queries, address membership checks, PFN conversion helpers, early hash allocation, memtest, and optional KHO scratch-only mode.

## Control flow
Architecture boot code populates `memblock.memory` from firmware maps, reserves kernel/initrd/device ranges in `memblock.reserved`, marks special attributes, and allocates early data structures from available ranges under `current_limit` and direction policy. Iteration macros walk memory, reserved, free, physical, and PFN ranges, optionally excluding flags or reserved regions. After boot, memblock metadata is discarded unless `CONFIG_ARCH_KEEP_MEMBLOCK` keeps it.

## State and persistence
Memblock state is global in-memory boot state: sorted region arrays, counts, totals, flags, node IDs, allocation direction, and allocation limit. It persists only as long as memblock is kept; physical memory reservations and nomap decisions affect later memory initialization.

## Dependencies and integration points
It depends on init annotations, mm types, DMA limits, PFN macros, NUMA, kmemleak/hash allocation, early memtest, and architecture boot code. It feeds zone setup, resource reservation, sparsemem, hotplug metadata, and early allocators.

## Risks and test signals
Risks include overlapping or unsorted ranges, off-by-one PFN conversion for unaligned reservations, resizing before `memblock_allow_resize()`, incorrect flag filtering in iterators, allocation above accessible limits, NUMA coverage gaps, and premature discard. Test firmware map parsing, reserve/free overlap, nomap and mirror marking, bottom-up/top-down allocation, NUMA node ranges, memory limit enforcement, KHO scratch mode, and 32-bit physical address limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memblock.h -->
