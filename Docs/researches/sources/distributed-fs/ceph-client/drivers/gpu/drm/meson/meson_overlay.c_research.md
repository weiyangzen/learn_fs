# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_overlay.c

Purpose: Implements the Meson video overlay plane backed by the VD1 video path. It supports multiple YUV packed/planar formats plus Amlogic FBC-only YUV420 modifiers, computes crop/scale windows, stages canvas/DMA/AFBC state, and creates the immutable zpos overlay plane.

Important APIs, types, and functions: `struct meson_overlay` wraps `drm_plane` and `meson_drm *priv`. Core callbacks are `meson_overlay_atomic_check()`, `atomic_update()`, `atomic_disable()`, and `format_mod_supported()`. Helpers include `fixed16_to_int()`, `meson_overlay_get_vertical_phase()`, and `meson_overlay_setup_scaler_params()`.

Control flow: atomic check delegates to `drm_atomic_helper_check_plane_state()` with 1/5 to 5x scaling, clipping, and visibility enabled. Atomic update locks `event_lock`, classifies the framebuffer as Amlogic FBC or linear, stages AFBC decode mode/default color/chroma formatting or VD1 IF0 settings, computes scaler and crop scopes, programs format-specific canvas/color-map/chroma subsampling fields, records DMA addresses/strides/heights for up to three planes, computes AFBC header/body addresses, and marks `vd1_enabled`. Disable clears VD1 blend/source registers on G12A or VPP pre/postblend bits on older SoCs.

State and persistence: The plane writes mostly into `priv->viu`, not directly to all hardware registers. This makes atomic update a staging step consumed by the VIU commit path. Direct writes are used for disable. AFBC body/header state is derived from GEM DMA address, pitch, height, modifier layout, and memory-saving/scatter mode.

Dependencies and integration points: Depends on DRM atomic/fb DMA/GEM helpers, Meson VIU/VPP register constants, canvas IDs in `meson_drm`, and the main VIU update path. It is separate from ARM AFBCD primary-plane support; this overlay supports Amlogic FBC modifiers for YUV420-specific video decode paths.

Risks: Crop-axis additions appear easy to confuse because vertical start/end later add `crop_left` and horizontal adds `crop_top`; this deserves regression attention. Interlaced input is explicitly TODO and treated like progressive input. AFBC size math assumes known Amlogic layouts and block sizes. Register staging under `event_lock` requires the consumer path to follow the same locking expectations.

Test signals: atomic scaling/clipping tests, YUYV/NV12/NV21/YUV444/422/420/411/410 scanout, Amlogic FBC basic/scatter with and without memory saving, multi-plane DMA address correctness, interlaced CRTC mode behavior, and disable clearing VD1 on both G12A and legacy VPP paths.
