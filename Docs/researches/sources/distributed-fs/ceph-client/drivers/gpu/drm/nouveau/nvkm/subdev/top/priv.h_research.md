# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/top/priv.h

## Purpose
Defines the private topology parser callback contract and shared allocation helper.

## Important APIs, Types, And Functions
`struct nvkm_top_func` contains the chip `parse` callback. The header declares `nvkm_top_new_()` and `nvkm_top_device_new()`.

## Control Flow
Chip files include this header, provide a parse function, and use the helper to allocate list entries.

## State, Persistence, And Dependencies
No runtime state is stored in the header; it defines the callback ABI.

## Integration Points
Integrates GK104 and GA100 topology parsers with the common top base.

## Risks
Callback or structure changes require coordinated updates across topology files.

## Test Signals
Compile-time coverage and successful topology parsing are the primary signals.
