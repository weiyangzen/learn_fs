# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_mdp_rdma.h

## Purpose
Defines the configuration payload for MediaTek MDP RDMA programming.

## Important APIs, types, and functions
`struct mtk_mdp_rdma_cfg` carries pitch, base address, width, height, crop origin, DRM format, and DRM color encoding.

## Control flow
The header has no control flow. It is a data contract consumed by `mtk_mdp_rdma_config()`.

## State and persistence
The struct represents transient per-plane/per-update configuration; persistence occurs only after the implementation writes the values to RDMA registers or CMDQ packets.

## Dependencies and integration points
Used by MediaTek display code that prepares RDMA memory-source configuration. The fields line up with DRM framebuffer geometry and color metadata.

## Risks
`addr0` is `unsigned int` instead of `dma_addr_t`, which is a potential limitation on platforms or IOMMU setups with addresses beyond 32 bits. The header does not declare the functions implemented in `mtk_mdp_rdma.c`, so callers likely get those prototypes from `mtk_disp_drv.h`.

## Test signals
Build coverage catches struct field use. Runtime validation is correct RDMA scanout for base address, pitch, crop, format, and color encoding combinations.
