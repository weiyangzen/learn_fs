# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_crtc.c

## Purpose
Implements the Amlogic Meson DRM CRTC. It controls vblank enable/disable, atomic CRTC enable/disable/begin/flush, VPP/VIU blender setup, OSD1 and VD1 register commits at vblank, AFBC enable/disable paths, canvas programming, and vblank event delivery.

## Important APIs, types, and functions
- `struct meson_crtc` wraps `drm_crtc` and stores pending vblank event, private driver pointer, SoC-specific enable callbacks, VIU offset, and vblank force/disable flags.
- `meson_crtc_create()` initializes the CRTC with primary plane and SoC-specific helper callbacks.
- `meson_crtc_irq()` is called from the top-level driver IRQ and performs deferred register commits and event handling.
- Helper callbacks include GX/GXL/GXM and G12A atomic enable/disable variants and OSD/VD enable callbacks.

## Control flow
CRTC creation allocates the wrapper, calls `drm_crtc_init_with_planes()`, then selects G12A-specific or legacy helper functions. Atomic enable programs postblend/preblend and output sizes, then turns vblank on. Atomic disable turns vblank off, clears OSD1/VD1 enabled and commit flags, disables legacy postblend paths where applicable, and sends inactive-state events.

Atomic begin steals any pending CRTC event into `meson_crtc->event` after taking a vblank reference. Atomic flush marks OSD1 and VD1 commit flags. On each vblank IRQ, if OSD1 is enabled and committed, the handler writes cached VIU and scaler registers, handles AFBC setup/reset/enable/disable, configures canvas for linear OSD, enables OSD1 blending, and clears the commit flag. If VD1 is enabled and committed, it programs AFBC or canvas state, many VD1/VD2 IF0 and scaler registers, enables VD1, and clears the commit flag. Finally, if vblank is not disabled, it calls `drm_crtc_handle_vblank()` and sends any stored event.

## State and persistence
The CRTC itself stores only event and vblank control flags; most display state persists in `priv->viu` fields prepared by plane/overlay code and consumed in IRQ context. Hardware register state persists in VPP, VIU, AFBC, and canvas blocks. `vsync_forced` keeps vblank enabled while AFBC setup needs IRQ-driven updates.

## Dependencies and integration points
Depends on DRM atomic/vblank helpers, Meson canvas API, Meson VIU/VPP/VENC/RDMA/AFBCD helpers, and `meson_drm` private state. The top-level `meson_irq()` calls `meson_crtc_irq()` after clearing VENC interrupt flags.

## Risks
The IRQ handler writes a large cached register set and assumes `priv->viu` was prepared coherently by atomic plane paths. Event delivery depends on balanced vblank get/put and lock ordering. G12A uses a different VIU offset and blending setup, so SoC detection is critical. AFBC paths force vsync and reset external AFBCD ops, making compressed-buffer transitions sensitive.

## Test signals
Signals include vblank interrupts/events, page flip completion, OSD1/VD1 visibility, AFBC and linear transitions, GXM/G12A behavior, scaler output, canvas IDs, vblank disable/enable behavior, suspend/resume modesets, and absence of missed page-flip events.
