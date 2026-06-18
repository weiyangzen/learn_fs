# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/display_mode_core_structs.h

## Purpose
`display_mode_core_structs.h` is the central schema for DML 2.0 mode evaluation and programming. It defines project, output, tiling, format, rotation, MALL, p-state, ODM/MPC, and clock-policy enums; SoC and IP bounding-box structures; display input configuration; support-failure reporting; programming outputs; parameter blocks; scratch storage; and register layout structures.

## Important APIs, types, and functions
Key types are `struct display_mode_lib_st`, `struct dml_display_cfg_st`, `struct dml_mode_eval_policy_st`, `struct dml_mode_support_info_st`, `struct mode_support_st`, and `struct mode_program_st`. Input is split across `dml_surface_cfg_st`, `dml_plane_cfg_st`, `dml_timing_cfg_st`, `dml_output_cfg_st`, `dml_writeback_cfg_st`, `dml_hw_resource_st`, and `dml_clk_cfg_st`. Calculation helper parameter blocks include `UseMinimumDCFCLK_params_st`, `CalculateWatermarksMALLUseAndDRAMSpeedChangeSupport_params_st`, `CalculateVMRowAndSwath_params_st`, `CalculateSwathAndDETConfiguration_params_st`, `CalculateStutterEfficiency_params_st`, and `CalculatePrefetchSchedule_params_st`. Register ABI structures include `dml_display_rq_regs_st`, `dml_display_dlg_regs_st`, `dml_display_ttu_regs_st`, and `dml_display_arb_params_st`.

## Control flow
The file has no executable flow, but it encodes the data flow through the core: SoC/IP/policy/display inputs enter `display_mode_lib_st`; mode support fills `mode_support_st` and `dml_mode_support_info_st` with pass/fail reasons, resource choices, bandwidths, p-state support, and intermediate swath/DET values; mode programming fills `mode_program_st` with clocks, watermarks, DLG/TTU/RQ timing, DCC blocks, MALL use, p-state support, and pipe-to-plane mapping.

## State and persistence behavior
All structures are in-memory state owned by a DML context or caller. Large local-state blocks are explicitly aggregated under `display_mode_lib_scratch_st` to reduce stack pressure. There is no persistence outside the caller's lifetime.

## Dependencies and integration points
The header depends on `display_mode_lib_defines.h` and `dml_top_display_cfg_types.h`. It is the common contract between DML calculation code, debug dump helpers, and driver wrappers that translate kernel display state into model inputs and map model outputs to hardware programming.

## Risks and edge cases
Most arrays are fixed at `__DML_NUM_PLANES__` or two combine-state slots, so overflow depends on wrappers correctly bounding stream/plane counts. The schema mixes units such as MHz, kHz, MBytes, KBytes, bytes, cycles, lines, and microseconds. Support booleans include both positive and negative semantics, making debug output and guard logic easy to invert. Layout changes can silently break consumers that memcpy register structures or scratch sub-blocks.

## Test signals
Validation should cover structure-size/layout-sensitive builds, maximum-plane configs, no-plane/blank-stream configs, 420/422/RGB formats, DSC/ODM/MPC combinations, hostvm/gpuvm page-table levels, MALL/subviewport p-state modes, immediate flip, dynamic metadata, and known-vector comparisons for support reasons and programming fields.
