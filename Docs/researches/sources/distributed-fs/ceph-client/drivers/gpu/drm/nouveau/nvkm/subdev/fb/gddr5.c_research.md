<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gddr5.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gddr5.c

## Purpose
Calculates GDDR5 mode-register values from parsed NVBIOS RAM timing/configuration data, including write latency, read latency, drive strength, termination, and optional per-partition differences.

## Important APIs, Types, And Functions
Exports `nvkm_gddr5_calc(struct nvkm_ram *, bool nuts)`. It fills `ram->mr[]` and `ram->mr1_nuts` using frequency, `ram->next->bios`, and GDDR5-specific latency/termination rules.

## Control Flow
The function derives WL, CL, WR and auxiliary timing variables from target frequency and BIOS fields, then constructs MR0/MR1/MR3/MR5/MR6/MR7/MR8 values. The `nuts` argument enables alternate MR1 handling for partitions whose physical memory wiring differs from the primary partition.

## State And Persistence
State is staged in the `nvkm_ram` object only. Actual persistence occurs when GK104-era scripts program MR registers and, for `nuts`, write adjusted values to non-uniform partitions.

## Dependencies And Integration Points
Used by GK104 and descendants for GDDR5 reclocking. Depends on BIOS rammap/timing decoding, partition-difference detection, and ramfuc command emission.

## Risks
GDDR5 mode-register values are extremely timing-sensitive. Wrong latency or drive/termination bits can cause immediate memory training failures or subtle data corruption. The `nuts` path must stay aligned with partition masks detected by the caller.

## Test Signals
Signals are successful reclocking across low/high memory clocks, stable GDDR5 training, no FIFO/FB errors after transition, and debug comparison of MR values against expected BIOS-derived configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gddr5.c -->
