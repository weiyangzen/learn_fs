# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/fifo.c

## Purpose
This file queries and caches FIFO runlist-to-engine mappings for a device.

## Important APIs, Types, and Functions
Public function is `nvif_fifo_runlist`. Internal `nvif_fifo_runlists` performs the device info query and allocation.

## Control Flow
The first runlist request allocates a query structure, asks `NV_DEVICE_V0_INFO` for host runlists and per-runlist engine masks, computes the number of runlists, allocates `device->runlist`, and caches engine masks. `nvif_fifo_runlist` then returns a bitmask of runlists containing the requested engine bit.

## State and Persistence Behavior
State persists in `device->runlists` and the allocated `device->runlist` array until device destruction.

## Dependencies and Integration Points
It depends on NVIF device info methods and is used by channel/runlist setup to select compatible runlists.

## Risks
The fixed stack of 64 runlist entries must cover backend reports. Query failure returns an empty mask. Cached results are not refreshed after creation.

## Test Signals
Signals include runlist discovery on multi-engine GPUs, query failure paths, device destructor freeing, and engine-to-runlist selection.
