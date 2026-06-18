# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/priv.h

## Purpose
Defines the private LTC backend contract and shared helper declarations for chip-specific cache/tag/ZBC implementations.

## Important APIs, Types, and Functions
`struct nvkm_ltc_func` declares oneinit/init/intr, CBC clear/wait, ZBC color/depth/stencil capacities and writers, and cache invalidate/flush hooks. The header declares GF100, GM107, GP100, and GP102 shared helpers used by later chip files.

## Control Flow, State, and Persistence
No executable flow is present. The function table determines which hardware paths base.c calls and controls persistent ZBC replay and tag clearing behavior.

## Dependencies and Integration Points
Includes public `subdev/ltc.h` and `core/enum.h`; consumed by all LTC implementation files.

## Risks and Test Signals
Risks are missing optional callbacks, incorrect capacity values, and helper signature drift. Build all chip variants and run ZBC/tag/interrupt paths to validate the interface.
