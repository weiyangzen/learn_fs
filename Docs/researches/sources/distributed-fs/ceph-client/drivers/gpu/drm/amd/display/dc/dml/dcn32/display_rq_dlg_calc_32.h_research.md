# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn32/display_rq_dlg_calc_32.h

## Purpose
This header exposes the DCN32 request queue and display logic generator register calculation entry points. It documents that DCN32 uses the newer v2 interface shape: register functions receive the full compacted `display_e2e_pipe_params_st` array, active pipe count, and target pipe index rather than a single pipe-only structure.

## Important APIs, Types, And Functions
`dml32_rq_dlg_get_rq_reg()` produces `display_rq_regs_st` for one pipe from `display_mode_lib`, the compacted pipe array, `num_pipes`, and `pipe_idx`. `dml32_rq_dlg_get_dlg_reg()` produces `display_dlg_regs_st` and `display_ttu_regs_st` for one pipe from the same multi-pipe context. The header forward declares `struct display_mode_lib` and imports `display_rq_dlg_helpers.h` for the register and pipe typedefs.

## Control Flow And State
The header has no control flow or state. Its comments define the intended flow: calculate RQ/DLG parameters from DML state, extract hardware register fields into output structs, and use cstate/pstate concepts indirectly through values already present in the DML calculation.

## Dependencies And Integration Points
`display_mode_lib.c` binds these symbols into `dml32_funcs`. DCN32 validation/programming code calls them through `context->bw_ctx.dml.funcs.rq_dlg_get_*_v2`. It is tightly coupled to `display_mode_structs.h` register structs and helper functions implemented outside this header.

## Risks
The v2 function signatures are intentionally different from earlier DML generations. Accidentally wiring them into legacy `rq_dlg_get_*` callback slots would corrupt call arguments. Since the header does not encode array lengths beyond `num_pipes`, callers must guarantee `pipe_idx < num_pipes` and that the compacted array order matches the resource pipe order expected by downstream programming.

## Test Signals
Compile-time coverage should ensure DCN32 binds the v2 callbacks. Runtime coverage should verify each active pipe receives nonzero RQ/DLG/TTU fields from the expected compacted index, especially with split or ODM-combined pipes.
