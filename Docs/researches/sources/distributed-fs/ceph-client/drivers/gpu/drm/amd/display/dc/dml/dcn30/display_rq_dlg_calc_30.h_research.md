# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn30/display_rq_dlg_calc_30.h

## Purpose
This header exposes the DCN 3.0 RQ/DLG calculation entry points implemented by `display_rq_dlg_calc_30.c`. It is the public interface used by tests and display code that need DML-derived request queue, display logic generator, and TTU register structures.

## Important APIs, Types, And Functions
- Includes `../display_rq_dlg_helpers.h`, which supplies the shared DML register and pipe parameter types.
- Forward-declares `struct display_mode_lib`.
- Declares `dml30_rq_dlg_get_rq_reg(struct display_mode_lib *mode_lib, display_rq_regs_st *rq_regs, const display_pipe_params_st *pipe_param)`.
- Declares `dml30_rq_dlg_get_dlg_reg(struct display_mode_lib *mode_lib, display_dlg_regs_st *dlg_regs, display_ttu_regs_st *ttu_regs, const display_e2e_pipe_params_st *e2e_pipe_param, unsigned int num_pipes, unsigned int pipe_idx, bool cstate_en, bool pstate_en, bool vm_en, bool ignore_viewport_pos, bool immediate_flip_support)`.

## Control Flow
The header has no runtime control flow. It documents the expected call shapes: one function derives RQ registers from a single pipe source configuration, while the other derives DLG and TTU registers for one indexed pipe within a compacted multi-pipe end-to-end parameter array.

## State And Persistence
No state is defined. Callers own all input and output storage. The header only establishes ABI-level dependencies between compilation units.

## Dependencies And Integration Points
This file is included by the DCN 3.0 implementation and by any code needing these calculation routines. It binds DCN 3.0-specific naming to common DML helper types, allowing versioned callers to select the correct calculator while sharing generic register structures.

## Risks And Edge Cases
- The prototypes require valid, initialized `mode_lib` and pipe structs; the implementation assumes many nested fields are populated.
- Several Boolean arguments in the DLG prototype are compatibility knobs, but the DCN 3.0 implementation currently ignores some of them internally.
- Because the header does not include full type definitions beyond helper headers, include ordering must already make `bool` and helper typedefs available through the included DML headers.

## Test Signals
Compile coverage should ensure users can include the header in both implementation and caller contexts. ABI tests or build checks should catch signature drift against call sites. Runtime tests belong with the `.c` implementation and should verify both exported functions populate nonzero, bounded register structures for representative pipes.
