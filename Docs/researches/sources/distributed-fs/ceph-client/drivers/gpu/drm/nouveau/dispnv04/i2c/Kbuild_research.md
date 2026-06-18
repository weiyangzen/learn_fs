<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/i2c/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/i2c/Kbuild

## Purpose
This build fragment defines optional external I2C encoder modules for pre-NV50 Nouveau display support.

## Important APIs, Types, and Functions
It declares `ch7006-y` as `ch7006_drv.o` plus `ch7006_mode.o`, adds it when `CONFIG_DRM_NOUVEAU_CH7006` is enabled, declares `sil164-y` as `sil164_drv.o`, and adds it when `CONFIG_DRM_NOUVEAU_SIL164` is enabled.

## Control Flow
There is no runtime flow. Kbuild combines the listed objects into module/built-in targets selected by kernel configuration.

## State and Persistence Behavior
No runtime state is stored. The file determines whether CH7006 TV and SIL164 TMDS slave encoder support is available to `request_module` and Nouveau's I2C encoder creation path.

## Dependencies and Integration Points
It integrates with the parent Nouveau Kbuild, Kconfig symbols, and the external encoder bridge in `nouveau_i2c_encoder.c`.

## Risks
If config symbols are disabled, DCB entries requiring those external encoders cannot bind. Object list changes must stay synchronized with exported symbols across driver and mode files.

## Test Signals
Build with both symbols enabled, disabled, built-in, and modular. Runtime probe of CH7006 and SIL164 DCB outputs verifies the objects were linked and module autoload names match I2C board info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/i2c/Kbuild -->
