# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_plane.h

## Purpose

`rcar_du_plane.h` declares the R-Car DU plane object, plane-state extension, source enum, hardware/KMS plane capacity constants, and APIs for plane allocation/check/setup.

## Important APIs, Types, and Functions

- `RCAR_DU_NUM_KMS_PLANES` is 9: one primary per CRTC plus up to seven overlays.
- `RCAR_DU_NUM_HW_PLANES` is 8 hardware planes per group.
- `enum rcar_du_plane_source` distinguishes memory scanout, VSPD0 live source, and VSPD1 live source.
- `struct rcar_du_plane` embeds DRM plane and points to its group.
- `struct rcar_du_plane_state` extends DRM plane state with format descriptor, hardware index, source, and colorkey.
- APIs: `rcar_du_atomic_check_planes()`, `__rcar_du_plane_atomic_check()`, `rcar_du_planes_init()`, `__rcar_du_plane_setup()`, and inline `rcar_du_plane_setup()`.

## Control Flow

The header provides the contract between KMS atomic checks, CRTC plane updates, VSP/direct scanout paths, and group-owned plane storage. `rcar_du_plane_setup()` fetches the current driver plane state and delegates to the full setup helper.

## State and Persistence Behavior

Plane state persists across atomic commits through DRM state duplication. `hwindex == -1` indicates no hardware plane is currently allocated, and `source` controls whether scanout comes from memory or VSP live input.

## Dependencies and Integration Points

- Includes DRM plane definitions and forward declares format/group types.
- Included by group, CRTC, KMS, VSP, and plane implementation code.

## Risks and Edge Cases

- The capacity constants encode hardware assumptions; changing group layout or overlay policy requires allocator and init changes.
- `colorkey` is an unsigned int with packed enable/RGB semantics defined in the C file, so external users need the property documentation from KMS/plane code.

## Test Signals

- Atomic state duplication/reset tests should verify `hwindex`, `source`, and `colorkey` defaults and persistence.
- Capacity tests should verify plane creation never exceeds group array bounds.
