<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn35/dcn35_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn35/dcn35_clk_mgr.c

## Purpose
Implements the shared DCN35/DCN351 display clock manager. It manages SMU-backed clock programming, DTBCLK/DPP DTOs, watermark and DPM table exchange, spread-spectrum handling, low-power/IPS integration, DPIA host-router bandwidth notification, boot clock snapshots, and FPGA fallback behavior.

## Important APIs, Types, And Functions
- `dcn35_clk_mgr_construct` initializes the manager, allocates GART watermark and DPM buffers, handles DCN351 table translation, imports PMFW DPM data into bandwidth params, configures IPS capability flags, and sets function pointers.
- `dcn35_update_clocks` handles live DCFCLK, deep-sleep DCFCLK, DISPCLK, DPPCLK, DTBCLK, zstate, display idle, DPIA bandwidth, and DMCUB notification transitions.
- `dcn35_init_clocks`, `dcn35_are_clock_states_equal`, `dcn35_notify_wm_ranges`, `dcn35_set_low_power_state`, `dcn35_exit_low_power_state`, `dcn35_is_ips_supported`, and `dcn35_get_max_clock_khz` provide function-table operations.
- Internal helpers manage OTG-disable workarounds, DTB/DPP DTO programming, host-router bandwidth aggregation, VCO and clock register snapshots, spread-spectrum LUT reads, watermark construction, DPM import, and DCN351-to-DCN35 table translation.

## Control Flow
Construction sets default register tables unless DCN351 preseeded them, allocates PMFW-visible buffers, queries SMU, reads VCO and boot clocks, chooses DDR5/LPDDR5 watermarks, reads DPREF spread-spectrum state, imports a DPM table when pstate is enabled, and adjusts IPS config based on PMFW support/version. Runtime updates normalize DTBCLK requests, branch on `safe_to_lower` for zstate/DTB/mission-mode behavior, apply force-min DCFCLK, program hard-min DCFCLK and deep-sleep DCFCLK, floor DPPCLK, wrap DISPCLK changes with the OTG workaround, update DTB DTOs, sequence DPP DTO versus SMU DPPCLK according to lowering/raising, optionally notify host-router bandwidth per DPIA tunnel, and notify DMCUB.

## State And Persistence
Persistent state includes current clocks, `smu_present`, `smu_ver`, static `dcn35_bw_params`, `smu_wm_set`, boot snapshots, spread-spectrum fields, DTBCLK enable/ref frequency, IPS-related DC config changes, and DCCG DTO state. Temporary DPM buffers are freed after construction, while the watermark buffer persists until destruction.

## Dependencies And Integration Points
Integrates with DCN35 SMU helpers, DCCG DTO programming, DMCUB command submission, link service for 128b/132b and DPIA bandwidth, BIOS integrated memory info, DC debug/config flags, DCE/ DCN31 clock helpers, and DC resource-pool bandwidth bounding behavior through populated `clk_bw_params`.

## Risks And Edge Cases
OTG disable logic has several guards for diagnostic mode, HPO/128b132b links, stream changes with active DIG/FIFO, virtual signals, and missing link encoders; mistakes can cause blanking or underflow. DTBCLK disable can be gated by `allow_0_dtb_clk`, while enabling verifies a current-count register before persisting state. DPM import assumes valid memory pstate, FCLK, DCF, SOC, DISP, and DPP counts. The destroy path frees the watermark allocation as `FRAME_BUFFER` even construction used `GART`, which is a notable allocation-type consistency risk. DCN351 translation must stay aligned with both PMFW table layouts.

## Test Signals
Test DCN35 and DCN351 construction, SMU present/absent, DPM import and DCN351 translation, IPS supported/unsupported and old-PMFW config fallback, DDR5 versus LPDDR5 watermarks, DTBCLK zero/nonzero transitions, OTG workaround cases including HPO and virtual streams, DPIA host-router bandwidth notifications, DPPCLK lowering/raising order, DMCUB clock notify, and destroy-time memory cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn35/dcn35_clk_mgr.c -->
