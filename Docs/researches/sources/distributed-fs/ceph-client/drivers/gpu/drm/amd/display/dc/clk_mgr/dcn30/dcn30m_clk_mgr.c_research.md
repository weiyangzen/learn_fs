<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30m_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30m_clk_mgr.c

## Purpose

`dcn30m_clk_mgr.c` is the small mobile DCN30 SmartMux bridge. It exposes a clock-manager callback that sends SmartMux switch requests to SMU.

## Important APIs, Types, And Functions

The exported function is `dcn30m_set_smartmux_switch(struct clk_mgr *clk_mgr_base, uint32_t pins_to_set)`. It converts the public `clk_mgr` to `clk_mgr_internal` and calls `dcn30m_smu_set_smart_mux_switch()`.

## Control Flow

There is one straight-line call path from DC clock-manager function table `.set_smartmux_switch` to the DCN30M SMU message helper. The return value from SMU is passed back to the caller.

## State And Persistence Behavior

This file owns no state. SmartMux pin/switch state is maintained by PMFW/platform hardware after the SMU message.

## Dependencies And Integration Points

It depends on `clk_mgr_internal`, `dcn30m_clk_mgr.h`, and `dcn30m_clk_mgr_smu_msg.h`. DCN30's main function table points `.set_smartmux_switch` at this helper.

## Risks

There is no local validation of `pins_to_set`, so correctness depends on callers and PMFW. If the active platform does not support SmartMux, failures are only visible through the SMU response.

## Test Signals

SmartMux switch requests on mobile platforms, SMU response validation, and negative tests for unsupported pins or unsupported firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30m_clk_mgr.c -->
