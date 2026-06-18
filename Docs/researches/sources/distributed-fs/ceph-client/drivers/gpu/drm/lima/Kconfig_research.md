<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/Kconfig

## Purpose
Adds `DRM_LIMA`, the DRM render driver option for ARM Mali 400/450 Utgard GPUs.

## Important APIs, types, and functions
The symbol is tristate, depends on DRM, ARM/ARM64/COMPILE_TEST, MMU, COMMON_CLK, and OF, and selects DRM scheduler, GEM shmem helper, PM devfreq, and the simple_ondemand devfreq governor.

## Control flow
No runtime flow. The selected symbol controls compilation of the `lima` module or built-in driver.

## State and persistence
No runtime state exists. Build configuration determines availability of the driver and its scheduler/devfreq dependencies.

## Dependencies and integration points
Links the driver to the DRM render-node stack, MMU-backed VM, device tree probing, clock framework, DRM scheduler, shmem GEM, and devfreq.

## Risks
The driver relies on selected subsystems for core behavior; missing scheduler or shmem support would be fatal. COMPILE_TEST broadens build coverage but cannot validate hardware-specific paths.

## Test signals
Build with module and built-in configurations on ARM/ARM64 and COMPILE_TEST. Runtime signals are probe and render-node IOCTL tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/Kconfig -->
