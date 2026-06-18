<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_modeset.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_modeset.c

Purpose: Implements UDL atomic modesetting: DisplayLink register command generation, damage upload from shadow framebuffers, primary plane, CRTC enable/disable, connector detect/modes, mode limits, and KMS object initialization.

Important APIs/types/functions: Register-command helpers produce `UDL_MSG_BULK` packets. `udl_lfsr16()` converts timing values to hardware LFSR counters. `udl_set_display_mode()` maps DRM mode timings to DisplayLink registers. `udl_handle_damage()` renders each damaged line through `udl_render_hline()`. Plane helper functions use DRM shadow-plane helpers and damage iterators. CRTC enable sends color depth, base addresses, display mode, blank on, unlock, and dummy render; disable sends powerdown. Connector helpers use UDL EDID reads and detection. `udl_modeset_init()` creates mode config, primary plane, CRTC, encoder, and VGA connector.

Control flow: Atomic update begins CPU access to framebuffer, enters DRM device, iterates damage clips, and sends compressed URB command streams. Atomic enable/disable each allocate one URB and submit a register sequence. Mode validation enforces `sku_pixel_limit` if present.

State and persistence: State lives in DRM plane/CRTC/connector objects, shadow plane map, hardware registers, and the UDL URB pool. Mode programming is sent to device but not persisted by the driver.

Dependencies and integration points: Integrates DRM atomic helpers, damage helpers, GEM shmem/shadow helpers, EDID helpers, DisplayLink protocol constants, and URB submission from `udl_main.c`.

Risks and test signals: Risks include ignored return values inside damage loop, CPU-access direction ambiguity, LFSR timing mistakes, fixed 16bpp hardware programming despite XRGB8888 input conversion, and mode-limit mismatches. Tests should cover damage clips, full-screen updates, 16/32bpp conversion, mode enable/disable, EDID hotplug, oversized modes, and USB unplug during atomic update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_modeset.c -->
