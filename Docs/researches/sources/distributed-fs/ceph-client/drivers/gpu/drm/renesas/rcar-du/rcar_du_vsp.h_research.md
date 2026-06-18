# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_vsp.h

## Purpose

`rcar_du_vsp.h` declares the R-Car DU to VSP compositor interface and the DRM plane/private-state structures used by the implementation.

## Important APIs, Types, and Functions

`struct rcar_du_vsp_plane` embeds a `drm_plane`, a parent `rcar_du_vsp *`, and a VSP input index. `struct rcar_du_vsp` stores the VSP index, supplier device, DU device, optional `device_link`, plane array, and plane count. `struct rcar_du_vsp_plane_state` extends `drm_plane_state` with resolved format metadata and up to three SG tables. The header exports conversion helpers and the init/enable/disable/atomic/map/unmap functions, with stubs when `CONFIG_VIDEO_RENESAS_VSP1` is disabled.

## Control Flow

Consumers call `rcar_du_vsp_init()` while building KMS objects, then CRTC code calls enable/disable and atomic begin/flush around DU commits. Plane helpers use the private state to carry map results from prepare to cleanup and format results from atomic check to update.

## State and Persistence Behavior

The header defines lifetime ownership: VSP data lives under the DU device, plane state is duplicated/destroyed through DRM atomic state, and SG tables are valid only for the prepared framebuffer state.

## Dependencies and Integration Points

It depends on DRM planes, Linux scatterlists, forward-declared R-Car DU types, and `media/vsp1.h` structures exposed in function signatures. Optional stubs let the rest of the DU code compile without VSP1 but make initialization return `-ENXIO`.

## Risks and Edge Cases

- The fixed `sg_tables[3]` array must match supported framebuffer plane counts.
- Stub behavior means callers must treat `-ENXIO` as a real missing-compositor failure.
- The header exposes internal structures to multiple DU files, so layout changes require coordinated updates.

## Test Signals

Compilation with and without `CONFIG_VIDEO_RENESAS_VSP1`, atomic state duplication tests, and framebuffer map/unmap lifecycle testing are the primary signals.
