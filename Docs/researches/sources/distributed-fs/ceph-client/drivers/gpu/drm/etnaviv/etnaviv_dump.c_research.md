# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_dump.c

## Purpose
Creates etnaviv devcoredump files on GPU hangs, collecting registers, MMU state, ring buffer, submitted command buffer, buffer-object physical map, and BO contents.

## Important APIs, Types, and Functions
Module parameter `dump_core` gates one-shot dumping. Internal helpers are `etnaviv_core_dump_header`, register/MMU/memory dump emitters, and `struct core_dump_iterator`. Exported `etnaviv_core_dump()` consumes `struct etnaviv_gem_submit`.

## Control Flow
On first enabled dump, it locks the submit MMU context, computes dump size and object count, allocates vmalloc memory, writes zeroed headers followed by data sections, dumps registers/MMU/ring/cmd, unlocks MMU, optionally writes a BO physical page map, copies each submitted BO, writes an end marker, and hands the buffer to `dev_coredumpv()`.

## State and Persistence
`etnaviv_dump_core` is set false after the first dump unless rearmed through the module parameter. Dump contents persist through the kernel devcoredump mechanism for userspace collection.

## Dependencies and Integration Points
Called by scheduler hang handling. Depends on GPU register accessors, MMU dump helpers, GEM page/vmap helpers, cmdbuf VA translation, devcoredump, and generated state register constants.

## Risks
Large dumps can fail `GFP_NOWAIT` allocation. BO copying races are mitigated by submit ownership but page/vmap failures may leave sparse sections. Register reads must account for power-register address fixups.

## Test Signals
Induced GPU hangs, devcoredump file format parsing, register/MMU/ring/cmd section presence, BO map consistency, and rearming `dump_core` are relevant.
