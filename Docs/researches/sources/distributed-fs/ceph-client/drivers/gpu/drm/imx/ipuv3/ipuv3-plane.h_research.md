# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/ipuv3-plane.h

## Purpose
Declares the IPUv3 DRM plane object and the plane APIs used by the CRTC and DRM core.

## Important APIs, types, and functions
- `struct ipu_plane` embeds `struct drm_plane` and stores IPU, IDMAC, alpha IDMAC, DMFC, DP flow, DMA channel number, and deferred-disable state.
- Declares `ipu_plane_init()`, `ipu_plane_irq()`, `ipu_plane_disable()`, `ipu_plane_disable_deferred()`, and `ipu_plane_atomic_update_pending()`.
- A legacy `ipu_plane_mode_set()` prototype remains declared even though this atomic implementation uses atomic update paths instead.

## Control flow
No runtime control flow exists here. The header defines ownership and callable entry points: CRTC creation calls `ipu_plane_init()`, CRTC IRQ setup calls `ipu_plane_irq()`, CRTC disable/commit-tail use disable helpers, and IRQ event completion uses `ipu_plane_atomic_update_pending()`.

## State and persistence
`struct ipu_plane` persists all hardware resource handles for a plane and the `disabling` flag that bridges atomic plane disable to deferred hardware shutdown after flip completion.

## Dependencies and integration points
Depends on DRM CRTC/plane types and forward declarations for IPUv3 resources. It is included by `imx-drm-core.c`, `ipuv3-crtc.c`, and `ipuv3-plane.c`.

## Risks
The header exposes internal resource fields, so other files can couple to implementation details. The stale-looking `ipu_plane_mode_set()` declaration can confuse readers and should be checked before any refactor.

## Test signals
Compile coverage catches API drift. Runtime signals are correct CRTC access to plane IRQs, pending-update checks, and deferred disable behavior.
