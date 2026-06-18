<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m52xxacr.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m52xxacr.h

## Purpose
`m52xxacr.h` defines cache control and access-control register settings for ColdFire version 2 cores.

## Important APIs, Types, and Functions
It defines CACR bits for enabling, invalidating, freezing, and selecting instruction/data caches; ACR base/mask/access/cache bits; `CACHE_TYPE`, `CACHE_INIT`, `CACHE_MODE`, `CACHE_INVALIDATE`, optional instruction/data invalidate modes, and `ACR0_MODE`/`ACR1_MODE`.

## Control Flow, State, and Persistence
There is no executable code. Kconfig selections such as `CONFIG_CACHE_I`, `CONFIG_CACHE_D`, and `CONFIG_CACHE_BOTH` choose the constants used by low-level cache setup.

## Dependencies and Integration Points
ColdFire v2 SIM headers include this file. Cache initialization, TLB/cacheflush code, and early boot setup program CACR/ACR registers from these macros.

## Risks
Cache mode mistakes can corrupt DMA or instruction fetch coherency. Older instruction-cache-only devices share this file with split-cache parts, so Kconfig assumptions matter. `ACR0_MODE` maps RAM based on `CONFIG_RAMBASE`.

## Test Signals
Boot with instruction-only, data-only, and split-cache configs where supported. Validate cache flush/invalidate behavior, DMA coherency, and performance counters or memory tests under copy/write buffer settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m52xxacr.h -->
