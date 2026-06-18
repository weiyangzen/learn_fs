# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_group.h

## Purpose

`rcar_du_group.h` defines the semi-global DU group object and APIs for group register access, reference management, start/stop/restart, routing, and DPAD/VSP routing updates.

## Important APIs, Types, and Functions

- `struct rcar_du_group` stores DU device pointer, MMIO offset, group index, channel/CMM masks, CRTC counts, use counters, DPTSR lock/state, plane array, and restart flag.
- APIs: `rcar_du_group_read()`, `rcar_du_group_write()`, `rcar_du_group_get()`, `rcar_du_group_put()`, `rcar_du_group_start_stop()`, `rcar_du_group_restart()`, `rcar_du_group_set_routing()`, and `rcar_du_set_dpad0_vsp1_routing()`.

## Control Flow

The header provides the cross-file contract used by KMS setup, CRTC lifecycle, and plane source switching. The group lock protects `dptsr_planes` and DPTSR register updates.

## State and Persistence Behavior

Group objects persist for the DRM device lifetime. `use_count` controls one-time setup, `used_crtcs` controls hardware start/stop, and `need_restart` communicates plane/source changes that require a group restart.

## Dependencies and Integration Points

- Includes `rcar_du_plane.h` because groups own the plane array.
- Used by CRTC, KMS, plane, and group implementation files.

## Risks and Edge Cases

- Counter fields require disciplined caller pairing under mode-config locking; the header cannot enforce this.
- Plane array capacity is fixed at `RCAR_DU_NUM_KMS_PLANES`; setup must keep `num_planes` within that bound.

## Test Signals

- Lockdep and atomic tests should verify DPTSR updates are serialized and restart flags are consumed exactly once.
