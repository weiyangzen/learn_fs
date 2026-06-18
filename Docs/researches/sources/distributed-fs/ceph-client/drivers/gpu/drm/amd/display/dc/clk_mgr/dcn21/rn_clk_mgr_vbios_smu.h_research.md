<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn21/rn_clk_mgr_vbios_smu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn21/rn_clk_mgr_vbios_smu.h

## Purpose

`rn_clk_mgr_vbios_smu.h` declares the Renoir VBIOS-SMU helper API consumed by `rn_clk_mgr.c`.

## Important APIs, Types, And Functions

It forward-declares `enum dcn_pwr_state` and declares SMU helpers for version query, DISPCLK, DCFCLK hard-min/deep-sleep, PHYCLK, DPPCLK, DCN power state, 48 MHz refclk power-down, PME workaround, and periodic retraining status.

## Control Flow

There is no runtime flow in the header. It defines the callable mailbox surface used by Renoir clock update and construction paths.

## State And Persistence Behavior

The header owns no state. Implementations persist effects in PMFW clock/power state, MP mailbox registers, and DMCU timing.

## Dependencies And Integration Points

It integrates the Renoir clock manager with PMFW without exposing register-level details to the policy file.

## Risks

All declarations depend on `struct clk_mgr_internal` visibility from includers. Adding new SMU messages requires updating both this header and the implementation.

## Test Signals

Build coverage for prototype consistency; runtime SMU-message tests through `rn_clk_mgr.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn21/rn_clk_mgr_vbios_smu.h -->
