# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_rq_dlg_helpers.c

## Purpose
`display_rq_dlg_helpers.c` provides debug printers for DML requestor, deadline generator, and TTU parameter and register structures.

## Important APIs, Types, And Functions
It exports `print__rq_params_st()`, `print__data_rq_sizing_params_st()`, `print__data_rq_dlg_params_st()`, `print__data_rq_misc_params_st()`, `print__dlg_sys_params_st()`, `print__data_rq_regs_st()`, `print__rq_regs_st()`, `print__dlg_regs_st()`, and `print__ttu_regs_st()`.

## Control Flow
Composite printers call lower-level luma and chroma printers, then log common fields. DLG and TTU printers enumerate register-like fields in hexadecimal; sizing and system printers log decimal and floating-point fields.

## State, Persistence, And Dependencies
The functions do not mutate inputs and keep no state. Their side effect is logging through `dml_print()`, which routes through `mode_lib->logger`. Dependencies are the helper header, `dml_logger.h`, `display_mode_lib.h`, and `DC_LOG_DML`.

## Integration Points
The DCN1 RQ/DLG calculator calls these helpers after computing request params and final DLG/TTU registers. They support comparisons against programming-guide values, spreadsheet traces, and hardware debug captures.

## Risks
Omitted fields or wrong format specifiers can hide calculation errors. The printers assume non-NULL pointers and can generate large logs on mode-set paths.

## Test Signals
Build with format warnings enabled. Runtime DML logging smoke tests should verify representative single-plane, dual-plane, VM, DCC, and cursor modes print expected sections and key fields.
