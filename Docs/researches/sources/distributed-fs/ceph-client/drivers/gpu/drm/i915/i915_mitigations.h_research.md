# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_mitigations.h

## Purpose
Declares the mitigation query used by i915 code that needs to know whether to clear residual GPU state.

## Important APIs, types, and functions
Exports `bool i915_mitigate_clear_residuals(void);`.

## Control flow
No header runtime flow.

## State and persistence
No state in the header; implementation reads the global mitigation bitmask.

## Dependencies and integration points
Included by workaround/context code and by `i915_mitigations.c`.

## Risks
The single-function API hides parsing details and should stay narrow unless more mitigation categories become externally queried.

## Test signals
Build coverage and runtime checks of mitigation-controlled code paths.
