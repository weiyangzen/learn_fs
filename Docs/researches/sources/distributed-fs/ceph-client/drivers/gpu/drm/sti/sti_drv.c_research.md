# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_drv.c

Purpose: Top-level STI DRM module and component master. It registers all STI display platform drivers, creates the DRM device, binds subcomponents, initializes mode config/GEM/fbdev helpers, and exposes debugfs FPS controls.

Important APIs/functions: `sti_drm_init()` registers the platform driver array unless firmware-only mode is active. `sti_platform_probe()` sets a 32-bit DMA mask, populates OF children, and calls `drm_of_component_probe()`. `sti_bind()` allocates `drm_device`, runs `sti_init()`, binds all components, registers DRM, resets mode config, and starts generic client setup. `sti_cleanup()` shuts down KMS, unbinds components, and frees `sti_private`. `sti_drm_fps_get/set()` and `sti_drm_fps_dbg_show()` control/report per-plane FPS logging.

Control flow: Platform probe creates the component graph; master bind is the point where subdrivers create encoders, connectors, planes, CRTCs, and bridges. Errors unwind through DRM cleanup and `drm_dev_put()`.

State/persistence: `struct sti_private` is allocated with `kzalloc_obj`, stored in `drm_dev->dev_private`, and holds the compositor pointer after compositor bind. Plane FPS strings/counters are persistent per plane and toggled through debugfs.

Dependencies/integration: Uses DRM atomic helpers, GEM DMA helpers, fbdev DMA setup, OF component matching, and all local STI platform driver declarations.

Risks/test signals: `sti_platform_shutdown()` assumes `platform_get_drvdata()` returns a DRM device, but master setup stores the device via `dev_set_drvdata()` during `sti_init()`. Test probe/unbind failure paths, module unload, fbdev client creation, debugfs FPS toggling, and component bind ordering.
