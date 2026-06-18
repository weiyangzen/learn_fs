# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_topology.c

## Purpose

`xe_gt_topology.c` discovers and reports the fused hardware topology for an Xe GT. It reads DSS geometry/compute masks, EU mask/type, and L3 bank masks from platform-specific fuse registers, stores the normalized values in `gt->fuse_topo`, and provides query helpers used by steering, engine enablement, userspace topology reporting, and debug output.

## Important APIs, Types, and Functions

- `xe_gt_topology_init()` is the initialization entry point. It loads geometry and compute DSS masks, EU mask/type, L3 bank mask, then dumps the result through the GT debug printer.
- `load_dss_mask()` reads one or more 32-bit fuse registers and converts them into `xe_dss_mask_t`.
- `load_eu_mask()` normalizes EU enable bits across pre-Xe_HP inverted semantics and SIMD8/SIMD16 encodings.
- `load_l3_bank_mask()` translates platform-specific L3 fuse layouts into `xe_l3_bank_mask_t`.
- `gen_l3_mask_from_pattern()` expands per-node/per-mask-bit patterns according to an enable mask.
- Query helpers include `xe_gt_topology_report_l3()`, `xe_gt_topology_dump()`, `xe_dss_mask_group_ffs()`, `xe_l3_bank_mask_ffs()`, `xe_gt_topology_has_dss_in_quadrant()`, `xe_gt_has_geometry_dss()`, `xe_gt_has_compute_dss()`, and `xe_gt_has_discontiguous_dss_groups()`.

## Control Flow

Initialization begins with fixed arrays of geometry and compute fuse registers. The function asserts that GT metadata does not request more registers than the arrays provide, reads the requested register count, and converts the raw arrays into bitmaps. EU loading reads `XELP_EU_ENABLE`, adjusts bit polarity for older platforms, expands SIMD8 encoding when one bit represents two EUs, and records `XE_GT_EU_TYPE_SIMD8` or `XE_GT_EU_TYPE_SIMD16`. L3 loading first suppresses media-GT L3 reporting on Xe3+ where the media mask is known unreliable, then handles Xe3.5+, Xe3, Xe2, Xe_HP/Xe_HPC/PVC/DG2, and older inverted one-bit-per-bank formats.

## State and Persistence Behavior

The file writes persistent topology state into `struct xe_gt::fuse_topo`. The masks are cached for later driver decisions and reporting; there is no allocation, reference counting, or delayed work. It assumes GT MMIO is readable during init and does not refresh topology after initialization.

## Dependencies and Integration Points

It depends on GT MMIO access, platform version macros, register definitions, bitmap helpers, MCR steering iteration, GT assertions, and workaround metadata. Consumers include topology dump/reporting paths, CCS quadrant enablement, MCR steering selection, L3 topology ABI reporting, and tests or debugfs that inspect GT topology.

## Risks and Edge Cases

The platform-specific L3 normalization is easy to break when register definitions change. The DSS quadrant helper divides by four based on the larger geometry/compute fuse-register span, so malformed metadata can produce misleading quadrant decisions. Media GT L3 reporting is ABI-sensitive because pre-Xe3 behavior is preserved even though values may be bogus. `xe_gt_has_*_dss()` trusts callers not to query beyond the bitmap width.

## Test Signals

Useful tests mock fuse register values for each platform branch, verify SIMD8 expansion and SIMD16 direct mapping, assert media GT L3 suppression on Xe3+, cover empty DSS and L3 masks, and check quadrant/discontiguous helpers against synthetic masks. Runtime signals include debug topology dumps and userspace topology queries matching expected fuse data.
