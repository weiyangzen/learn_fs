<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gb20x.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gb20x.c

## Purpose
Defines GB20x RM class IDs and generation-specific FIFO/CE behavior for Blackwell display GPUs.

## Important APIs, Types, And Functions
Exports `gb20x_gpu` with display, usermode, FIFO channel, CE, GR, NVDEC, NVENC, NVJPG, and OFA class IDs. Uses `gb202_chan_doorbell_handle` and `gb202_ce_grce_mask`.

## Control Flow
No dynamic control flow. RM constructors use the table to allocate objects and to skip certain GRCE engines in FIFO setup.

## State And Persistence
Immutable class and callback metadata.

## Dependencies And Integration Points
Referenced by GB202 GSP function table; integrates with Blackwell FIFO and CE helper code.

## Risks And Edge Cases
Incorrect GRCE mask or doorbell callback affects channel creation and runlist selection. Display class mismatches break RM display init.

## Test Signals
Working GB20x display init, FIFO channel creation, and engine allocation across display/video/graphics/copy engines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gb20x.c -->
