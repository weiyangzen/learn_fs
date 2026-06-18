# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_types.h

## Purpose

`xe_gt_types.h` defines the central `struct xe_gt` and related enums, masks, and conversion helpers for an Xe Graphics Technology unit. It is the shared data contract for GT initialization, topology, power management, GuC/uC, engines, workarounds, steering, user-visible engine availability, OA, and stall tracking.

## Important APIs, Types, and Functions

- `enum xe_gt_type` distinguishes uninitialized, main, and media GTs.
- `enum xe_gt_eu_type` records SIMD8 versus SIMD16 EU mask encoding.
- `XE_MAX_DSS_FUSE_*`, `XE_MAX_EU_FUSE_*`, and `XE_MAX_L3_BANK_MASK_BITS` define topology bitmap widths.
- `xe_dss_mask_t`, `xe_eu_mask_t`, and `xe_l3_bank_mask_t` are fixed-width bitmap types used by topology code and ABI reporting.
- `enum xe_steering_type` classifies MCR steering categories, from L3BANK/DSS/node-specific steering to implicit/default steering.
- `gt_to_tile()` and `gt_to_xe()` are `_Generic` helpers preserving constness.
- `struct xe_gt` aggregates backpointers, hardware identity, MMIO, forcewake, SR-IOV state, register save/restore, reset work, TLB invalidation, CCS mode, USM state, workqueues, `struct xe_uc`, idle state, submission ops, hardware engines, sysfs nodes, MOCS, fuse topology, steering targets, locks, workaround/tuning bitmaps, user engine exposure, OA, and EU stall data.

## Control Flow

This header does not execute runtime logic, but it defines the storage that many init flows progressively populate: device/tile setup creates GTs; topology code fills `fuse_topo`; engine discovery fills `hw_engines`, `eclass`, and engine masks; GuC initialization fills `uc`; power and reset paths use locks/workqueues; sysfs/debug paths read the resulting state.

## State and Persistence Behavior

`struct xe_gt` is long-lived for a GT instance. Many fields are persistent hardware facts (`info`, `fuse_topo`, `mmio`), while others are runtime mutable (`reset.worker`, `tlb_inval`, `uc`, forcewake, workaround bitmaps, user engine masks). The type itself does not enforce locking; individual subsystems document and protect their own fields.

## Dependencies and Integration Points

The header pulls in major subsystem type headers: device, forcewake, idle, SR-IOV PF/VF, stats, hardware engines/fences, OA, register save/restore, suballocation, TLB invalidation, and uC. It is included by most GT, GuC, engine, topology, reset, and debug modules.

## Risks and Edge Cases

Because `struct xe_gt` is broad and shared, field lifetime and locking assumptions are easy to violate. The const-preserving `_Generic` helpers depend on exact pointer types. Topology widths are ABI-relevant; changing them affects bitmap storage and reporting. MCR steering categories must stay synchronized with platform register range tables.

## Test Signals

Build coverage across GT/GuC/engine modules is the primary signal. Structural tests should verify topology bitmap widths, const helper behavior, engine mask/user engine consistency, and reset/power paths that use mutable GT state under the intended locks.
