# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_factory.c

## Purpose
Constructs a `dml2_core_instance` by project id and wires the correct DCN4/DCN42 implementation callbacks. It is the dispatch boundary between project selection in the top layer and core mode-support/mode-programming code.

## Important APIs, types, and functions
- `dml2_core_create(enum dml2_project_id project_id, struct dml2_core_instance *out)` is the only exported function.
- For `dml2_project_dcn40`, `dml2_project_dcn4x_stage2`, and `dml2_project_dcn4x_stage2_auto_drr_svp`, it selects `core_dcn4_initialize`, `core_dcn4_mode_support`, `core_dcn4_mode_programming`, `core_dcn4_populate_informative`, and `core_dcn4_calculate_mcache_allocation`.
- For `dml2_project_dcn42`, it swaps only initialization to `core_dcn42_initialize` while reusing the DCN4 support/programming/populate/MCACHE hooks.
- `dml2_project_dcn4x_stage1` explicitly returns false; invalid/default ids also fail.

## Control flow and integration
The function validates `out`, zeroes the instance with `memset`, records the project id, then fills callback slots based on a switch. The resulting instance is consumed by DML top-level initialization and later invoked through function pointers.

## State and persistence behavior
The only persistent state initialized here is the function table and `project_id` inside `dml2_core_instance`. Previous contents of `out` are intentionally discarded. No heap allocation or external registration occurs.

## Dependencies
Depends on `dml2_core_factory.h`, `dml2_core_dcn4.h` for implementation symbols, and `dml2_external_lib_deps.h` for `memset`/bool support.

## Risks and edge cases
Callers must check the boolean result before using callback pointers. Stage1 returns false without dummy callbacks, so treating zeroed callbacks as usable would crash. DCN42 shares DCN4 core algorithms after DCN42-specific initialization, so changes to shared DCN4 algorithms also affect DCN42 behavior.

## Test signals
Factory tests should cover null output, invalid project id, unsupported stage1, DCN40/stage2/stage2_auto_drr_svp callback identity, and DCN42 initialization callback identity. A smoke test should invoke `initialize` after creation for each supported project.
