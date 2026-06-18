# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_dcn3.h

## Purpose
Declares the DCN3 PMO callback set used by the PMO factory for DCN40/DCN4 stage2 projects.

## Important APIs, types, and functions
Exports initialization, DCC/MCACHE optimization, vmin init/test/optimize, and p-state init/test/optimize functions. All use in/out bundles from `dml2_internal_shared_types.h`.

## Control flow and integration
The PMO factory assigns these functions into `dml2_pmo_instance` callbacks. The top-level optimizer calls the init/test/optimize triples during staged optimization loops.

## State and persistence behavior
No header-owned state. The functions mutate PMO instance scratch and optimized display configuration outputs.

## Dependencies
Includes `dml2_internal_shared_types.h`.

## Risks and edge cases
The header exposes only UCLK p-state callback names; factory users map them to `init_for_uclk_pstate`/`test_for_uclk_pstate`/`optimize_for_uclk_pstate`. Any FCLK/stutter extension would require new declarations or reuse of generic callback slots.

## Test signals
Compile/link coverage through `dml2_pmo_factory.c` plus runtime tests for each callback family described in the implementation.
