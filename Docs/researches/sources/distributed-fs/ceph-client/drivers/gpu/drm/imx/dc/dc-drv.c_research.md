<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-drv.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-drv.c

Purpose: Provides the top-level i.MX8 DC DRM platform driver, component master, DRM device allocation/registration, PM hooks, and subdevice population.

Important APIs/types/functions: Defines `dc_drm_driver`, `dc_probe()`, `dc_remove()`, `dc_drm_bind()`, `dc_drm_unbind()`, runtime/system PM hooks, and the `dc_driver` platform driver with OF compatible `fsl,imx8qxp-dc`.

Control flow: Probe allocates private state, gets the configuration clock, sets 32-bit DMA mask, enables runtime PM, populates OF children, builds a component match for children and grandchildren excluding the interrupt controller, and registers the component master. Bind allocates `struct dc_drm_device`, binds all components, runs post-bind pointer fixups, initializes KMS, registers DRM, and starts the DRM client setup. Unbind unplugs DRM, uninitializes KMS, and performs atomic shutdown.

State and persistence behavior: `struct dc_priv` stores the registered DRM device and configuration clock. The aggregate `struct dc_drm_device` owns arrays of CRTC/plane/encoder and component pointers.

Dependencies: DRM core, GEM DMA/fbdev helpers, component framework, OF platform, runtime PM, clocks, DMA mask, and DC subcomponent platform drivers.

Integration points: Kbuild includes this object in `imx8-dc-drm`. It is the root that ties all component drivers into one DRM device.

Risks: Component matching against both children and grandchildren must match device-tree layout exactly. Shutdown/suspend paths assume `priv->drm` is valid. Partial bind failures must unwind KMS and component state correctly.

Test signals: Probe/remove, module load/unload, component bind failure injection, runtime PM clock enable/disable, system suspend/resume, DRM device registration, and fbdev/client setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-drv.c -->
