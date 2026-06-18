# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/display_mode_util.h

## Purpose
`display_mode_util.h` declares the legacy DML utility surface for math helpers, format classifiers, debug dump functions, and pipe/plane mapping helpers.

## Important APIs, types, and functions
It exports arithmetic helpers, `dml_util_is_420()`, `dml_is_vertical_rotation()`, cursor bpp conversion, print helpers for DML register/config/support/bounding-box structures, active plane/pipe counters, `dml_get_plane_idx()`, `dml_get_pipe_idx()`, and `dml_calc_pipe_plane_mapping()`.

## Control flow
The header has no control flow. It groups utility prototypes behind `__DML_DLL_EXPORT__` so the same signatures can be shared by standalone/tool and in-driver builds.

## State and persistence behavior
The header defines no state. Function implementations operate on caller-owned in-memory DML structures and logging callbacks.

## Dependencies and integration points
It includes `display_mode_core_structs.h`, `cmntypes.h`, `dml_assert.h`, and `dml_logging.h`. It is a low-level dependency for calculation code and debug consumers.

## Risks and edge cases
Because it exposes debug routines for many structure types, any schema change in `display_mode_core_structs.h` may require prototype or implementation updates. Callers must pass valid plane counts and pipe indices; the utility contract does not encode bounds in types.

## Test signals
Build coverage across standalone and kernel-style inclusion, function-level regression tests for math/mapping helpers, and debug dump smoke tests are the main signals.
