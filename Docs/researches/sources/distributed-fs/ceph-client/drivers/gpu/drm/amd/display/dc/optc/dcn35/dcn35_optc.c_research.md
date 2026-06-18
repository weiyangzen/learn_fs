# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn35/dcn35_optc.c

## Purpose
Implements DCN 3.5 OPTC operations. It builds on DCN32 with enhanced CRC support, long-vtotal handling, fine-grain clock-gating control, stronger disable wait semantics, and defensive null/function checks around DRR paths.

## Important APIs, Types, and Functions
Public APIs are `dcn35_timing_generator_init()`, `dcn35_timing_generator_set_fgcg()`, `optc35_set_drr()`, `optc35_set_long_vtotal()`, `optc35_configure_crc()`, and `optc35_wait_otg_disable()`. Static functions include `optc35_set_odm_combine()`, enable/disable, phantom post-enable, `optc35_get_crc()`, and manual-trigger setup.

## Control Flow and State
The ODM path follows DCN32 memory allocation and records `opp_count`. Disable clears ODM mappings and memory, disables OTG/VTG, waits for both `OTG_BUSY` and `OTG_CURRENT_MASTER_EN_STATE`, then clears underflow. CRC configuration rejects disabled CRTCs, clears/reset controls when requested, programs per-engine window A/B boundaries, enables optional CRC window double buffering, and writes polynomial mode when available. CRC readback selects CRC32 registers when all CRC32 masks exist, otherwise uses legacy 16-bit result registers. DRR programs min/max/mid and uses DMUB manual-trigger commands when memory-clock switching is active; long-vtotal splits very large vertical totals across `OTG_V_COUNT_STOP_CONTROL` and `OTG_V_COUNT_STOP_CONTROL2`.

## Dependencies and Integration Points
Includes DCN31/DCN32 headers and `dc_dmub_srv.h`. The vtable reuses DCN32 ODM bypass/manual-mode helpers, DCN31 readback, and DCN3 base helpers. Initialization sets timing limits, `max_frame_count`, and OPTC fine-grain clock gating based on `dc->debug.enable_fine_grain_clock_gating.bits.optc`.

## Risks and Test Signals
Risks include CRC32/CRC16 capability detection via nonzero masks, long-vtotal edge cases where min exceeds max hardware count, FAMS/DMUB trigger behavior, and clock-gating side effects. Test signals include CRC engine 0/1 captures, CRC polynomial selection on DCN3.6-style masks, VRR and long-vblank modes, ODM 2:1/4:1, and disable underflow cleanup.
