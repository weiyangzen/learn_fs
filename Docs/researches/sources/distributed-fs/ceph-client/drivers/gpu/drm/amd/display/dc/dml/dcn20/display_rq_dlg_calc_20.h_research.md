# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/display_rq_dlg_calc_20.h

## Purpose

`display_rq_dlg_calc_20.h` is the public DCN 2.0 Display Mode Library header for requestor queue (RQ), display logic generator (DLG), and time-to-use (TTU) register calculation. It exposes the two generation-specific entry points that convert DML pipe timing, scaling, tiling, memory, and watermark data into hardware register structs consumed by AMD Display Core programming paths.

The header itself contains no calculations. Its role is ABI and integration: include the shared RQ/DLG type declarations from `display_rq_dlg_helpers.h`, forward-declare `struct display_mode_lib`, and publish the DCN 2.0 function names that `display_mode_lib.c` installs into the `dml20_funcs` dispatch table.

## Important APIs, Types, And Functions

- `dml20_rq_dlg_get_rq_reg(mode_lib, rq_regs, pipe_param)`: fills `display_rq_regs_st` for one pipe from `display_pipe_params_st`. The implementation computes source-format, tiling, swath, metadata, and PTE sizing before extracting hardware register fields.
- `dml20_rq_dlg_get_dlg_reg(mode_lib, dlg_regs, ttu_regs, e2e_pipe_param, num_pipes, pipe_idx, cstate_en, pstate_en, vm_en, ignore_viewport_pos, immediate_flip_support)`: fills DLG and TTU register structs for one pipe within a compacted active-pipe array.
- `struct display_mode_lib`: forward-declared owner of SoC/IP parameters, DML function tables, logging, and VBA-calculated model state.
- `display_rq_regs_st`, `display_dlg_regs_st`, `display_ttu_regs_st`, `display_pipe_params_st`, and `display_e2e_pipe_params_st`: shared DML structs pulled in indirectly through `display_rq_dlg_helpers.h` and `display_mode_lib.h`.

## Control Flow

Callers do not include implementation details from this header; they select the functions through `struct dml_funcs` or call the named symbols directly. `display_mode_lib.c` includes this header and assigns `dml20_rq_dlg_get_dlg_reg` and `dml20_rq_dlg_get_rq_reg` into the DCN 2.0 function table. DCN resource code later calls those function pointers while populating per-pipe `rq_regs`, `dlg_regs`, and `ttu_regs`.

The header's comments document the intended implementation flow: RQ register generation calls an internal `get_rq_param` style calculation and then extracts RQ register fields; DLG register generation uses compacted end-to-end pipe parameters plus clock, c-state, p-state, virtual-memory, viewport, and immediate-flip policy flags.

## State And Persistence Behavior

This header declares pure calculation entry points from the caller perspective. It owns no storage, global variables, or persistent state. The implementation writes caller-owned output structs and reads `mode_lib`, pipe parameters, and DML model state. Hardware persistence happens later when the display core programs the generated register values; this header is only the calculation contract.

## Dependencies And Integration Points

The only direct include is `../display_rq_dlg_helpers.h`, which supplies shared DML typedefs and debug printer prototypes. The header integrates with:

- `display_mode_lib.c`, where DCN 2.0 DML function pointers are registered.
- `display_mode_lib.h`, which defines the common `struct dml_funcs` slots matching these prototypes.
- DCN 2.0 FPU/resource code that calls the registered functions to fill pipe register programming data.
- The sibling implementation file `display_rq_dlg_calc_20.c`, which contains the actual calculations.

## Risks And Edge Cases

- Prototype drift between this header, `display_mode_lib.h`, and `display_rq_dlg_calc_20.c` would break DCN 2.0 function-table registration or produce compile errors.
- The function signatures expose several boolean policy flags. Misordered arguments at direct call sites are hard to detect because they share the same type.
- The header uses shared DML typedefs rather than local structs, so any incompatible change in `display_mode_structs.h` can affect this API.
- DCN 2.0 and DCN 2.0v2 headers are intentionally very similar. Mixing `dml20_*` and `dml20v2_*` symbols would silently select a different algorithm variant if function-table wiring is changed incorrectly.

## Test Signals

- Kernel build coverage verifies prototypes, includes, and function-table assignment compatibility.
- Static symbol checks can confirm that `dml20_funcs` points at the DCN 2.0 symbols and not the v2 symbols.
- Runtime validation should compare generated RQ/DLG/TTU register values against known-good DCN 2.0 DML vectors for RGB, YUV420, tiled, linear, c-state, p-state, VM, and immediate-flip scenarios.
- Regression tests should include direct compile coverage for consumers including only this header and calling both public entry points.
