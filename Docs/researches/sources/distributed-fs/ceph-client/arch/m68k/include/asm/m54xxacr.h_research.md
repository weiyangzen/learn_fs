<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m54xxacr.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m54xxacr.h

## Purpose
`m54xxacr.h` defines cache and ACR policy for ColdFire version 4 cores.

## Important APIs, Types, and Functions
It defines data/instruction/branch cache CACR bits, ACR base/mask/cache modes, `ACR_BA()` and `ACR_ADMSK()`, cache sizes for M5407/M54xx/M5441x, line size, ways, set masks, `CACHE_MODE`, `CACHE_INIT`, invalidate modes, optional `CACHE_PUSH`, and ACR modes for MMU and non-MMU configurations.

## Control Flow, State, and Persistence
There is no executable flow. Build-time configuration selects cache geometry and copy-back/write-through behavior.

## Dependencies and Integration Points
M5407, M54xx, and M5441x SIM headers include this file. Cache initialization, cacheflush code, and I/O mapping rely on its ACR definitions, especially `IOMEMBASE/IOMEMSIZE` under MMU.

## Risks
Version 4 has separate instruction/data caches and branch cache; incomplete invalidation can leave stale instructions or data. Copy-back mode requires dirty-line pushes before device DMA. ACR masks must match RAM and MMIO size.

## Test Signals
Signals include cache flush tests after code patching, DMA coherency tests, MMU and non-MMU boot, copy-back versus write-through configurations, and performance/branch-cache sanity checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m54xxacr.h -->
