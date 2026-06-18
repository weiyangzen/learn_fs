<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn315/dcn315_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn315/dcn315_clk_mgr.c

## Purpose
Implements the DCN315 clock-manager variant. It programs display clocks through DCN315 SMU messages, builds watermark ranges, imports PMFW DPM tables into bandwidth parameters, and handles display-off low-power transitions and OTG workarounds.

## Important APIs, Types, And Functions
- `dcn315_update_clocks` is the active runtime updater for DCFCLK, deep-sleep DCFCLK, DISPCLK, DPPCLK, DTBCLK, and display idle optimization.
- `dcn315_clk_mgr_construct` initializes function pointers, GPU-visible watermark/DPM tables, SMU version state, memory-specific watermark defaults, DPREF/DTB reference clocks, spread-spectrum adjustment, and optional PMFW-derived bandwidth data.
- `dcn315_clk_mgr_helper_populate_bw_params` maps `DpmClocks_315_t` voltage and pstate data into `clk_bw_params`.
- `dcn315_build_watermark_ranges` and `dcn315_notify_wm_ranges` prepare PMFW watermark ranges and transfer them through DRAM.

## Control Flow
Runtime updates skip entirely under `skip_clock_update`. The active-display workaround counts enabled link encoders and keeps TMDS display-off as one active display. On lowering, DTBCLK may be disabled and idle optimization entered. On raising, DTBCLK and mission mode are restored. A DCN315-specific pstate lock requests an unsupported 10 GHz DCFCLK when `p_state_change_support` is false. DISPCLK changes wrap SMU programming with the OTG workaround, while DPPCLK changes preserve DTO ordering around lowering or raising.

## State And Persistence
State persists in `clk_mgr_base->clks`, `smu_present`, `smu_ver`, the static `dcn315_bw_params`, and `smu_wm_set`. Constructor-allocated DPM memory is temporary and freed after import; the watermark buffer persists until destroy. `pwr_state`, `zstate_support`, `dtbclk_en`, and last clock values suppress redundant PMFW updates.

## Dependencies And Integration Points
The file uses DCN315 SMU wrappers, DCE DP ref clock helpers, DCN31 init/equality helpers, DCN20 DPP DTO updates, DCCG state, DMCUB notify commands, link encoder state, and BIOS integrated memory info.

## Risks And Edge Cases
The unsupported-DCFCLK pstate lock relies on PMFW behavior and can be fragile if PMFW clamps or rejects it. `should_disable_otg` must avoid disabling an active DIG path. DPM table population assumes DF pstate sorting and matching voltage/count arrays. Zero or inconsistent PMFW clocks fall back to defaults but can reduce power optimization quality.

## Test Signals
Exercise pstate supported/unsupported transitions, TMDS display-off restore, DIG-active OTG bypass, DPREF query through SMU, DPM import with mismatched DCF/SOC levels, DPPCLK 100 MHz floor, watermark transfer, and DMCUB clock notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn315/dcn315_clk_mgr.c -->
