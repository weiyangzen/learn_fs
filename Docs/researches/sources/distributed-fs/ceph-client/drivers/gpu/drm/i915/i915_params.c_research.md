# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_params.c

## Purpose
Defines i915 module parameters, their descriptions and permissions, dynamic debug class mapping, and helper routines to dump/copy/free parameter sets.

## Important APIs, types, and functions
Defines global `i915_modparams` from `I915_PARAMS_FOR_EACH`. Registers parameters such as `modeset`, `reset`, `error_capture`, `enable_hangcheck`, `force_probe`, `memtest`, `mmio_debug`, `enable_guc`, firmware paths, GVT, request timeout, LMEM sizes, and debug-only API. Public helpers are `i915_params_dump()`, `i915_params_copy()`, and `i915_params_free()`.

## Control flow
Macro wrappers register safe and unsafe module params with sysfs permissions and descriptions. Dumping uses `_Generic` to choose type-specific printing. Copying performs a struct copy then duplicates `char *` members; freeing releases only allocated `char *` members and nulls them.

## State and persistence
`i915_modparams __read_mostly` persists module-wide. Copied parameter structs may own duplicated string members and must be released with `i915_params_free()`.

## Dependencies and integration points
Depends on Linux module parameter APIs, DRM printing, dynamic debug class maps, Kconfig feature guards, and consumers throughout driver probe, GT firmware loading, reset, hangcheck, memory sizing, and debugfs.

## Risks
Permissions are ABI-sensitive; comments require most sysfs params to stay read-only, with runtime changes through debugfs. Unsafe params may change without full synchronization. String copy/free ownership must be respected to avoid leaks or double frees. Defaults in the header macro and module_param declarations must stay aligned.

## Test signals
Inspect `/sys/module/i915/parameters`, dump params in driver logs/debugfs, load with custom GuC paths, force_probe, reset, LMEM sizes, and invalid values; run Kconfig combinations for optional params.
