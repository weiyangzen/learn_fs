# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/ipuv3-crtc.c

## Purpose
Implements IPUv3 DRM CRTC components. It binds IPU display-interface/DC resources, creates the primary and optional overlay planes, programs display timing and DI signal configuration, handles vblank/page-flip events, and controls IPU/DC/DI/PRG enable sequencing.

## Important APIs, types, and functions
- `struct ipu_crtc` embeds `struct drm_crtc`, stores full and partial planes, IPU DC/DI handles, EOF IRQ, and pending vblank event.
- CRTC state management uses `imx_drm_crtc_reset()`, `imx_drm_crtc_duplicate_state()`, and `imx_drm_crtc_destroy_state()` for `struct imx_crtc_state`.
- Atomic helper callbacks include `ipu_crtc_mode_fixup()`, `ipu_crtc_mode_set_nofb()`, `ipu_crtc_atomic_check()`, `ipu_crtc_atomic_begin()`, `ipu_crtc_atomic_flush()`, `ipu_crtc_atomic_enable()`, and `ipu_crtc_atomic_disable()`.
- Resource/component functions include `ipu_get_resources()`, `ipu_put_resources()`, `ipu_drm_bind()`, `ipu_drm_probe()`, and exported `ipu_drm_driver`.

## Control flow
Component bind creates a primary IPU plane for the platform DMA channel, allocates a CRTC with that plane, stores the DI OF port, attaches helper funcs, obtains DC and DI resources from the parent IPU, optionally creates a DP foreground overlay plane, and registers the primary plane EOF IRQ disabled.

Mode fixup converts DRM mode to videomode, asks the IPU DI to adjust it, rejects zero sync lengths, and converts back. Mode set gathers attached encoder types to choose DI clocking mode, consumes bus format/flags and sync pins from `imx_crtc_state`, aligns hactive to 8 pixels by shrinking front porch if necessary, initializes DC sync and DI panel timing. Atomic enable turns on PRG, DC, DC channel, and DI. Atomic disable shuts down DC channel and DI, disables planes before removing the DC clock, disables DC and PRG, turns vblank off, and sends pending events if the CRTC is inactive.

Vblank enable/disable toggles the EOF IRQ. The IRQ handler calls `drm_crtc_handle_vblank()` and, when a page-flip event is pending, waits until all associated planes report no pending update before sending the event and dropping the vblank reference.

## State and persistence
`ipu_crtc` persists for the component lifetime and owns IPU DC/DI resource handles. Atomic CRTC state persists bus format, bus flags, and sync pins supplied by encoders. Pending page-flip event state lives in `ipu_crtc->event` until the EOF handler completes it.

## Dependencies and integration points
Depends on `video/imx-ipu-v3.h` APIs for DC, DI, PRG, and IDMAC resources, DRM vblank/event helpers, component framework, and `ipuv3-plane.c` for plane creation and pending-update checks. The platform data supplies DI/DC/DMA channel numbers and OF node identity.

## Risks
Disable ordering is safety-critical: planes must be disabled before DC clocks are removed to avoid undefined IDMAC/IPU state. Hactive alignment mutates timing and can underflow front porch on marginal modes. Event completion depends on plane pending checks, especially when PRE/PRG is used. `ipu_enable_vblank()` unconditionally enables an IRQ requested with `IRQF_NO_AUTOEN`, so mismatched disable counts would warn.

## Test signals
Validation includes modes needing DI adjustment, invalid zero sync lengths, DAC/LVDS/TVDAC/HDMI clock-flag selection, hactive alignment warnings, vblank enable/disable, page-flip event completion with PRE and non-PRE planes, overlay creation only when DP flow is available, and shutdown with active scanout.
