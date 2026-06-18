# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_mcg/dml2_mcg_dcn42.h

## Purpose
Declares the DCN42 min-clock table builder.

## Important APIs, types, and functions
- `mcg_dcn42_build_min_clock_table(struct dml2_mcg_build_min_clock_table_params_in_out *in_out)`.

## Control flow and integration
The MCG factory includes this header and assigns the function for `dml2_project_dcn42`.

## State and persistence behavior
No header-owned state. The builder mutates the supplied min-clock table through the in/out bundle.

## Dependencies
Includes `dml2_internal_shared_types.h`.

## Risks and edge cases
The header intentionally exposes only the builder. DCN42 behavior differences live entirely in the implementation, so any new DCN42 min-clock policy entry points need explicit additions.

## Test signals
Compile/link coverage through `dml2_mcg_factory.c` and runtime DCN42 min-clock table tests.
