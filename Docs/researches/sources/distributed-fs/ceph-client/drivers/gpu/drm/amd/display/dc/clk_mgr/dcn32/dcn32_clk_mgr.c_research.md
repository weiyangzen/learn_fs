<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c

## Purpose
Implements the DCN32/DCN321 clock manager. It discovers SMU DPM levels, builds bandwidth and watermark tables, sequences live clock updates across SMU hard-min requests and DCCG DTO programming, manages UCLK/FCLK pstate policy, handles DTBCLK switching, and exposes memory-clock control hooks.

## Important APIs, Types, And Functions
- `dcn32_clk_mgr_construct` selects register tables for DCN32 versus DCN321, reads dentist VCO/boot clocks/spread-spectrum state, allocates bandwidth params and a GART watermark table.
- `dcn32_init_clocks` queries SMU for DCF/SOC/DTB/DISP/DPP/UCLK/FCLK DPM levels, applies debug floors and 1950 MHz display clock caps, marks DPM presence, and builds watermark ranges through FPU helpers.
- `dcn32_update_clocks` is the main runtime transition path for DCFCLK, deep-sleep DCFCLK, UCLK, FCLK pstate permission, DISPCLK, DPPCLK, DTBCLK, CAB, and DMCU PSR wait-loop updates.
- `dcn32_update_clocks_update_dpp_dto`, `dcn32_update_clocks_update_dtb_dto`, and `dcn32_update_clocks_update_dentist` sequence DCCG and dentist divider programming.
- Memory hooks include `dcn32_set_hard_min_memclk`, `dcn32_set_hard_max_memclk`, `dcn32_get_memclk_states_from_smu`, `dcn32_set_max_memclk`, and `dcn32_set_min_memclk`.

## Control Flow
Initialization starts with a SMU presence/version check, then queries each PPCLK with `dcn32_init_single_clock`; a fine-grained DPM response becomes two levels, while discrete DPM reports a fixed count. Runtime updates first handle boot/resume force-reset, active display count, display count notification, FCLK pstate support messages, DCFCLK/deep-sleep hard-mins, UCLK pstate lock/unlock, DMCUB MCLK-ack policy, dramclk hard-mins, and CAB num-ways messages. It then rounds DISPCLK/DPPCLK to dentist-realizable values and sequences dentist/DTO updates differently for clock lowering versus raising.

## State And Persistence
Persistent state includes `clk_mgr->base.bw_params`, `wm_range_table`/address, `smu_present`, `dpm_present`, SMU version, `dentist_vco_freq_khz`, boot snapshot, spread-spectrum fields, current `dc_clocks`, and DCCG per-pipe DTO state. UCLK/FCLK pstate support, `num_ways`, and `dc_mode_softmax_memclk` are carried across updates.

## Dependencies And Integration Points
Integrates with DCN30 SMU helpers, DCN32-specific SMU messages, DCCG, DMCU, DML FPU watermark construction, BIOS spread-spectrum tables, link/service helpers, resource-pool bounding-box updates, and ASIC revision macros for DCN321 register layout.

## Risks And Edge Cases
Clock sequencing is order-sensitive: lowering DPPCLK requires DTO changes before refclk lowering, while raising requires refclk first. Dentist divider transitions to/from DID 127 need FIFO pixel add/drop workarounds. UCLK hard-min policy depends on pstate support and dc-mode softmax configuration. If DPM levels are missing, the code patches defaults and updates the bounding box. Several debug masks can suppress individual clock updates, making state comparisons harder.

## Test Signals
Test SMU version/header negotiation, fine-grained and discrete DPM queries, DPM-absent fallback patching, DCN32 versus DCN321 register paths, pstate lock/unlock for UCLK and FCLK, SubVP CAB num-ways changes, MCLK DMCUB ack enable/disable, DTBCLK switching, dentist override programming, auto-DPM logs, and memory-clock set/get hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c -->
