<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gb10x.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gb10x.c

## Purpose
Defines GB10x RM class IDs for Blackwell datacenter-style GPUs.

## Important APIs, Types, And Functions
Exports `gb10x_gpu` with Hopper usermode, Blackwell FIFO channel, CE, GR/compute, NVDEC, NVJPG, and OFA classes.

## Control Flow
No runtime flow; constructors consume the table.

## State And Persistence
Immutable RM class metadata.

## Dependencies And Integration Points
Referenced by GB100 GSP function table. Uses TU102 doorbell helper for FIFO channels.

## Risks And Edge Cases
Display classes are absent; display construction should not expect them. Wrong Blackwell class IDs break RM allocations.

## Test Signals
Successful FIFO, CE, GR, NVDEC, NVJPG, and OFA object allocation on GB10x.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gb10x.c -->
