# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_params.h

## Purpose
Defines the canonical i915 module parameter list, `struct i915_params`, GuC enable bit masks, and parameter helper declarations.

## Important APIs, types, and functions
Defines `ENABLE_GUC_SUBMISSION`, `ENABLE_GUC_LOAD_HUC`, `ENABLE_GUC_MASK`, `I915_PARAMS_FOR_EACH(param)`, `struct i915_params`, global `i915_modparams`, and dump/copy/free prototypes.

## Control flow
The macro list is expanded by the implementation to initialize defaults, declare struct members, register parameters, print, copy, and free fields.

## State and persistence
The struct stores persistent module and per-device copied parameter state. Character pointer fields may either reference static defaults or allocated copies depending on copy/free lifecycle.

## Dependencies and integration points
Included broadly by i915 probe, GT, firmware, memory, debugfs, and module code needing parameter values.

## Risks
The macro is a single source of truth; reordering affects struct layout and comments note bools are kept at the end to avoid holes. Mode values control debugfs creation and sysfs behavior.

## Test signals
Build all macro expansion sites and verify default values/permissions appear as expected.
