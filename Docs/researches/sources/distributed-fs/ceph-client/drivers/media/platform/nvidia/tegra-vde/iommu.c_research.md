# sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/iommu.c

## Purpose
`iommu.c` provides IOMMU and IOVA-domain support for the Tegra VDE driver. It maps SG tables into VDE-visible IOVA space and initializes/deinitializes the VDE IOMMU domain.

## Important APIs, Types, and Functions
Public functions are `tegra_vde_iommu_map()`, `tegra_vde_iommu_unmap()`, `tegra_vde_iommu_init()`, and `tegra_vde_iommu_deinit()`. Initialization also handles legacy ARM DMA-IOMMU mappings when `CONFIG_ARM_DMA_USE_IOMMU` is enabled.

## Control Flow
Init gets the device IOMMU group; absence of a group means the driver operates without an IOMMU. If a legacy ARM DMA mapping exists, it detaches/releases it, then allocates a paging domain, initializes the IOVA allocator using the domain page size, attaches the group, reserves static invalid-address space from `0x60000000` to `0x70000000`, and reserves the last page to avoid BSEV end-address wraparound. Map aligns the requested size, allocates an IOVA near the aperture end, maps the SG table read/write into the domain, and returns the IOVA. Unmap removes the mapping and frees the IOVA. Deinit frees reservations, detaches, releases IOVA cache/domain, frees the IOMMU domain, and drops the group.

## State and Persistence
State lives in `vde->domain`, `vde->group`, `vde->iova`, and reservation pointers. Mappings are volatile runtime DMA state and are also referenced by BOs and DMA-buf cache entries. There is no persistence.

## Dependencies and Integration Points
The file depends on Linux IOMMU, IOVA allocator, platform device infrastructure, optional ARM DMA-IOMMU compatibility, and the VDE buffer/cache code.

## Risks and Edge Cases
No IOMMU group is a valid path, but it forces other code to require physically contiguous buffers. Failure after attaching must unwind reservations, IOVA domain, cache, domain, and group in the right order. The reserved ranges encode hardware quirks; removing them can reintroduce invalid access traps or address wrap failures.

## Test Signals
Test hardware with and without IOMMU, SG-table map/unmap balance, allocation near aperture boundaries, init failure unwinding with forced errors, imported non-contiguous buffers, and deinit after cached mappings are drained.
