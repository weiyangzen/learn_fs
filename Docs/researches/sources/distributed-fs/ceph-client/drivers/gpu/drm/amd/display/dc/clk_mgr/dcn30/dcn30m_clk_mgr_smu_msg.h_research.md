<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30m_clk_mgr_smu_msg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30m_clk_mgr_smu_msg.h

## Purpose

`dcn30m_clk_mgr_smu_msg.h` declares the mobile DCN30 SmartMux SMU message helper.

## Important APIs, Types, And Functions

It forward-declares `struct clk_mgr_internal` and exports `dcn30m_smu_set_smart_mux_switch()`.

## Control Flow

There is no runtime flow. The declaration is used by `dcn30m_clk_mgr.c`.

## State And Persistence Behavior

No state is owned. The implementation modifies PMFW SmartMux state through DALSMC.

## Dependencies And Integration Points

It includes `core_types.h` for fixed-width types and connects the mobile clock-manager wrapper to the mailbox implementation.

## Risks

The API exposes raw pin bits rather than a typed enum. Declaration drift breaks SmartMux callback builds.

## Test Signals

Build coverage and SmartMux SMU command execution tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30m_clk_mgr_smu_msg.h -->
