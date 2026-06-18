<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn314/dcn314_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn314/dcn314_clk_mgr.c

## Purpose
Implements the DCN 3.1.4 display clock manager for AMD display hardware. It owns boot-time clock manager construction, runtime clock updates for DISPCLK/DPPCLK/DCFCLK/deep-sleep DCFCLK/DTBCLK, SMU watermark/DPM table exchange, spread-spectrum handling, and low-power/zstate transitions for display-off and mission-mode operation.

## Important APIs, Types, And Functions
- `dcn314_clk_mgr_construct` initializes `struct clk_mgr_dcn314`, hooks `dcn314_funcs`, allocates GPU-visible watermark and DPM buffers, queries SMU version, selects DDR5/LPDDR5 watermark defaults, reads spread-spectrum state, and optionally replaces default bandwidth parameters from SMU DPM data.
- `dcn314_update_clocks` is the runtime clock transition entry point used by DC. It compares requested `dc_state` clocks against persisted `clk_mgr_base->clks`, calls DCN314 SMU helpers, updates DPP DTOs, applies OTG-disable workarounds, and notifies DMCUB.
- `dcn314_init_clocks`, `dcn314_are_clock_states_equal`, `dcn314_is_spll_ssc_enabled`, and `dcn314_clk_mgr_destroy` provide lifecycle and comparison support.
- Internal helpers build watermark ranges, transfer watermark/DPM tables via SMU DRAM address messages, derive VCO frequency from PLL registers, and populate `clk_bw_params` from `DpmClocks314_t`.

## Control Flow
Construction sets static defaults first, then allocates a framebuffer watermark table and a temporary DPM table. If PMFW responds to `dcn314_smu_get_smu_version`, the manager treats SMU as present and can exchange tables. Runtime updates branch on `safe_to_lower`: lowering may allow zstates, disable DTBCLK, and enter display-off low power when the active-display workaround count is zero; raising disallows zstates when requested, enables DTBCLK, exits idle optimization, and returns to mission mode. Clock requests are then ordered so DCF hard-mins and deep-sleep minima are sent before DISPCLK/DPPCLK changes. DPP DTOs are updated before lowering global DPPCLK and after raising it.

## State And Persistence
Persistent state is in `clk_mgr->base.base.clks`, `dentist_vco_freq_khz`, `dprefclk_khz`, `dp_dto_source_clock_in_khz`, SMU presence/version fields, bandwidth tables, and the GPU allocation tracked by `smu_wm_set.mc_address`. The static `dcn314_bw_params` and watermark tables are shared configuration templates. The current power state, zstate allowance, DTBCLK enablement, and last programmed clock values are used to suppress redundant PMFW messages.

## Dependencies And Integration Points
This file integrates DC clock policy with DCCG DTO programming, DMCUB clock notifications, link encoder state, BIOS integrated memory info, spread-spectrum BIOS tables, and the DCN314 SMU mailbox layer in `dcn314_smu.c`. It reuses DCN20 DPP DTO update logic, DCN31 DTB reference helpers, DCE DP reference helpers, and common `clk_mgr_internal` helpers such as `should_set_clock`.

## Risks And Edge Cases
The active-display workaround intentionally counts enabled DIG/PHY state and forces one display for TMDS display-off cases to avoid HDMI resume hangs. The DISPCLK path temporarily disables OTGs for DPMS-off or virtual streams, so incorrect pipe selection can cause visible glitches. PMFW DPM tables are trusted enough to populate bandwidth limits but guarded by validity checks and fallback defaults; malformed level counts or zero clocks can distort watermarks and mode validation. Mutating `new_clocks->dppclk_khz` to enforce the 100 MHz floor is a side effect visible to later code in the same state transition.

## Test Signals
Useful signals include boot with and without SMU response, pstate-enabled versus disabled runs, DDR5 and LPDDR5 integrated info, display-off/restore over HDMI and DP, DTBCLK enable/disable transitions, zstate allow/disallow transitions, DPPCLK lowering and raising with DTO ordering, successful DMCUB notify commands, and watermark table transfers with nonzero GPU addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn314/dcn314_clk_mgr.c -->
