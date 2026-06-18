# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_plane.c

Purpose: Implements the primary OSD1 DRM plane for Meson. It validates primary-plane scaling, supports RGB formats with linear and SoC-specific ARM AFBC modifiers, stages OSD/scaler/blend/canvas state, and coordinates with AFBCD ops when compressed scanout is used.

Important APIs, types, and functions: `struct meson_plane` wraps `drm_plane`, private pointer, and enabled flag. Main callbacks are `meson_plane_atomic_check()`, `atomic_update()`, `atomic_disable()`, and `format_mod_supported()`. Helpers include `meson_g12a_afbcd_line_stride()` and `fixed16_to_int()`. Public constructor is `meson_plane_create()`.

Control flow: atomic check allows upscaling up to 5x and no downscaling (`DRM_PLANE_NO_SCALING`) while requiring final coordinates. Update locks `event_lock`, decides whether ARM AFBC is required on GXM/G12A, configures OSD control/global alpha/canvas/endian/path bits, selects block mode and color matrix from DRM format, configures alpha replacement, computes OSD scaler registers for interlaced/progressive output, fills source/destination windows, sets G12A blend scopes, records DMA address/stride/height/width, updates AFBCD modifier/format/stride when needed, resets OSD1 before first enable on GXM/GXL, and marks `osd1_enabled`. Disable resets/disables AFBCD if present and clears OSD1 blend source.

State and persistence: Most hardware programming is staged in `priv->viu` and later committed by the VIU path. Plane-local `enabled` gates first-enable reset. AFBC details persist in `priv->afbcd`. Direct disable writes alter live VPP/OSD blend registers.

Dependencies and integration points: Uses DRM atomic/GEM DMA/fourcc helpers, `meson_osd_afbcd` ops, `meson_viu` reset helper, and register definitions. Modifier support depends on selected SoC compatibility and selected `priv->afbcd.ops`.

Risks: `drm_universal_plane_init()` return is checked but helper/property calls after success are not. AFBC modifier validation relies on bitmask comparison and the plane modifier list. G12A AFBC output stride math supports only currently accepted RGB formats. Interlace scaler handling is complex and should be visually tested.

Test signals: primary plane enumeration, RGB565/RGB888/XRGB/ARGB/XBGR/ABGR linear scanout, AFBC modifier acceptance/rejection on GXBB/GXL/GXM/G12A, alpha replacement behavior, interlaced output field positioning, first-enable reset on GXM/GXL, and disable resetting AFBCD.
