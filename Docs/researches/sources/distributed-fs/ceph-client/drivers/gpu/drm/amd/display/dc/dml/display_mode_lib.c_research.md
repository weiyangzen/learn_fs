# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_mode_lib.c

## Purpose
This file is the generation dispatch and logging core for DML. It binds `display_mode_lib` instances to the correct generation-specific validate/recalculate/RQ/DLG functions, maps validation statuses to messages, and provides verbose logging for pipe inputs and mode-support results.

## Important APIs, Types, And Functions
Static `dml_funcs` tables exist for DML20, DML20v2, DML21, DML30, DML31, DML314, and DML32. `dml_init_instance()` copies SoC/IP bounding boxes into a `display_mode_lib`, stores the project enum, and selects the function table. `dml_get_status_message()` translates selected `dm_validation_status` values. `dml_log_pipe_params()` prints source, destination, scaler, output, and clock config for each pipe. `dml_log_mode_support_params()` prints per-voltage-state support booleans from `mode_lib->vba`.

## Control Flow And State
Initialization is a switch on `enum dml_project`; most projects use legacy `rq_dlg_get_*` callbacks, while `DML_PROJECT_DCN32` binds `rq_dlg_get_*_v2` because DCN32 requires multi-pipe arguments. Logging loops over provided pipe count or `vba.soc.num_states` and emits `dml_print()` diagnostics.

## State And Persistence Behavior
`dml_init_instance()` mutates the caller-owned `display_mode_lib` by value-copying the SoC/IP structs and replacing the callback table. There is no global mutable state in this file. Logging reads current `vba` and pipe structures without persisting data.

## Dependencies And Integration Points
The file includes generation-specific DML and RQ/DLG headers from DCN20 through DCN32 plus `dml_logger.h`. ASIC FPU files call `dml_init_instance()` after constructing bounding boxes. DCN FPU validation code calls `mode_lib->funcs.validate`, `recalculate`, and RQ/DLG callbacks through this dispatch layer.

## Risks
Unsupported or unrecognized `project` values leave `funcs` unchanged, which can produce stale callbacks if the struct was previously initialized. The validation status message switch covers only a subset of enum values. DCN35/DCN351 currently initialize as `DML_PROJECT_DCN31`, which is intentional in the read code but means they depend on DCN31 DML behavior unless DML2 paths override it. Logging assumes populated pointers and valid pipe counts.

## Test Signals
Tests should verify each project selects the expected callback table, especially DCN32 v2 RQ/DLG callbacks. Status-message tests should catch unmapped validation failures. Debug logging tests can compare key pipe fields and mode-support flags when diagnosing bandwidth validation regressions.
