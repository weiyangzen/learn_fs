# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_configfs.h

## Purpose

`vkms_configfs.h` declares the VKMS configfs registration lifecycle.

## Important APIs

`vkms_configfs_register()` registers the `/config/vkms` subsystem and is called during module initialization. `vkms_configfs_unregister()` unregisters it during module exit.

## Integration, state, and risks

The header has no state. It is included by `vkms_drv.c` for module lifecycle and by `vkms_configfs.c` for self-declarations. Risk is minimal; registration state is implemented in the `.c` file through `is_configfs_registered`.

## Test signals

Build coverage verifies declaration/definition consistency. Runtime integration is successful module load/unload with configfs enabled and no double-register/unregister warnings.
