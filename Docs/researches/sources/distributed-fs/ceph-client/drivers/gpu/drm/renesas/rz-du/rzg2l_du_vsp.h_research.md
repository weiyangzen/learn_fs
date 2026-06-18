# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_vsp.h

## Purpose

`rzg2l_du_vsp.h` declares the RZ/G2L DU to VSP compositor types and function interface.

## Important APIs, Types, and Functions

`struct rzg2l_du_vsp_plane` embeds a DRM plane and stores VSP index/parent. `struct rzg2l_du_vsp` stores index, VSP device, and DU device. `struct rzg2l_du_vsp_plane_state` extends plane state with resolved format metadata. The header exports VSP init, enable/disable, atomic flush, and plane lookup, with `CONFIG_VIDEO_RENESAS_VSP1` stubs returning `-ENXIO` or `ERR_PTR(-ENXIO)`.

## Control Flow

KMS init creates VSP planes before CRTC creation. CRTC and plane callbacks then use the declared functions for display enable and atomic updates.

## State and Persistence Behavior

The header defines persistent VSP/plane structures and per-atomic plane state. No state is allocated by the header.

## Dependencies and Integration Points

It depends on DRM plane types, Linux scatterlist/container helpers, and forward declarations for RZ/G2L DU/CRTC types.

## Risks and Edge Cases

Stub behavior must be handled by KMS init. Include ordering must make `struct rzg2l_du_crtc` visible where inline stubs are used.

## Test Signals

Build with VSP1 enabled and disabled; verify CRTC creation fails cleanly without VSP.
