<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-plane.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-plane.c

Purpose: Implements the i.MX8 DC primary DRM plane, including atomic validation and programming of fetchunit/layerblend/extdst for framebuffer scanout.

Important APIs/types/functions: Public `dc_plane_init()`. Important callbacks are `dc_plane_atomic_check()`, `dc_plane_atomic_update()`, and `dc_plane_atomic_disable()`. Only `DRM_FORMAT_XRGB8888` is advertised.

Control flow: Atomic check permits disable, requires a CRTC for active state, uses DRM helper with no scaling, validates max source dimensions, framebuffer DMA base alignment, pitch range, and pitch alignment. Update computes source size and DMA base, programs fetchunit layerblend, burst length, stride, dimensions, format, frame dimensions, base address, enables source, programs layerblend inputs/mode/position/clock, and sets extdst source to layerblend. Disable turns off fetchunit source and restores extdst source to constframe.

State and persistence behavior: `struct dc_plane` stores fetchunit, constframe, layerblend, and extdst pointers. Atomic update writes volatile hardware registers under `drm_dev_enter()` protection.

Dependencies: DRM atomic/plane helpers, GEM DMA framebuffer address helpers, DC fetchunit and pixel-engine helpers.

Integration points: Created by each CRTC as a primary plane. Its update path is flushed by `dc_crtc_atomic_flush()` through extdst sync.

Risks: No scaling and single-format support simplify validation but limit functionality. Atomic update assumes `new_state->fb` is present. Hardware pitch max is exclusive to 0x10000 boundary as coded.

Test signals: Atomic check rejects unaligned base/pitch, oversized source, scaling attempts, and missing CRTC; page flips show correct framebuffer; disable restores background constframe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-plane.c -->
