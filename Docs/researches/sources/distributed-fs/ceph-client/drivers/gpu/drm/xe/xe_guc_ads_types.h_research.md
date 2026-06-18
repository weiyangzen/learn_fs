# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_ads_types.h

## Purpose

`xe_guc_ads_types.h` defines the small persistent state object for GuC ADS allocation and sizing.

## Important APIs, Types, and Functions

- `struct xe_guc_ads::bo` points to the pinned BO containing the ADS blob.
- `golden_lrc_size` stores total page-aligned golden context storage needed for enabled engine classes.
- `regset_size` stores MMIO save/restore regset bytes.
- `ads_waklv_size` stores workaround KLV region size.
- `capture_size` stores GuC capture-list input storage size.

## Control Flow

The type is filled by `xe_guc_ads_init()` and recalculated by `xe_guc_ads_init_post_hwconfig()`. Population code uses these fields to compute ADS region offsets.

## State and Persistence Behavior

All fields are persistent for the GuC object lifetime. Size fields represent current platform/engine assumptions and are consumed by offset helpers each time the ADS is populated.

## Dependencies and Integration Points

The type forward-declares `struct xe_bo` and is embedded in `struct xe_guc`. It bridges GuC lifecycle code and ADS layout code without exposing GuC ABI internals.

## Risks and Edge Cases

If size fields are stale after hwconfig changes, later population may write incorrect offsets. `bo` must be valid before any populate call. `regset_size` and `capture_size` must be large enough for dynamic MCR/capture content.

## Test Signals

Tests should verify sizes before and after hwconfig, valid BO allocation, and consistency between size fields and populated ADS offsets.
