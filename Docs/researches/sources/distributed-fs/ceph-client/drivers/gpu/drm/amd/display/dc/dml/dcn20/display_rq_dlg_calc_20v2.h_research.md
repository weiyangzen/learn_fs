# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/display_rq_dlg_calc_20v2.h

## Purpose

`display_rq_dlg_calc_20v2.h` is the public DCN 2.0v2 Display Mode Library header for RQ, DLG, and TTU register calculation. It exposes the v2 namespaced calculation entry points implemented in `display_rq_dlg_calc_20v2.c` so the shared DML dispatch table can select the DCN 2.0v2 algorithm independently from the original DCN 2.0 implementation.

Like the non-v2 header, this file is a declaration contract only. It does not implement formulas, own state, or program hardware.

## Important APIs, Types, And Functions

- `dml20v2_rq_dlg_get_rq_reg(mode_lib, rq_regs, pipe_param)`: calculates requestor queue register fields for a single pipe and writes `display_rq_regs_st`.
- `dml20v2_rq_dlg_get_dlg_reg(mode_lib, dlg_regs, ttu_regs, e2e_pipe_param, num_pipes, pipe_idx, cstate_en, pstate_en, vm_en, ignore_viewport_pos, immediate_flip_support)`: calculates DLG and TTU register fields for one pipe in an end-to-end active-pipe set.
- `struct display_mode_lib`: forward declaration for the DML context carrying SoC, IP, function-table, logging, and VBA state.
- Shared output/input structs come from `display_rq_dlg_helpers.h` and `display_mode_lib.h`: `display_rq_regs_st`, `display_dlg_regs_st`, `display_ttu_regs_st`, `display_pipe_params_st`, and `display_e2e_pipe_params_st`.

## Control Flow

`display_mode_lib.c` includes this header and wires the public functions into `dml20v2_funcs`. Display resource code that has selected the DCN 2.0v2 DML implementation calls those function pointers while building per-pipe hardware programming state.

The documented flow mirrors the implementation: RQ generation derives register-definition-agnostic request parameters and then extracts encoded register fields; DLG generation consumes compacted end-to-end pipe parameters and system policy flags to produce DLG and TTU register structs.

## State And Persistence Behavior

The header has no mutable state and creates no persistence. Its functions are declared as output-struct writers: they read DML context and pipe arrays, then populate caller-owned register structs. Any hardware-visible persistence is outside this header and occurs only when later code programs the generated values into registers.

## Dependencies And Integration Points

The direct dependency is `../display_rq_dlg_helpers.h`, which brings in shared DML type definitions and print helper declarations. Integration points include:

- `display_rq_dlg_calc_20v2.c`, the implementation for these symbols.
- `display_mode_lib.c`, where `dml20v2_funcs` registers these functions.
- `display_mode_lib.h`, whose `struct dml_funcs` prototypes must stay compatible.
- DCN 2.0 resource/FPU code that consumes `struct dml_funcs` to populate DLG, TTU, and RQ register caches.

## Risks And Edge Cases

- Because this header is nearly identical to `display_rq_dlg_calc_20.h`, accidental symbol substitution between `dml20_*` and `dml20v2_*` is a realistic maintenance risk.
- The boolean policy arguments are positional and same-typed, so direct callers can accidentally swap c-state, p-state, VM, viewport, and immediate-flip controls without compiler help.
- Any mismatch between this header and the implementation breaks the DCN 2.0v2 function-table assignment.
- The header exposes a broader signature than the current v2 implementation uses; in `display_rq_dlg_calc_20v2.c`, `vm_en`, `ignore_viewport_pos`, and `immediate_flip_support` are currently ignored.

## Test Signals

- Compile tests should verify this header can be included wherever `struct dml_funcs` is initialized and that the v2 symbols resolve.
- Function-table tests or static checks should confirm `dml20v2_funcs` uses the v2 functions and not the DCN 2.0 functions.
- ABI-style regression tests should flag changes to these prototypes because downstream function-pointer users depend on exact signatures.
- DML output tests should include at least one case that distinguishes DCN 2.0v2 from DCN 2.0, especially the DLG `min_dst_y_next_start` behavior implemented behind this declaration.
