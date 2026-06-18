<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_step_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_step_types.h

## Purpose

`xe_step_types.h` defines the symbolic stepping enum and storage struct used by platform stepping detection.

## Important APIs, Types, and Functions

`struct xe_step_info` stores platform, graphics, media, and base-die stepping bytes. `STEP_NAME_LIST()` enumerates minor steppings A0 through J3 in groups of four to match GMD_ID spacing. `enum xe_step` adds `STEP_NONE`, all symbolic steps, `STEP_FUTURE`, and `STEP_FOREVER`.

## Control Flow

Revision tables initialize `struct xe_step_info` entries using these enum values. `xe_step_gmdid_get()` depends on four-value spacing per major stepping.

## State and Persistence Behavior

The types are embedded in device info and persist for the device lifetime after probe.

## Dependencies and Integration Points

The header depends on Linux types and is consumed by step lookup, platform workaround checks, and diagnostics.

## Risks and Test Signals

Changing list order or spacing would affect GMD_ID conversion and comparison logic. Tests should assert enum ordering, string conversion, and `STEP_FUTURE` capping semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_step_types.h -->
