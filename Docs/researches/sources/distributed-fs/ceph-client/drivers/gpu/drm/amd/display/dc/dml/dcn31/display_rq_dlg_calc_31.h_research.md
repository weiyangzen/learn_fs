# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn31/display_rq_dlg_calc_31.h

## Purpose

`display_rq_dlg_calc_31.h` declares the DCN 3.1 RQ/DLG/TTU calculation interface. It is the public header for `display_rq_dlg_calc_31.c`, allowing display validation and hardware programming code to request computed register values for one pipe source or one pipe in a complete end-to-end pipe set.

## Important APIs, Types, And Functions

- Includes `../display_rq_dlg_helpers.h`, which supplies `display_rq_regs_st`, `display_dlg_regs_st`, `display_ttu_regs_st`, `display_pipe_params_st`, and `display_e2e_pipe_params_st`.
- Forward declares `struct display_mode_lib`.
- `dml31_rq_dlg_get_rq_reg(mode_lib, rq_regs, pipe_param)`: computes request queue register fields from one source pipe configuration.
- `dml31_rq_dlg_get_dlg_reg(mode_lib, dlg_regs, ttu_regs, e2e_pipe_param, num_pipes, pipe_idx, cstate_en, pstate_en, vm_en, ignore_viewport_pos, immediate_flip_support)`: computes display logic generator and TTU register fields for `pipe_idx` using the full compacted active-pipe array and policy flags.

## Control Flow

This header has no runtime control flow. It exposes two calculation entry points under the include guard `__DML31_DISPLAY_RQ_DLG_CALC_H__`.

The API-level flow implied by the declarations is:

1. Callers populate DML pipe parameters and a `struct display_mode_lib`.
2. Callers invoke `dml31_rq_dlg_get_rq_reg` when they need RQ register fields for a pipe source.
3. Callers invoke `dml31_rq_dlg_get_dlg_reg` with the compacted pipe array, active pipe count, selected pipe index, and validation policy flags when they need DLG and TTU register fields.
4. Callers program the returned register structs through generation-specific hardware code.

## State And Persistence Behavior

The header does not own state. Its functions write caller-provided output structs and read caller-owned DML inputs. There is no allocation, reference ownership, or on-disk persistence in this interface.

## Dependencies And Integration Points

This header is a DCN 3.1 generation-specific interface in AMD Display Core. It integrates with:

- The DML RQ/DLG helper type definitions.
- DCN 3.1 RQ/DLG implementation.
- Resource validation code that constructs `display_e2e_pipe_params_st`.
- Hardware programming code that consumes `display_rq_regs_st`, `display_dlg_regs_st`, and `display_ttu_regs_st`.

The comments explicitly frame `dml31_rq_dlg_get_rq_reg` as a main entry point for tests to obtain register values, so it also supports DML regression harnesses.

## Risks And Edge Cases

- The header does not validate `pipe_idx < num_pipes`, non-null pointers, or fully populated input structs. All such validation is the caller's responsibility.
- The `cstate_en`, `pstate_en`, `vm_en`, `ignore_viewport_pos`, and `immediate_flip_support` parameters imply policy control, but the current implementation treats several of them as unused inside the DLG calculation. Callers should not assume these flags independently override precomputed VBA values unless the implementation changes.
- Because this is a generation-specific header, including it from the wrong DCN generation can create subtle model mismatches even when types and signatures compile.

## Test Signals

- Compile tests catch declaration/definition mismatches and missing helper type includes.
- Unit tests can call the declared functions with synthetic DML inputs and compare output register structs against known DCN 3.1 cases.
- Integration tests should confirm the RQ/DLG/TTU outputs from these APIs match the register programming expected by DCN 3.1 hubp/hubbub/display timing code.
