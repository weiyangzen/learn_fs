# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_drv.c

## Purpose

`vkms_drv.c` is the VKMS module and DRM driver entry point. It declares module parameters, DRM driver/mode-config callbacks, device creation/destruction, module init/exit, and default-device setup.

## Important APIs and functions

Module parameters control default cursor, writeback, overlay, plane pipeline, and whether a default VKMS device is created. `vkms_atomic_commit_tail()` sequences DRM atomic helper operations, fake vblank, flip completion waits, composer work flushing, and plane cleanup. `vkms_atomic_check()` validates gamma LUT size before delegating to DRM atomic checks. `vkms_modeset_init()` initializes mode config bounds and output components. Public lifecycle APIs are `vkms_create()` and `vkms_destroy()`.

## Control flow and state

`vkms_init()` registers configfs, optionally creates a default config from module params, instantiates a device, and stores it in `default_config`. `vkms_create()` creates a faux device, opens a devres group, allocates a managed DRM device, stores config back-pointer, coerces DMA mask, initializes vblank count from config CRTCs, initializes modeset/output, registers debugfs, registers the DRM device, and starts client setup. Error paths release devres and destroy the faux device. `vkms_destroy()` unregisters DRM, shuts down atomic state, releases devres, destroys the faux device, and clears `config->dev`.

## Dependencies and integration

The file depends on faux devices, DRM managed allocation, GEM shmem helpers, fbdev shmem helpers, vblank, atomic helpers, config/configfs, and output initialization from other VKMS files. Configfs-created and default devices both converge on `vkms_create()`.

## Risks and test signals

Risks include init failure after configfs registration leaking registration when default-device creation fails, resource-group lifetime ordering, composer work flushing before cleanup, gamma LUT size calculation correctness, and module parameter interactions. Test signals include module load/unload, default device creation, configfs-created devices, fbdev client setup, atomic modesets, and KUnit suites for config/color/format helpers.
