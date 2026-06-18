# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_debugfs_params.c

## Purpose
`intel_display_debugfs_params.c` creates a debugfs directory exposing display module parameters for inspection and, when permitted by mode bits, mutation. It provides typed file operations for display params that are not handled by generic debugfs helpers.

## Important APIs, Types, And Functions
The public API is `intel_display_debugfs_params(struct intel_display *display)`. Internal helpers implement integer and unsigned-integer seq-file show/open/write paths: `intel_display_param_int_show/open/write()` and `intel_display_param_uint_show/open/write()`. `intel_display_debugfs_create_int()` and `intel_display_debugfs_create_uint()` select read-only or read-write file operations based on mode. `_intel_display_param_create_file()` uses C11 `_Generic` to dispatch `bool *`, `int *`, `unsigned int *`, `unsigned long *`, and `char **` values to the right debugfs creation routine.

## Control Flow And State
The function builds a directory named `<driver_name>_params` under the DRM debugfs root, reusing it if it already exists. It iterates `INTEL_DISPLAY_PARAMS_FOR_EACH(REGISTER)` and creates a file for each parameter with a nonzero mode. Writes parse integers or unsigned integers first and fall back to boolean parsing, allowing common boolean values for numeric toggles. The persistent state is `display->params`; debugfs writes mutate that in-memory parameter struct and affect subsequent display logic that consults those params.

## Dependencies And Integration Points
This file depends on `intel_display_params.h` for the parameter list and metadata, `intel_display_core.h` for `display->params`, and Linux debugfs/seq-file helpers. It is called by global display debugfs registration after other display debugfs files are created.

## Risks And Test Signals
Risks include unsafe debugfs lifetime if files outlive `display`, unvalidated parameter changes that affect active hardware paths, and type mismatches in the `_Generic` dispatch if a new parameter type is added. The use of `debugfs_create_file_unsafe()` is acceptable only because debugfs lifetime is tied to driver/device teardown. Test signals include reading every param file, writing allowed params, confirming read-only modes reject writes, checking boolean fallback for numeric params, and building after adding new parameter types.
