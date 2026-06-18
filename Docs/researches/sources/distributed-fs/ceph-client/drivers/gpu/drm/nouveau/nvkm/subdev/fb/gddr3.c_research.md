<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gddr3.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gddr3.c

## Purpose
Calculates GDDR3 mode-register values from NVBIOS timing/config fields for use by the RAM reclocking scripts.

## Important APIs, Types, And Functions
Exports `nvkm_gddr3_calc(struct nvkm_ram *)`. Local `struct ramxlat` tables translate BIOS-encoded CL, WR, and CWL values into JEDEC-like mode register encodings.

## Control Flow
The calculator extracts CL, WR, CWL, DLL, ODT, RON, and high-frequency mode from `ram->next->bios`, applies translation tables, handles missing CWL by deriving it from CL on some paths, and writes the resulting MR values into `ram->mr[]` for later programming by generation-specific scripts.

## State And Persistence
It only mutates calculated `struct nvkm_ram` mode-register cache. Hardware persistence happens later when GT215/GF/GK scripts write MR registers.

## Dependencies And Integration Points
Called by GT215-style RAM calculation for GDDR3 targets. Depends on parsed NVBIOS rammap/timing fields and on generation scripts honoring `ram->mr[]`.

## Risks
Encoding tables are compatibility-sensitive; an unsupported BIOS value can produce invalid mode-register settings. DLL/ODT/RON interpretation must match board memory parts and voltage settings.

## Test Signals
Debug reclocking traces, successful memory clock transitions on GDDR3 boards, lack of post-reclock memory corruption, and comparison with known-good BIOS/NVIDIA behavior are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gddr3.c -->
