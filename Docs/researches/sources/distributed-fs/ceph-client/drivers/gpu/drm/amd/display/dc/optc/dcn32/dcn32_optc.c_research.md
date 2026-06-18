# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn32/dcn32_optc.c

## Purpose
Implements DCN 3.2 OPTC operations, extending the DCN31/DCN314 model with ODM segment query/wait support, DMUB-assisted DRR manual trigger for FAMS/memory-clock switching, phantom OTG disable, and richer double-buffer pending hooks.

## Important APIs, Types, and Functions
Public functions are `dcn32_timing_generator_init()`, `optc32_set_h_timing_div_manual_mode()`, `optc32_get_odm_combine_segments()`, `optc32_set_odm_bypass()`, and `optc32_wait_odm_doublebuffer_pending_clear()`. Static generation-specific functions include `optc32_set_odm_combine()`, enable/disable, phantom helpers, `optc32_setup_manual_trigger()`, and `optc32_set_drr()`.

## Control Flow and State
ODM combine uses the 2048-pixel memory-count scheme and programs memory mask, segment sources, segment width, horizontal timing division, and `opp_count`. Segment readback converts `OPTC_NUM_OF_INPUT_SEGMENT` values 0, 1, and 3 into 1, 2, and 4 segments, treating value 2 as invalid. Disable clears ODM source/memory, disables OTG/VTG, and waits longer than DCN31 for `OTG_BUSY`. DRR sets min/max and optional midpoint, then either sends a DMUB manual-trigger command when `mclk_sw` is supported and FAMS is enabled, or programs TRIGA mask bits locally.

## Dependencies and Integration Points
Depends on `dc_dmub_srv.h` for DMUB commands and on DCN31 readback helpers. The vtable wires shared DCN3 helpers for locks, DSC, GSL, pending status, and timing readback. Resource code selects this init for DCN32-family OPTCs.

## Risks and Test Signals
Risks include disagreement between software ODM segment count and register encoding, DMUB capability gating for DRR, and timeouts on ODM double-buffer pending. Tests should include FAMS enabled/disabled VRR transitions, ODM combine and bypass, phantom pipe teardown, and update-pending polling under rapid mode updates.
