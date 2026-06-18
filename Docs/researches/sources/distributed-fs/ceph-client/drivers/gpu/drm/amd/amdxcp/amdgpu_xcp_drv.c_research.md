# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdxcp/amdgpu_xcp_drv.c

## Purpose
Provides a small DRM render-device wrapper for AMD XCP partitions. It allocates platform devices and devm-managed DRM devices so partitioned GPU nodes can have separate DRM render nodes.

## Important APIs, Types, And Functions
`struct xcp_device` embeds `struct drm_device` and stores the backing `platform_device`. `amdgpu_xcp_driver` advertises `DRIVER_GEM | DRIVER_RENDER` with name `amdgpu_xcp_drv`. Global state is `pdev_num`, `xcp_dev[MAX_XCP_PLATFORM_DEVICE]`, and `xcp_mutex`. Exported functions are `amdgpu_xcp_drm_dev_alloc`, `amdgpu_xcp_drm_dev_free`, and `amdgpu_xcp_drv_release`.

## Control Flow
Allocation takes the mutex, finds a free slot below 64, registers a simple platform device named `amdgpu_xcp_%d`, opens a devres group, allocates a DRM device with `devm_drm_dev_alloc`, records it in the slot table, returns the embedded DRM pointer, and increments the count. Free scans for the DRM pointer under the mutex and calls `free_xcp_dev`, which releases devres, unregisters the platform device, clears the slot, and decrements the count. Module exit calls release for all remaining devices.

## State And Persistence
State is runtime-global in the slot array and count. Device resources are tied to platform-device devres groups and are released on explicit free or module exit.

## Dependencies And Integration Points
Uses Linux platform device APIs, devres, DRM driver/device allocation, module exit, and exported symbols. KFD topology consumes the resulting XCP DRM render minor through `gpu->xcp->ddev`.

## Risks
The fixed 64-device table can return `-ENODEV` under extreme partition counts or leaks. Correctness depends on callers freeing exactly the DRM devices returned. `int8_t` indexes/counts are adequate for 64 entries but fragile if the limit grows. Allocation failure after platform registration must keep devres/platform cleanup balanced.

## Test Signals
Tests should allocate and free multiple XCP devices, verify unique platform names/render devices, hit allocation failure cleanup paths, call release with live devices, and run module unload/leak checks.
