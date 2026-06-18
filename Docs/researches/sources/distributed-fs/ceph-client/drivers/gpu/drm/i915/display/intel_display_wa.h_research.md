# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_wa.h

## Purpose
This header defines the display workaround ID namespace and exposes helpers to apply or query workaround policy.

## Important APIs, Types, and Functions
It declares `intel_display_wa_apply()`, `__intel_display_wa()`, and the user-facing macro `intel_display_wa(display, wa)`, which passes the enum value and stringified name. `enum intel_display_wa` lists sorted workaround IDs such as `INTEL_DISPLAY_WA_1409120013`, `INTEL_DISPLAY_WA_16025573575`, and `INTEL_DISPLAY_WA_22021048059`. `intel_display_needs_wa_16023588340()` is provided as an inline false stub for i915 builds and an external declaration otherwise.

## Control Flow
The header has no runtime logic beyond the macro and i915 conditional stub. The enum comment establishes the maintenance contract that each enum entry must have a matching switch case in `__intel_display_wa()`.

## State and Persistence Behavior
No state is stored here. The enum values are stable identifiers used as predicates across the driver.

## Dependencies and Integration Points
It includes Linux types and forward-declares `struct intel_display`. It integrates with display feature paths that need platform-specific workaround checks and with init code that applies global workaround registers.

## Risks
Adding an enum without updating the implementation produces runtime warnings and false predicates. Renumbering is less visible because callers use names, but ordering by lineage helps audits. The i915 versus Xe difference for WA 16023588340 must remain intentional.

## Test Signals
Build coverage for i915 and non-i915 configurations, no missing-WA warnings, and targeted platform stepping tests for each workaround predicate are primary signals.
