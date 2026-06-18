# sources/distributed-fs/ceph-client/arch/arm/include/asm/glue-cache.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/glue-cache.h` selects cache maintenance
implementations according to CPU/cache configuration. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `ASM_GLUE_CACHE_H`, `MULTI_CACHE`, `_CACHE`, `__cpuc_flush_icache_all`,
`__cpuc_flush_kern_all`, `__cpuc_flush_kern_louis`, `__cpuc_flush_user_all`,
`__cpuc_flush_user_range`, `__cpuc_coherent_kern_range`, `__cpuc_coherent_user_range`,
`__cpuc_flush_dcache_area`, `dmac_flush_range`. The file is 151 lines / 2950 bytes, and the exported
surface is primarily an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
DMA-visible state depends on cache cleanliness, bus mappings, and device/platform data owned by the
DMA mapping or driver layers. There is no userspace filesystem persistence in this file; persistence
is either kernel memory, CPU register state, hardware register state, or generated ABI values.
Direct includes are `asm/glue.h`. It integrates with generic Linux ARM architecture code through
include-time contracts rather than a standalone translation unit. DMA paths integrate with cache
maintenance, IOMMU, scatterlist, and device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `glue-cache.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
run DMA mapping, scatterlist, and noncoherent-device tests; ensure all include users still build
with sparse/objtool-style diagnostics where available.
