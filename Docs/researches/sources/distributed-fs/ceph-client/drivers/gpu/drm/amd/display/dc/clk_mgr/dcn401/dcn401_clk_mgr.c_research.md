# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c

## Purpose
This file implements the DCN 4.01 clock manager. It initializes DPM clock tables from SMU, builds watermark ranges, programs display and bandwidth clocks, sequences PMFW and DCCG operations, exposes clock-manager function pointers, and constructs/destroys the DCN 4.01 clock-manager object.

## Important APIs, Types, And Functions
Key internal helpers include `dcn401_init_single_clock`, `dcn401_build_wm_range_table`, `dcn401_build_update_bandwidth_clocks_sequence`, `dcn401_build_update_display_clocks_sequence`, `dcn401_execute_block_sequence`, `dcn401_set_hard_min_by_freq_optimized`, `dcn401_update_clocks_update_dpp_dto`, `dcn401_update_clocks_update_dtb_dto`, `dcn401_update_clocks_update_dentist`, `dcn401_notify_wm_ranges`, `dcn401_get_memclk_states_from_smu`, and `dcn401_get_max_clock_khz`. The exported construction path is `dcn401_clk_mgr_construct`; teardown is `dcn401_clk_mgr_destroy`.

The file uses `struct dcn401_clk_mgr_block_sequence` from the header to queue clock operations before execution. The function table `dcn401_funcs` integrates it with generic Display Core clock-manager operations.

## Control Flow And Integration
Initialization probes SMU with `dcn401_smu_get_smu_version`, checks driver and message header versions, queries DPM levels for DCFCLK, SOCCLK, DTBCLK, DISPCLK, DPPCLK, UCLK, and FCLK, applies debug minimum overrides, computes DC-mode limits, and updates the bandwidth bounding box. Watermark initialization creates PMFW rows for normal and dummy p-state ranges.

Runtime updates are split into bandwidth and display sequences. Bandwidth sequencing updates display count, UCLK/FCLK p-state support, DCFCLK, deep-sleep DCFCLK, FW-assisted memory switching, CAB ways, active/idle UCLK/FCLK hardmins, and SubVP prefetch hardmins. Display sequencing handles DTBCLK hardmin and DTO updates, DPPCLK and DISPCLK hardmins, dentist programming, DPP DTO ordering, and PSR wait-loop updates. The sequence executor then performs SMU, DCCG, dentist, and DMCU operations in the computed order.

## State And Persistence
The clock manager caches current `dc_clocks`, `smu_present`, `dpm_present`, `smu_ver`, DPM tables in `bw_params`, boot snapshot clocks, spread-spectrum state, and a GART-allocated `wm_range_table`. Firmware-side persistent state includes hardmins, p-state allow settings, DMCUB wait policy, DRR status, display count, CAB ways, and watermark rows.

## Dependencies
The implementation depends on DCCG, generic clock-manager helpers, DC state/resource helpers, link service, atom firmware spread-spectrum queries, DCN 4.1 register definitions, and `dcn401_clk_mgr_smu_msg.c` wrappers. It also uses Display Core debug flags such as `force_min_dcfclk_mhz`, `disable_dtb_ref_clk_switch`, `force_subvp_df_throttle`, `min_disp_clk_khz`, and `min_dpp_clk_khz`.

## Risks
The block sequence has a fixed maximum size of 30; future additions can overflow if not audited. `dcn401_set_hard_min_by_freq_optimized` intentionally floors then ceils to balance power and correctness, so firmware return values must be reliable. Some FCLK p-state messages are commented as unsupported, making policy asymmetric with UCLK. Hardmin acknowledgements wait up to one second, which can stall commit paths. Watermark table allocation and physical address transfer require strict lifetime handling.

## Test Signals
Good signals include correct DPM table population, SMU version/header validation logs, no underflow when raising/lowering DPPCLK and DISPCLK, correct ordering for DPP DTO versus global clock changes, successful watermark transfer, correct DC-mode softmax behavior, and AutoDPM test logs matching expected hardware readbacks.
