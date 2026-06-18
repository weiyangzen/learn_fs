# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/clk_mgr.h

## Purpose

`clk_mgr.h` defines the public Display Core clock-manager abstraction. It owns display clock state, DPM clock-limit/watermark tables, SMU/PMFW interactions, low-power transitions, register dump interfaces, and clock update policy.

## Important APIs, Types, And Functions

Important constants include watermark set IDs and minimum DISPCLK/DPPCLK. Types include ASIC-specific clock register snapshots, `enum clk_type`, `clk_limit_table_entry`, `clk_limit_table`, watermark range structs, `clk_state_registers_and_bypass`, `wm_table`, `clk_bw_params`, `clk_mgr_funcs`, and `clk_mgr`. Public constructors/helpers are `dc_clk_mgr_create`, `dc_destroy_clk_mgr`, `clk_mgr_exit_optimized_pwr_state`, and `clk_mgr_optimize_pwr_state`.

## Control Flow

Validation populates required clocks and watermark ranges. Commit code calls `update_clocks(clk_mgr, context, safe_to_lower)`: with `safe_to_lower == false`, implementations raise clocks needed for safety; with true, they lower clocks after programming is safe. Clock manager functions query DP/DTB refs, set low-power state, dump registers, notify watermark ranges, respond to link-rate changes, and set hard min/max memory clocks through SMU.

## State And Persistence Behavior

`clk_mgr` persists on the DC instance and stores current `dc_clocks`, DP reference clocks, dentist VCO, boot register snapshot, bandwidth params, SMU watermark ranges, and policy flags. Hardware/firmware persistence includes programmed clocks, DPM bounds, PMFW watermark ranges, and low-power state.

## Dependencies And Integration Points

It includes `dc.h` and `dm_pp_smu.h`. It integrates with resource validation, DML/DML2 bandwidth output, PPLIB/SMU, DCCG, clock sources, link-rate changes, idle power optimization, and HWSS clock callbacks.

## Risks And Edge Cases

Clock lowering must be delayed until safe or underflow can occur. Watermark set IDs and latency fields must match PMFW contracts. Units mix kHz, MHz, MT/s, and microseconds. Missing SMU handling must use fallback paths. DC mode softmax and hard min/max memory clock controls can affect system power/performance outside display.

## Test Signals

Tests should cover clock raising/lowering order, SMU-present/absent paths, watermark notification, link-rate changes, DC mode, low-power entry/exit, register dumps, hard min/max memclk, and DPM table parsing. Underflow, clock readback mismatch, and PMFW errors are core signals.
