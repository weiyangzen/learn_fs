<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/sddr2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/sddr2.c

## Purpose
Calculates SDR DDR2 mode register values from Nouveau RAM timing and configuration data.

## Important APIs, Types, And Functions
Defines `struct ramxlat`, `ramxlat`, translation tables for DDR2 CAS latency and write recovery encodings, and exported `nvkm_sddr2_calc(struct nvkm_ram *ram)`.

## Control Flow
`nvkm_sddr2_calc` reads timing version 0x10 or 0x20 data, derives CL, WR, DLL state, and ODT state, falls back to existing MR1 ODT bits when timing data is unavailable or version 0x20 is used, translates timing values to register encodings, then updates `ram->mr[0]` and `ram->mr[1]`.

## State And Persistence
It mutates only the pending mode-register array on `struct nvkm_ram`; hardware is not written directly. The caller later programs these values through the RAM sequencer.

## Dependencies And Integration Points
Depends on `struct nvkm_ram` BIOS timing fields and is consumed by memory reclocking paths that support DDR2.

## Risks And Edge Cases
Unsupported timing versions return `-ENOSYS`; unsupported CL/WR values return `-EINVAL`. Some DDR2 encodings are noted as only present in some documentation, so VBIOS entries outside the tables will fail.

## Test Signals
Passing reclock calculations, correct MR values in debug traces, and stable DDR2 reclocking are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/sddr2.c -->
