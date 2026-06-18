# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_mcg/dml2_mcg_factory.h

## Purpose
Declares the MCG factory API.

## Important APIs, types, and functions
- `dml2_mcg_create(enum dml2_project_id project_id, struct dml2_mcg_instance *out)`.

## Control flow and integration
Top-level DML setup includes this header to create the min-clock generator instance before building min-clock tables used by core and DPMM.

## State and persistence behavior
No header-owned state; the declared function writes the callback table into `out`.

## Dependencies
Includes `dml2_internal_shared_types.h` and `dml_top_types.h`.

## Risks and edge cases
Factory failure is boolean-only. Consumers must not call the callback unless creation succeeds and the callback is non-null.

## Test signals
Compile/link coverage and factory runtime tests for supported/unsupported project ids.
