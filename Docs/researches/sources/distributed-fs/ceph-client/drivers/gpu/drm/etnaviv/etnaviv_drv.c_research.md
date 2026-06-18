# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_drv.c

## Purpose
Implements the top-level etnaviv DRM driver: module/platform registration, component master binding, DRM device setup, per-open context lifecycle, debugfs, ioctl dispatch, and GEM/PRIME integration.

## Important APIs, Types, and Functions
Important functions include `etnaviv_open`, `etnaviv_postclose`, ioctl handlers for params/GEM CPU prep/fini/info/userptr/waits/perfmon, debugfs show functions, `etnaviv_bind/unbind`, `etnaviv_pdev_probe/remove`, and module init/exit. The `drm_driver` advertises `DRIVER_GEM | DRIVER_RENDER`, ioctl table, PRIME import, fdinfo, debugfs, fops, and version metadata.

## Control Flow
Module init initializes command validation, registers GPU and master platform drivers, and creates a virtual etnaviv platform device when DT has an available Vivante GPU. Probe sets DMA masks/configuration and registers a component master. Bind allocates `drm_device` and private state, initializes xarray/GEM list/cmdbuf suballocator, binds GPU components, initializes available GPUs, and registers the DRM device. Open allocates a file-private context, assigns an xarray ID, creates an IOMMU context, and initializes scheduler entities per GPU. Postclose destroys scheduler entities, drops the MMU context, erases the xarray entry, and frees the context.

## State and Persistence
Driver-private state tracks GPU pointers, command buffer suballocator, global MMU, active contexts xarray, GEM object list, shared-memory GFP mask, and optional flop-reset cmdbuf. State exists while the DRM device is bound.

## Dependencies and Integration Points
Integrates Linux component framework, platform driver/DT matching (`vivante,gc`), DMA masks, DRM core, DRM scheduler, GEM helpers, PRIME, debugfs, etnaviv GPU/MMU/perfmon/GEM submit implementations, and generated validation init.

## Risks
Partial bind failures must unwind suballocator/private/device state correctly. Open error paths must release xarray IDs and MMU contexts; this file currently frees ctx on MMU init failure but the xarray allocation path requires scrutiny. DMA mask assumptions affect command buffer reachability. Device-tree component matching must include all active GPU cores.

## Test Signals
Module load/unload, bind/unbind with multiple GPUs, render-node open/close stress, ioctl validation tests, DMA mask probe failures, debugfs reads, and scheduler entity leak checks.
