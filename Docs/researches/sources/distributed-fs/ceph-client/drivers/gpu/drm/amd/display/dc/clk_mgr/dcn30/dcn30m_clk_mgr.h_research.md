<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30m_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30m_clk_mgr.h

## Purpose

`dcn30m_clk_mgr.h` declares the mobile DCN30 SmartMux clock-manager callback.

## Important APIs, Types, And Functions

It exports `uint32_t dcn30m_set_smartmux_switch(struct clk_mgr *clk_mgr_base, uint32_t pins_to_set)`.

## Control Flow

No runtime flow exists. The implementation sends a DALSMC SmartAccess message through the mobile SMU helper.

## State And Persistence Behavior

The header owns no state. Runtime state is PMFW/platform SmartMux state.

## Dependencies And Integration Points

It is included by DCN30 main clock-manager code to install the SmartMux callback.

## Risks

Signature drift or missing declaration breaks the callback table. No enum is provided for `pins_to_set`, so semantic validation is external.

## Test Signals

Build coverage and SmartMux runtime tests on DCN30 mobile systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30m_clk_mgr.h -->
