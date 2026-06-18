# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/loongson_module.c

Purpose: module entry/exit and module parameters for the Loongson DRM driver.

Important APIs/types/functions: `loongson_modeset` parameter, exported `loongson_vblank` parameter, `loongson_module_init`, and `loongson_module_exit`.

Control flow: init refuses to load when modeset is disabled or firmware-only video drivers are requested, otherwise registers the PCI driver. Exit unregisters the PCI driver.

State and persistence: module parameters persist for module lifetime. `loongson_vblank` controls whether probe initializes vblank IRQ support.

Dependencies and integration points: depends on PCI driver object from `lsdc_drv.c` and `video_firmware_drivers_only`.

Risks and test signals: `loongson_modeset` default `-1` means enabled unless explicitly set to zero. Test module load with `modeset=0`, firmware-only boot, and `vblank=0/1`.
