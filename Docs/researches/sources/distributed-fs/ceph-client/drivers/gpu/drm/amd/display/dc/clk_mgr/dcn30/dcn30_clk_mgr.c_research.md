<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c

## Purpose

`dcn30_clk_mgr.c` implements the DCN3.0 clock manager for Sienna Cichlid-style dGPU. It initializes clock DPM levels from SMU, manages DISPCLK/DPPCLK/DCEFCLK/UCLK hard-mins, uploads watermark tables to PMFW, updates memory clock limits, and exposes DCN3 clock-manager callbacks.

## Important APIs, Types, And Functions

Public functions are `dcn3_init_clocks()`, `dcn3_clk_mgr_construct()`, and `dcn3_clk_mgr_destroy()`. Key helpers are `dcn3_init_single_clock()`, `dcn3_build_wm_range_table()`, `dcn30_get_vco_frequency_from_reg()`, `dcn3_update_clocks()`, `dcn3_notify_wm_ranges()`, memory limit setters, `dcn3_get_memclk_states_from_smu()`, `dcn3_is_smu_present()`, `dcn3_are_clock_states_equal()`, `dcn3_enable_pme_wa()`, and `dcn30_notify_link_rate_change()`. Callback tables are `dcn3_funcs` and `dcn3_fpga_funcs`.

## Control Flow

Construction installs callbacks/register masks, sets DFS/DPREF defaults and VCO fallback, allocates `bw_params`, and allocates a GART watermark range table whose GPU address is later passed to PMFW. `dcn3_init_clocks()` clears clock state, detects SMU presence through version query unless forced off, checks PMFW interface/header versions, queries DPM levels for DCEFCLK, DTBCLK, SOCCLK, DISPCLK, PIXCLK, PHYCLK, refreshes UCLK states, and builds watermark ranges.

`dcn3_update_clocks()` returns if SMU is missing, handles boot/resume DENTIST reads, notifies display count, applies forced DCFCLK minimums, sends DCEFCLK and deep-sleep hard-mins, manages p-state support by pinning UCLK to max or DC-mode softmax when unsupported, updates UCLK when support returns, sends hard-mins for PIXCLK and DISPCLK, sequences DPP DTO versus DENTIST changes, and updates DMCU PSR wait loops.

## State And Persistence Behavior

Persistent state includes `smu_present`, `smu_ver`, `bw_params`, `wm_range_table` and GPU address, clock state, p-state support history, DCCG DTO state, SMU hard-min/max constraints, and PMFW watermark table contents. `dcn3_clk_mgr_destroy()` frees allocated bandwidth params and watermark GPU memory.

## Dependencies And Integration Points

It depends on DCN20 shared DENTIST/DTO helpers, DCN30 SMU message helpers, DCN30 FPU watermark builder, Sienna/NBIO/MMHUB/DPCS register headers, DMCU, DCCG, DC resource bounding-box update functions, and SmartMux mobile hook `dcn30m_set_smartmux_switch()`.

## Risks

SMU absence disables updates entirely, so fallback behavior must be intentional. UCLK p-state pinning and DC-mode softmax transitions are subtle and can overconstrain memory clocks. Watermark upload requires valid GPU memory and matching `WatermarksExternal_t` layout. Construction can return after allocation failures without freeing earlier allocations. `dcn3_build_wm_range_table()` is wrapped in FPU guards twice.

## Test Signals

SMU present/absent paths, DPM-level discovery, interface/header version checks, p-state unsupported modes, DC-mode softmax, UCLK min/max APIs, watermark table uploads, link-rate PHYCLK changes, MALL/DF C-state messages, suspend/resume DENTIST reads, and destroy-time memory cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c -->
