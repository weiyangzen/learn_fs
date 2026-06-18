# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_drv.c

Purpose: Implements the main OMAP DRM platform driver, DRM device setup/teardown, modeset pipeline construction, global atomic private state, atomic commit tail, custom zpos normalization, GEM ioctls, PM hooks, and module registration.

Important APIs/functions: `omapdrm_init()` allocates/registers a DRM device, initializes private state, GEM, mode config, global private object, overlays, modeset, vblank, poll helpers, fbdev, and DRM registration. `omap_modeset_init()` connects DSS outputs, creates planes, encoders, bridge connectors, CRTCs, pipeline/channel lookup tables, mode limits, and IRQ install. `omap_atomic_commit_tail()` sequences modeset disables/enables, plane commits, waits for completion, and cleanup, with an OMAP3-specific ordering exception. `omap_atomic_update_normalize_zpos()` adjusts normalized zpos for dual-overlay planes. Ioctls expose chipset ID and GEM create/info.

Control flow: Module init initializes DSS and registers DMM plus DRM platform drivers. Probe sets a 32-bit DMA mask, allocates `omap_drm_private`, and calls init. Modeset setup builds one connector/encoder/CRTC chain per connected DSS output. Atomic commit runtime-resumes DISPC around the hardware update and waits for CRTC pending completion before old buffers are released.

State and persistence: `struct omap_drm_private` owns DSS/DISPC pointers, pipelines, channels, planes, overlays, global private object, GEM object list, workqueue, IRQ waits, fbdev, and bandwidth limit. No disk persistence exists.

Dependencies/integration: Depends on DRM core/atomic/bridge connector/GEM/PRIME/fbdev helpers, OMAP DSS stack readiness, DISPC, overlays/planes/CRTC/encoder/fb/IRQ/GEM modules, DMM driver, SoC matching, and PM helpers.

Risks and test signals: Pipeline assumptions require one output per DISPC channel and no more outputs than managers/primary planes. Atomic ordering differs for OMAP3 versus later SoCs. Cleanup must disconnect pipelines after failure. Test multi-display DT aliases, deferred bridge probes, zpos with dual-overlay planes, GEM ioctls, suspend/resume, vblank init, max bandwidth filtering, and driver unload.
