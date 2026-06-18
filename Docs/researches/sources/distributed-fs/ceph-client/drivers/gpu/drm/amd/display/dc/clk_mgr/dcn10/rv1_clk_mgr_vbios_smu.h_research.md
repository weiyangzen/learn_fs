<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv1_clk_mgr_vbios_smu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv1_clk_mgr_vbios_smu.h

## Purpose

`rv1_clk_mgr_vbios_smu.h` declares the Raven1 VBIOS-SMU DISPCLK setter used by the RV1 clock-manager implementation.

## Important APIs, Types, And Functions

It exports `int rv1_vbios_smu_set_dispclk(struct clk_mgr_internal *clk_mgr, int requested_dispclk_khz)`. The function returns the actual DISPCLK in kHz as reported by SMU.

## Control Flow

The header has no runtime flow. It enables `rv1_clk_mgr.c` to install `rv1_vbios_smu_set_dispclk()` in the internal clock-manager function table.

## State And Persistence Behavior

No state is owned by the header. The implementation changes MP1 mailbox registers and may update DMCU PSR wait-loop state.

## Dependencies And Integration Points

It depends on `struct clk_mgr_internal` being visible to includers. The integration point is the clock-manager internal `.set_dispclk` hook.

## Risks

The header exposes only DISPCLK, so adding other RV1 SMU message helpers requires synchronized declarations. Prototype mismatch with the C implementation would cause build or call ABI failures.

## Test Signals

Build coverage verifies declaration consistency. Runtime validation belongs to RV1 DISPCLK changes and SMU mailbox tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv1_clk_mgr_vbios_smu.h -->
