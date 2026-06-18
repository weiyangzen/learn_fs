# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/ipuv3-plane.c

## Purpose
Implements IPUv3 DRM primary and overlay planes. It validates framebuffer geometry and IPU memory constraints, assigns optional PRE/PRG resources, configures IDMAC/DMFC/DP channels and CPMEM descriptors, handles separate alpha planes, and performs double-buffered base-address flips.

## Important APIs, types, and functions
- `struct ipu_plane_state` extends DRM plane state with `use_pre`.
- Format lists split all DP-capable formats from RGB-only formats, with optional PRE modifiers for Vivante tiled and super-tiled buffers.
- Public APIs are `ipu_plane_init()`, `ipu_plane_irq()`, `ipu_plane_disable()`, `ipu_plane_disable_deferred()`, `ipu_plane_atomic_update_pending()`, and `ipu_planes_assign_pre()`.
- Address helpers include `drm_plane_state_to_eba()`, `drm_plane_state_to_ubo()`, and `drm_plane_state_to_vbo()`.
- Atomic hooks are `ipu_plane_atomic_check()`, `ipu_plane_atomic_update()`, and `ipu_plane_atomic_disable()`.

## Control flow
Initialization chooses format lists based on whether the plane is attached to a DP flow, enables PRE modifiers when PRG is present, allocates the universal plane, adds zpos/color properties, and obtains IDMAC, optional alpha IDMAC, DMFC, and optional DP resources. Atomic check enforces no scaling, overlay-only positioning, minimum dimensions, EBA alignment, pitch limits, 8-pixel framebuffer width alignment, planar YUV U/V offset constraints, chroma-aligned source offsets, and separate-alpha address/pitch constraints. It forces a CRTC mode change when active plane size, format, pitch, or planar offsets change.

`ipu_planes_assign_pre()` runs during the core atomic check. It first adds affected planes for all affected CRTCs, then assigns scarce PRE channels to tiled buffers as a hard requirement and to eligible linear buffers as an optimization. Atomic update programs DP window/global-alpha state, computes width/height, optionally configures PRG/PRE and substitutes the internal SRAM EBA, updates DP colorspace on color/format changes, fast-paths base flips when no modeset is needed and PRE is not used, otherwise programs DMFC, CPMEM resolution/format/burst/stride/AXI ID/YUV offsets/separate alpha, enables double buffering, locks IDMAC bursts, and enables the plane. Atomic disable disables DP channel early and marks deferred disable for later core commit-tail cleanup.

## State and persistence
Plane objects persist resource handles and a `disabling` flag. Atomic plane state persists `use_pre`. Hardware state persists in IDMAC, CPMEM, DMFC, DP, and PRG/PRE channels. Double-buffered address state is updated in the inactive buffer for fast flips. Separate alpha uses a second IDMAC channel when the DRM format requires it.

## Dependencies and integration points
Depends on IPUv3 IDMAC/DMFC/DP/PRG/PRE APIs, DRM atomic helpers, GEM DMA framebuffer helpers, DRM color properties, and the core commit tail in `imx-drm-core.c` for deferred disables. It provides the vblank IRQ source for the CRTC through `ipu_plane_irq()`.

## Risks
Alignment and offset rules are hardware constraints; relaxing them can hang IDMAC or scan out wrong planes. Active geometry/format changes require a forced modeset so CRTC disable can stop planes safely. PRE assignment is global and scarce; tiled buffers fail if no PRE is available. The fast flip path returns without reprogramming when PRE is used, assuming PRG handles pending updates. Separate alpha paths must keep color and alpha buffers synchronized.

## Test signals
Coverage should include packed RGB, packed YUV, planar YUV, NV12/NV16, separate alpha formats, tiled modifiers with PRG/PRE, linear fallback without PRE, active format/size/pitch changes, chroma-unaligned crop rejection, double-buffered page flips, deferred disable completion, and DP overlay zpos/global-alpha behavior.
