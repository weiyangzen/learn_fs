# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_dcn42.h

## Purpose
Declares DCN42-specific PMO initialization and p-state support test functions.

## Important APIs, types, and functions
- Forward declares `struct dml2_pmo_initialize_in_out` and `struct dml2_pmo_test_for_pstate_support_in_out`.
- Exports `pmo_dcn42_initialize()` and `pmo_dcn42_test_for_pstate_support()`.

## Control flow and integration
The header is intended for factory or project-specific PMO wiring. In the researched factory, the DCN42 project currently uses DCN4 FAMS2 callbacks instead of these declarations, so integration should be verified before relying on them.

## State and persistence behavior
No header-owned state. Declared functions mutate/read `dml2_pmo_instance` through their in/out bundles.

## Dependencies
Includes `dml2_internal_shared_types.h`.

## Risks and edge cases
Forward declarations keep the header narrow but can hide mismatches until implementation compile time. The apparent lack of factory wiring is the main integration risk.

## Test signals
Compile/link coverage if factory wiring is added, plus direct DCN42 PMO policy tests described for the implementation.
