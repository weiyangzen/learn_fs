# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn314/dcn314_optc.c

## Purpose
Implements DCN 3.14 timing-generator behavior. It derives from DCN31 but changes ODM memory allocation for the DCN314 memory organization and uses a compact vtable tailored to this ASIC generation.

## Important APIs, Types, and Functions
The public function is `dcn314_timing_generator_init()`. Static overrides are `optc314_set_odm_combine()`, `optc314_enable_crtc()`, `optc314_disable_crtc()`, `optc314_phantom_crtc_post_enable()`, `optc314_set_odm_bypass()`, and `optc314_set_h_timing_div_manual_mode()`. The vtable also imports `optc31_immediate_disable_crtc()`, `optc31_set_drr()`, `optc3_init_odm()`, and DCN31 readback helpers.

## Control Flow and State
ODM combine computes active width as `segment_width * opp_cnt`, derives an ODM memory count in 2048-pixel chunks, and selects memory bitmasks for two or four OPP paths. It programs `OPTC_DATA_SOURCE_SELECT`, `OPTC_WIDTH_CONTROL`, and `OTG_H_TIMING_CNTL`, then updates `optc1->opp_count`. Enable and disable mirror the DCN31 flow, but disable does not clear ODM source/memory registers and does not clear underflow in this file. Phantom enable immediately disables the OTG and waits for busy to clear. ODM bypass selects the local OPTC instance, masks unused segments, restores horizontal timing division from pixel-container mode, clears ODM memory, and records one OPP.

## Dependencies and Integration Points
Includes DCN30 and DCN31 OPTC headers for shared implementations, `reg_helper.h` for MMIO access, and `dc.h`. Its vtable is selected by DCN314 resource initialization and participates in the same Display Core `timing_generator` polymorphic API as older generations.

## Risks and Test Signals
Risk areas are the memory mask thresholds for 4K/8K/12K paths, the less aggressive disable sequence compared with DCN31/DCN32, and manual horizontal timing division control. Tests should cover single-pipe bypass, ODM 2:1/4:1, phantom pipe enable/disable, VRR/DRR via inherited DCN31 logic, and mode-set teardown on real DCN314 hardware.
