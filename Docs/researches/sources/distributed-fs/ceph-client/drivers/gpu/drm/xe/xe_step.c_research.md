<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_step.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_step.c

## Purpose

`xe_step.c` maps PCI revision IDs and GMD_ID register revision fields to Xe symbolic graphics/media/platform/base-die steppings.

## Important APIs, Types, and Functions

Static revision tables cover Tiger Lake, DG1, Alder Lake variants, DG2 subplatforms, and PVC. `xe_step_platform_get()` sets platform stepping for platforms that need it. `xe_step_pre_gmdid_get()` maps legacy PCI revids and PVC base-die IDs. `xe_step_gmdid_get()` maps graphics/media GMD_ID revid fields directly. `xe_step_name()` converts enum values to strings and is exported for KUnit.

## Control Flow

For pre-GMD_ID platforms, the function selects a table based on platform/subplatform, splits PVC revid into base ID and die revid, looks up steppings, warns on gaps, advances to the next known revid when possible, and falls back to `STEP_FUTURE` if the value is beyond the table. GMD_ID platforms use `STEP_A0 + revid`, capped at `STEP_FUTURE`.

## State and Persistence Behavior

The functions write `xe->info.step.platform`, `graphics`, `media`, and `basedie`. These persist in device info and drive platform workaround checks.

## Dependencies and Integration Points

The file depends on platform/subplatform definitions, DRM logging, bitfield helpers, and KUnit visibility. It is called during PCI/device discovery before workaround and feature gating.

## Risks and Test Signals

Risks include missing new revid mappings, table holes producing conservative but possibly wrong steppings, and PVC base-die misclassification. Tests should exercise known table entries, gaps, future values, GMD_ID capping, PVC split fields, and `xe_step_name()` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_step.c -->
