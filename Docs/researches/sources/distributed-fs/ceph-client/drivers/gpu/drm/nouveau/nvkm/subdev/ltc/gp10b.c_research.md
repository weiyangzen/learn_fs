# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/gp10b.c

## Purpose
Implements Tegra GP10B LTC init differences, including LTC count programming and optional IOMMU stream ID setup.

## Important APIs, Types, and Functions
`gp10b_ltc_init` programs LTC count registers and writes `sid << 2` to `0x160000` when `tegra_dev_iommu_get_stream_id` succeeds. `gp10b_ltc_new` registers the backend.

## Control Flow, State, and Persistence
The table reuses GP100 oneinit/interrupt, GM107 CBC/color/depth, GP102 stencil, and GF100 cache operations. Init persists the Tegra stream ID and LTC count into hardware after base.c replays ZBC state.

## Dependencies and Integration Points
Depends on Tegra IOMMU helpers, GP100/GM107/GP102/GF100 common functions, and the public LTC base.

## Risks and Test Signals
Risks are stream-ID programming failure, SoC-specific register mismatch, and inherited missing tag RAM setup. Test Tegra GP10B boot, IOMMU DMA faults, ZBC replay, cache flush/invalidate, and interrupt dispatch.
