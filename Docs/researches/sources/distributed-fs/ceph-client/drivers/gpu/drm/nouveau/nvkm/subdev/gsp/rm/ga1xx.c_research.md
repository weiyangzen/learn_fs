<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/ga1xx.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/ga1xx.c

## Purpose
Defines GA10x RM class IDs for Ampere display, FIFO, graphics, copy, decode, encode, and OFA engines.

## Important APIs, Types, And Functions
Exports `ga1xx_gpu` as `struct nvkm_rm_gpu`.

## Control Flow
Static class data is read by RM-backed display, FIFO, and engine constructors.

## State And Persistence
Immutable generation metadata.

## Dependencies And Integration Points
Referenced by GA102 GSP RM function table. Uses NVIF class IDs and TU102 FIFO doorbell helper.

## Risks And Edge Cases
Bad class IDs cause RM allocation failures visible during display or engine initialization.

## Test Signals
Working display channels, FIFO channels, GR/CE/video object creation on GA10x.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/ga1xx.c -->
