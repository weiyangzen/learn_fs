# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_mcg/dml2_mcg_dcn4.h

## Purpose
Declares the DCN4 MCG min-clock table builder and a unit-test hook.

## Important APIs, types, and functions
- `mcg_dcn4_build_min_clock_table()` fills a `dml2_mcg_min_clock_table` from SoC bounding-box data.
- `mcg_dcn4_unit_test()` is declared but not implemented in the researched file set, suggesting a legacy or external test hook.

## Control flow and integration
The MCG factory wires `mcg_dcn4_build_min_clock_table()` for DCN40 and DCN4 stage2 variants. The unit-test declaration is not used in the nearby source files inspected.

## State and persistence behavior
No header-owned state. The builder mutates its in/out parameter bundle.

## Dependencies
Includes `dml2_internal_shared_types.h` for MCG parameter and table structures.

## Risks and edge cases
The declared `mcg_dcn4_unit_test()` can cause link failures if referenced without an implementation. Keep declaration/implementation status in sync if adding automated tests.

## Test signals
Compile/link tests should ensure the factory-visible builder resolves. Dedicated MCG tests should target the implementation behavior from `dml2_mcg_dcn4.c`.
