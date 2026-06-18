# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_mcg/dml2_mcg_factory.c

## Purpose
Constructs a `dml2_mcg_instance` and assigns the project-specific min-clock table builder.

## Important APIs, types, and functions
- `dml2_mcg_create()` is the exported factory.
- Stage1 receives a dummy builder that returns true without building a table.
- DCN40, DCN4 stage2, and DCN4 stage2 auto-DRR/SVP use `mcg_dcn4_build_min_clock_table()`.
- DCN42 uses `mcg_dcn42_build_min_clock_table()`.

## Control flow and integration
The function validates `out`, zeroes the instance, switches on project id, fills `build_min_clock_table`, and returns success. Top-level DML initialization uses this instance before core mode-support/DPMM mapping.

## State and persistence behavior
The only persistent state is the callback pointer in `dml2_mcg_instance`. No project id is stored.

## Dependencies
Includes MCG factory, DCN4/DCN42 builder headers, and external library dependencies.

## Risks and edge cases
Stage1 succeeds with a dummy builder, which can leave downstream code with an uninitialized or unchanged min-clock table if it expects real entries. Unsupported/invalid projects return false with zeroed callbacks.

## Test signals
Factory tests should cover null output, invalid id, stage1 dummy behavior, DCN4-family callback assignment, and DCN42 callback assignment.
