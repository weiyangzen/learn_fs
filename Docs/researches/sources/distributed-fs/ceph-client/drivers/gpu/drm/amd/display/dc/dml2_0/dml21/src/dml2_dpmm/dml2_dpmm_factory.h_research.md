# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_dpmm/dml2_dpmm_factory.h

## Purpose
Declares the DPMM factory API for project-specific display power management mapping.

## Important APIs, types, and functions
- `dml2_dpmm_create(enum dml2_project_id project_id, struct dml2_dpmm_instance *out)` fills a caller-provided DPMM instance.

## Control flow and integration
The header is included by top-level initialization code that needs to bind DPMM callbacks and by the factory implementation.

## State and persistence behavior
No header-owned state. The declared function mutates `out`.

## Dependencies
Includes `dml2_internal_shared_types.h` and `dml_top_types.h`.

## Risks and edge cases
As with other DML factories, failure details are compressed into a bool. Unsupported projects leave the zeroed callback table unusable.

## Test signals
Compile/link coverage plus runtime creation tests for supported, unsupported, and null-output inputs.
