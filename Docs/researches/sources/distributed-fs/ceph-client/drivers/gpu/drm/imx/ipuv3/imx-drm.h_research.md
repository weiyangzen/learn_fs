# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/imx-drm.h

## Purpose
Defines the private cross-file contract for the i.MX IPUv3 DRM stack, especially the custom CRTC atomic state shared between output encoders and the IPU CRTC.

## Important APIs, types, and functions
- `struct imx_crtc_state` embeds `struct drm_crtc_state` and adds `bus_format`, `bus_flags`, `di_hsync_pin`, and `di_vsync_pin`.
- `to_imx_crtc_state()` converts generic DRM CRTC state to the i.MX extension.
- Externally declares `struct platform_driver ipu_drm_driver`.
- Declares `imx_drm_encoder_parse_of()` for encoder possible-CRTC parsing.
- Declares `ipu_planes_assign_pre()` for the core atomic check.

## Control flow
No runtime control flow exists in the header. Output encoders fill `imx_crtc_state` during atomic checks, and `ipuv3-crtc.c` consumes those fields when configuring the IPU display interface.

## State and persistence
`imx_crtc_state` fields persist per atomic state object and are duplicated/reset/destroyed by the CRTC implementation. They are not global; each modeset carries the selected bus format, bus flags, and DI sync pin mapping.

## Dependencies and integration points
Ties together `imx-drm-core.c`, `ipuv3-crtc.c`, `ipuv3-plane.c`, and output drivers such as HDMI, LDB, TVE, and parallel display. It depends on DRM CRTC state definitions via included users.

## Risks
Any encoder that fails to populate bus format/flags or DI pins can leave the CRTC with zero/default signal configuration. The header's narrow API assumes only the core needs PRE assignment and only output drivers need OF encoder parsing.

## Test signals
Compile coverage catches signature drift. Runtime signals include correct bus format selection for all encoders and CRTC mode programming that reflects each encoder's hsync/vsync pins and bus flags.
