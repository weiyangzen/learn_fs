<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/Kconfig

## Purpose
Adds the `DRM_KMB_DISPLAY` Kconfig option for the Intel Keem Bay display controller DRM driver.

## Important APIs, types, and functions
The symbol is tristate, depends on DRM and either `ARCH_KEEMBAY` or `COMPILE_TEST`, and selects DRM client, KMS helper, display helper, bridge connector, GEM DMA helper, and MIPI DSI support.

## Control flow
No runtime control flow exists. Build selection controls whether the `kmb-drm` module or built-in object is compiled.

## State and persistence
No runtime state is defined. The selected config persists in the kernel build and determines availability of the display driver.

## Dependencies and integration points
Ties the KMB display implementation to the DRM/KMS stack, GEM DMA framebuffer memory, bridge connectors, and MIPI DSI infrastructure.

## Risks
Missing selected helpers would break compilation or probe. The option is narrow to Keem Bay hardware but allows compile-test coverage on other architectures.

## Test signals
Build `CONFIG_DRM_KMB_DISPLAY=y/m` with Keem Bay and COMPILE_TEST configurations. Runtime validation belongs to the module probe and mode-setting files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/Kconfig -->
