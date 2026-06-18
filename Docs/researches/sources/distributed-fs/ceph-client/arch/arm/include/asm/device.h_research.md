# sources/distributed-fs/ceph-client/arch/arm/include/asm/device.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/device.h` adds ARM-specific per-device DMA
metadata and arch setup hooks. It is part of the ARM kernel-architecture compatibility layer
imported in the Ceph client source tree, so its direct consumers are kernel architecture, MM,
interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `ASMARM_DEVICE_H`, `to_dma_iommu_mapping`; types: `dev_archdata`, `dma_iommu_mapping`,
`omap_device`, `pdev_archdata`. The file is 29 lines / 533 bytes, and the exported surface is
primarily an include-time contract for other kernel files.

### Control Flow
MMU and mapping helpers are reached from memory-management setup, page-table transitions,
highmem/fixmap setup, or device mapping code rather than from normal filesystem paths.

### State, Persistence, And Dependencies
Caller-visible state is represented by `dev_archdata`, `dma_iommu_mapping`, `omap_device`,
`pdev_archdata`. DMA-visible state depends on cache cleanliness, bus mappings, and device/platform
data owned by the DMA mapping or driver layers. There is no userspace filesystem persistence in this
file; persistence is either kernel memory, CPU register state, hardware register state, or generated
ABI values. It integrates with generic Linux ARM architecture code through include-time contracts
rather than a standalone translation unit. Mapping helpers depend on page-table, vmalloc, highmem,
or memory-type definitions supplied elsewhere under `arch/arm`. DMA paths integrate with cache
maintenance, IOMMU, scatterlist, and device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `device.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
incorrect address alignment, memory type, or cache alias handling can corrupt data or make
executable mappings incoherent.

### Test Signals
run MMU, highmem, ioremap, kexec, and cache/TLB coherency tests; run DMA mapping, scatterlist, and
noncoherent-device tests; ensure all include users still build with sparse/objtool-style diagnostics
where available.
