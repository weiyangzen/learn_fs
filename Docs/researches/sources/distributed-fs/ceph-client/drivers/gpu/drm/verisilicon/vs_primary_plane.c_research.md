<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_primary_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_primary_plane.c

## Purpose
`vs_primary_plane.c` implements the VeriSilicon primary plane. It validates no-scaling plane state, enables/disables the framebuffer layer, writes format/address/stride/position/size/blend registers, and allocates the primary plane with hardware-supported formats.

## Important APIs, Types, and Functions
The public API is `vs_primary_plane_init()`. Important callbacks are `vs_primary_plane_atomic_check()`, `vs_primary_plane_atomic_enable()`, `vs_primary_plane_atomic_disable()`, `vs_primary_plane_atomic_update()`, and `vs_primary_plane_commit()`.

## Control Flow
Atomic check fetches the new plane and CRTC state and calls `drm_atomic_helper_check_plane_state()` with no scaling and clipping allowed. Enable sets FB enable and display ID bits then commits. Update disables the plane if not visible; otherwise it translates the DRM format, writes color/swizzle/UV fields, computes DMA address, writes address/stride/top-left/bottom-right/size, disables blending, and commits. Init allocates a managed universal primary plane with the format list from chip identity and attaches helper funcs.

## State and Persistence Behavior
Software state is standard DRM plane state. Hardware state persists in FB config, address, stride, geometry, blend, and config-ex commit registers. Framebuffer memory is DMA-backed and remains owned by DRM GEM helpers.

## Dependencies and Integration Points
The file depends on DRM atomic/GEM helper APIs, regmap, `vs_crtc`, `vs_dc`, common plane helpers, and primary-plane register definitions. It is created by `vs_crtc_init()`.

## Risks
`vs_primary_plane_atomic_disable()` sets `FB_EN` instead of clearing it, which looks suspicious for a disable path and should be verified against hardware semantics. Atomic update assumes a non-NULL framebuffer when visible. Blend is always disabled, and only a single primary plane is implemented. Register commits rely on `VSDC_FB_CONFIG_EX_COMMIT` behavior.

## Test Signals
Tests should cover visible and invisible plane updates, disable behavior on hardware/readback, format/swizzle programming, DMA source offsets, pitch programming, clipping without scaling, and supported format advertisement from HWDB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_primary_plane.c -->
