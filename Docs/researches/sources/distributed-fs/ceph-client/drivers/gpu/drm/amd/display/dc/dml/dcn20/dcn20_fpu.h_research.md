# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/dcn20_fpu.h

## Purpose

`dcn20_fpu.h` declares the FPU-protected DCN2.0/DCN2.01/DCN2.1 DML and bandwidth helper interfaces implemented in `dcn20_fpu.c`. It is the integration boundary used by resource, clock-manager, and writeback code that must call into floating-point DML logic while keeping FPU-sensitive implementation details centralized.

## Important APIs, Types, And Functions

The header includes `core_types.h`, which supplies many of the display core type declarations used in the prototypes. Declared APIs include:

- Writeback modeling: `dcn20_populate_dml_writeback_from_context`, `dcn201_populate_dml_writeback_from_context_fpu`.
- Writeback arbitration: `dcn20_fpu_set_wb_arb_params`.
- DLG and watermark programming: `dcn20_calculate_dlg_params`, `dcn20_calculate_wm`.
- DML pipe translation: `dcn20_populate_dml_pipes_from_context`, `dcn21_populate_dml_pipes_from_context`.
- Bounding-box and clock table updates: `dcn20_cap_soc_clocks`, `dcn20_update_bounding_box`, `dcn20_patch_bounding_box`, `dcn21_update_bw_bounding_box_fpu`, `dcn21_clk_mgr_set_bw_params_wm_table`.
- Bandwidth validation entry points: `dcn20_validate_bandwidth_fp`, `dcn21_validate_bandwidth_fp`.
- SMU/DML adjustment helpers: `dcn20_fpu_set_wm_ranges`, `dcn20_fpu_adjust_dppclk`.

The prototypes expose several cross-subsystem structures: `struct dc`, `struct dc_state`, `struct resource_context`, `struct mcif_arb_params`, `display_e2e_pipe_params_st`, `struct _vcs_dpi_soc_bounding_box_st`, `struct pp_smu_nv_clock_table`, `struct pp_smu_wm_range_sets`, `struct vba_vars_st`, and `struct clk_bw_params`.

## Control Flow

The header itself has no runtime control flow. It enables resource-layer code to call into these flows:

1. Populate DML pipes from a proposed `dc_state`.
2. Run DCN2 bandwidth validation.
3. Calculate watermarks and DLG/RQ/TTU programming data.
4. Update SoC bounding boxes from firmware/SMU clock data.
5. Populate SMU watermark ranges and writeback arbitration parameters.

## State And Persistence Behavior

The header owns no state. The declared functions mutate display driver state in their implementation, especially `context->bw_ctx`, `context->res_ctx.pipe_ctx`, DML bounding boxes, clock-manager bandwidth parameters, and caller-provided pipe arrays. There is no disk persistence.

## Dependencies And Integration Points

This header is included by:

- `dcn20_fpu.c` for prototype consistency.
- DCN20/DCN21 resource files that call validation, bounding-box update, watermark range, and writeback helpers.
- DCN201 resource code for the DCN2.01 writeback-specific helper.
- Newer DCN resource files that reuse the generic `dcn20_patch_bounding_box`.

The header is part of the FPU boundary. Callers must wrap calls with the display core FPU protection mechanism before entering these APIs.

## Risks And Edge Cases

- The `_fp` suffix is a convention, not compile-time enforcement. Incorrect caller-side FPU handling is caught only by implementation assertions.
- Prototypes expose DML-internal types, so changes to DML struct names or include paths ripple into resource code.
- Some functions are DCN2.0-specific while others apply to DCN2.1 or DCN2.01. Calling the wrong helper for a resource generation can silently produce invalid DML modeling.
- `dcn20_fpu_adjust_dppclk` mutates DML VBA arrays in place; callers must pair validation/non-validation adjustment correctly to avoid leaving doubled or halved clocks.
- Header include order is partly covered by `core_types.h`, but callers may still need generation-specific headers for complete definitions.

## Test Signals

Useful validation signals include:

- Compile coverage for all resource files that include this header.
- Link coverage ensuring every declared symbol remains implemented when DCN generation configs are enabled.
- Runtime FPU assertion tests through representative callers.
- Cross-generation validation tests confirming DCN20, DCN201, and DCN21 resource code dispatches to the correct declared helper.
