<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_step.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_step.h

## Purpose

`xe_step.h` declares the stepping lookup API and a GMD_ID conversion helper.

## Important APIs, Types, and Functions

It exposes `xe_step_platform_get()`, `xe_step_pre_gmdid_get()`, `xe_step_gmdid_get()`, `xe_step_to_gmdid()`, and `xe_step_name()`.

## Control Flow

Device discovery chooses either pre-GMD_ID or GMD_ID path and may call platform-level stepping first. Consumers use `xe_step_name()` for diagnostics and tests.

## State and Persistence Behavior

The APIs write fields in `xe->info.step`; the header owns no state. `xe_step_to_gmdid()` assumes enum values are spaced like GMD_ID stepping values.

## Dependencies and Integration Points

It includes `xe_step_types.h` and Linux types, and is used by device probe, workaround code, and tests.

## Risks and Test Signals

Enum spacing changes would break `xe_step_to_gmdid()`. Compile and KUnit tests should cover the conversion and exported name mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_step.h -->
