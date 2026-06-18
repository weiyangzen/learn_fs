# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_topology.h

## Purpose

`xe_gt_topology.h` exposes the GT topology initialization and query interface. It also defines the canonical DSS iteration macro that combines geometry and compute DSS masks.

## Important APIs, Types, and Functions

- `for_each_dss(dss, gt)` iterates set bits in the OR of `gt->fuse_topo.g_dss_mask` and `gt->fuse_topo.c_dss_mask`.
- `xe_gt_topology_init()` fills `gt->fuse_topo`.
- `xe_gt_topology_dump()` prints cached topology through a `drm_printer`.
- `xe_gt_topology_mask_last_dss()` returns `find_last_bit()` or `XE_MAX_DSS_FUSE_BITS` for an empty mask.
- `xe_dss_mask_group_ffs()` and `xe_l3_bank_mask_ffs()` find first set DSS/L3 entries.
- `xe_gt_topology_has_dss_in_quadrant()`, `xe_gt_has_geometry_dss()`, `xe_gt_has_compute_dss()`, `xe_gt_has_discontiguous_dss_groups()`, and `xe_gt_topology_report_l3()` provide higher-level queries.

## Control Flow

The header is declarative apart from inline helpers. Its control-flow contract is that callers initialize topology once with `xe_gt_topology_init()` before iterating or querying masks. `for_each_dss()` relies on Linux bitmap OR iteration and the fixed `XE_MAX_DSS_FUSE_BITS` width defined in `xe_gt_types.h`.

## State and Persistence Behavior

No state is stored in the header. It exposes access to persistent masks held by `struct xe_gt`. Callers that cache results must account for the fact that this interface does not provide invalidation or re-read hooks.

## Dependencies and Integration Points

It includes `xe_gt_types.h` for `struct xe_gt`, mask typedefs, and topology widths. The API is used by topology initialization, MCR steering, engine/CCS configuration, debug dumping, and code that needs to know whether an individual DSS exists for geometry or compute.

## Risks and Edge Cases

`for_each_dss()` intentionally iterates DSS available to either geometry or compute; callers needing only one domain must use `xe_gt_has_geometry_dss()` or `xe_gt_has_compute_dss()`. `xe_gt_topology_mask_last_dss()` returns the bitmap size for empty masks, which callers must not treat as a valid DSS index.

## Test Signals

Compile coverage catches signature drift. Unit tests should cover empty masks, combined geometry/compute iteration, and the distinction between any-DSS iteration and per-domain queries.
