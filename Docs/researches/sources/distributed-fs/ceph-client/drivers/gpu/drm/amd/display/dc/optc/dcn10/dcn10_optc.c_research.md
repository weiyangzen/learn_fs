# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn10/dcn10_optc.c

## Purpose
`dcn10_optc.c` implements the base DCN timing generator/OPTC behavior. It programs mode timing, global sync, VTG parameters, CRTC enable/disable, blanking, clocks, update locks, reset triggers, dynamic refresh rate, test patterns, stereo, CRC, underflow handling, and hardware state readback.

## Important APIs, types, and functions
Major APIs include `optc1_program_timing()`, `optc1_program_global_sync()`, vertical interrupt setup functions, `optc1_enable_crtc()`, `optc1_disable_crtc()`, `optc1_enable_optc_clock()`, `optc1_set_blank()`, `optc1_validate_timing()`, lock/unlock helpers, reset-trigger helpers, `optc1_set_drr()`, `optc1_set_vtotal_min_max()`, `optc1_get_crtc_scanoutpos()`, stereo helpers, `optc1_read_otg_state()`, `optc1_get_hw_timing()`, CRC configure/read helpers, `optc1_is_two_pixels_per_container()`, and `dcn10_timing_generator_init()`.

## Control flow
Mode programming copies and patches timing to enforce front-porch minimums, writes H/V totals, sync widths, blank start/end, sync polarities, interlace state, VTG state, global sync, data format, and horizontal timing division for 4:2:0 or ODM-like cases. Enable selects the OPTC source, enables VTG, and turns on OTG master enable through a register sequence. Disable clears master enable, disables VTG, and waits for OTG not busy. DRR writes mid/min/max totals and selectors, then configures manual trigger. CRC configuration validates that the timing generator is enabled, programs windows per engine, and enables continuous or one-shot CRC.

## State and persistence behavior
`struct optc` stores cached timing parameters such as vready/vstartup/vupdate and original patched timing, plus capability bounds initialized from masks. Hardware state is in OTG, VTG, OPTC input, CRC, and trigger registers. There is no durable persistence.

## Dependencies and integration points
The file depends on `reg_helper`, `dcn10_optc.h`, `dc.h`, tracing, timing-generator interfaces, DC timing/color enums, and register sequence helpers. It is the base function-table provider reused by DCN20, DCN201, DCN30, and DCN301.

## Risks and edge cases
Timing arithmetic is sensitive to off-by-one hardware conventions. Interlace validation is blocked even though some programming paths contain interlace handling. `vstartup_start == 0` triggers debugger break. Underflow is cleared during unblank as a test workaround, which can hide transient events. CRC is unavailable while the CRTC is disabled. Manual trigger and reset-trigger programming depends on correct source pipe and edge polarity.

## Test signals
Mode validation and programming across common timings, DP/HDMI/eDP signals, 4:2:0 and DSC 4:2:2 native timing division, CRTC enable/disable and blank/unblank, vblank counter/scanout position, DRR min/max/mid updates, CRC window capture, stereo modes, reset synchronization, and underflow clear/readback are key tests.
