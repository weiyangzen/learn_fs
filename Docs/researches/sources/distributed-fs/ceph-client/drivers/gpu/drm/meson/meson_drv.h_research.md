# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_drv.h

## Purpose
Defines the shared private state and SoC compatibility data for the Amlogic Meson DRM driver.

## Important APIs, types, and functions
- `enum vpu_compatible` distinguishes GXBB, GXL, GXM, and G12A display hardware.
- Encoder indices identify CVBS, HDMI, DSI, and the array limit.
- `struct meson_drm_match_data` carries compatibility and AFBCD ops.
- `struct meson_drm_soc_limits` carries SoC/package limits such as maximum HDMI PHY frequency.
- `struct meson_drm` is the central private object for registers, canvas IDs, DRM objects, encoders, limits, VIU/VENC/RDMA/AFBCD cached state, and helper data.
- `meson_vpu_is_compatible()` is the inline compatibility test.

## Control flow
The only executable code is the inline compatibility comparison. The rest is shared data shape.

## State and persistence
`struct meson_drm` persists for the DRM device lifetime and is the primary state bus between planes, CRTC, encoders, VENC/VPP/VIU/RDMA, and AFBCD helpers. It stores both resource handles and cached register values that are committed later, often in vblank IRQ context.

## Dependencies and integration points
Includes Linux device/OF/regmap types and forward declares DRM and AFBCD structures. Nearly every Meson DRM source includes this header, making it the main internal ABI.

## Risks
The private state is large and tightly coupled; fields such as `viu` cached registers must remain consistent with writer and IRQ consumer code. Adding SoC families requires updating compatibility checks and match data. Because many modules write shared fields, concurrency and atomic commit ordering matter.

## Test signals
Build coverage across all Meson DRM objects catches struct/signature mismatches. Runtime signals include correct SoC-specific paths, AFBCD operations, encoder indexing, VIU/VENC cached state commits, and HDMI PHY limit use.
