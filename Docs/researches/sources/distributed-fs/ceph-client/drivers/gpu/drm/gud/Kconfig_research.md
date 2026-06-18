
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gud/Kconfig

## Purpose
`gud/Kconfig` defines the kernel configuration option for the Generic USB Display DRM driver.

## Important APIs, Types, And Functions
It declares `config DRM_GUD` as a tristate option named "GUD USB Display". The option depends on `DRM`, `USB`, and `MMU`, and selects `LZ4_COMPRESS`, `DRM_CLIENT_SELECTION`, `DRM_KMS_HELPER`, `DRM_GEM_SHMEM_HELPER`, and `BACKLIGHT_CLASS_DEVICE`.

## Control Flow
There is no runtime flow. During kernel configuration, enabling this option controls whether `drivers/gpu/drm/gud/Makefile` builds the `gud` module or built-in object.

## State And Persistence
The file stores build-time configuration state only. If selected as a module, the resulting module is named `gud`.

## Dependencies And Integration Points
The selected helpers match the implementation's use of USB control/bulk transfers, DRM KMS helpers, GEM shmem framebuffers, LZ4 compression, DRM clients/fbdev setup, and backlight registration.

## Risks
Missing a selected dependency would surface as compile or link failures in `gud_drv.c`, `gud_pipe.c`, or `gud_connector.c`. The `MMU` dependency is important because the driver allocates vmalloc buffers and maps them into scatterlists for USB bulk transfer.

## Test Signals
Configuration tests should cover built-in and module builds with `CONFIG_DRM_GUD=y/m`, confirm required helper symbols are selected, and verify the `gud` module autoloads for the supported USB IDs.
