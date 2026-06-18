# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn30/dcn30_fpu.h

## Purpose

This header declares the DCN 3.0 floating-point DML/resource integration functions implemented in `dcn30_fpu.c`. It is the public interface used by DCN30 resource and clock-manager code for writeback modeling, watermark/DLG calculation, bounding-box updates, dummy pstate support, and BIOS/PMFW watermark setup.

The header includes `core_types.h` and `dcn20/dcn20_optc.h`, which provide core display, DML, resource, clock, and MCIF/OPT controller type declarations used by the prototypes.

## Important APIs, Types, and Functions

The declarations cover the complete exported surface of the C file:

- `dcn30_fpu_populate_dml_writeback_from_context()` maps `struct resource_context` pipe/writeback state into `display_e2e_pipe_params_st` writeback fields.
- `dcn30_fpu_set_mcif_arb_params()` fills `struct mcif_arb_params` watermarks from a DML instance and pipe array.
- `dcn30_fpu_update_soc_for_wm_a()` applies WM_A latency inputs to a validation context.
- `dcn30_fpu_calculate_wm_and_dlg()` calculates DCN watermarks and DLG data for a context, pipe array, pipe count, and voltage level.
- `dcn30_fpu_update_dram_channel_width_bytes()` patches DML SOC channel width from BIOS VRAM information.
- `dcn30_fpu_update_max_clk()` fills missing max clock fields in `struct dc_bounding_box_max_clk`.
- `dcn30_fpu_get_optimal_dcfclk_fclk_for_uclk()` derives DCFCLK/FCLK recommendations for a UCLK rate.
- `dcn30_fpu_update_bw_bounding_box()` updates DML bounding boxes and reinitializes DML from clock arrays.
- `dcn30_find_dummy_latency_index_for_fw_based_mclk_switch()` searches for a usable dummy pstate latency index.
- `dcn3_fpu_build_wm_range_table()` initializes clock manager watermark ranges and dummy pstate table entries.
- `patch_dcn30_soc_bounding_box()` patches SOC latency fields from BIOS-provided bounding-box data.

## Control Flow

The header has no executable control flow. It enables call sites in `resource/dcn30/dcn30_resource.c` and `clk_mgr/dcn30/dcn30_clk_mgr.c` to call into the FPU-protected implementation. The prototypes make the calling convention explicit: most functions mutate caller-provided context structures and must be invoked under whatever FPU enable/disable discipline the caller uses around DCN FPU code.

## State and Persistence Behavior

There is no direct state in the header. The declared functions imply significant state mutation in their implementation: DML pipe arrays, bandwidth context watermarks, global DCN30 SOC/IP bounding boxes, clock manager watermark tables, and BIOS-derived latency/channel-width fields. Callers should treat these routines as mutating operations rather than pure calculations unless the specific function only writes output pointers.

## Dependencies and Integration Points

This header is an integration contract between DCN30 resource management, clock management, and DML. The resource layer uses it during validation, bandwidth bounding-box setup, writeback modeling, and watermark/DLG calculation. The clock manager uses it when building PMFW watermark ranges. The implementation also depends on DCN20 shared DLG calculation code, but that dependency is intentionally hidden behind the DCN30 API.

## Risks and Edge Cases

The main interface risk is that the header does not encode FPU preconditions; callers must know these functions require FPU-enabled execution because the implementation asserts it. Several prototypes accept raw pointers and array counts without size annotations, so incorrect `pipe_cnt`, `vlevel`, or clock-array sizing can corrupt calculations in the implementation. The `patch_dcn30_soc_bounding_box()` parameter name suggests an IP pointer even though the type is SOC bounding-box; the implementation ignores it, so callers should not expect that argument to be patched.

## Test Signals

Compile tests should cover all DCN30 resource and clock-manager users of this header. Functional validation should exercise each declared function through its real call site, with debug FPU assertions enabled, and verify that DML instances, watermarks, clock recommendations, writeback parameters, and bounding-box patches match expected DCN30 behavior.
