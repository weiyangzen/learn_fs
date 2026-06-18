# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_utils.h

## Purpose
This header exposes small display utility macros and environment helper declarations used across display code.

## Important APIs, Types, and Functions
`MISSING_CASE(x)` emits a warning for unhandled enum/switch values. `fetch_and_zero(ptr)` atomically at C-expression level reads a value, stores zero back to the pointed object, and returns the old value. `KHz(x)` and `MHz(x)` are unit-conversion macros. It declares `intel_display_run_as_guest()` and `intel_display_vtd_active()`.

## Control Flow
The macros expand inline at call sites. `fetch_and_zero()` uses a GNU statement expression and `typeof` to preserve the pointed type.

## State and Persistence Behavior
The only state mutation is from `fetch_and_zero()`, which clears the caller-provided object. It is not an atomic CPU operation and relies on caller synchronization.

## Dependencies and Integration Points
It includes Linux bug/types headers and forward-declares `struct intel_display`. It is used by reset code and general display code for warnings, unit conversions, clear-on-fetch ownership transfers, and environment queries.

## Risks
`fetch_and_zero()` can be mistaken for atomic synchronization; it is only safe when the caller controls concurrent access. `KHz`/`MHz` are simple multiplication macros and can overflow if used with large values or side-effect expressions. `MISSING_CASE` warns but does not enforce recovery.

## Test Signals
Build coverage, warning paths for unexpected enum values, reset cleanup paths using `fetch_and_zero()`, and unit-sensitive clock calculations are useful signals.
