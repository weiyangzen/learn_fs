# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_stream_encoder.c

## Purpose
This file implements the DCN32 stream encoder, adapting the DCN30 stream path for newer DP pixel-per-cycle and FIFO behavior while retaining common DCN30 packet/audio support.

## Important APIs and Functions
`enc32_dp_set_odm_combine` writes `DP_PIXEL_PER_CYCLE_PROCESSING_MODE`. DVI/HDMI attribute setup mirrors DCN30 but notes that `DIG_START` is removed from the register spec and does not reset FIFO through that path. HDMI setup programs deep color, scrambling, general control, audio infoframe, and AVMUTE.

`enc32_stream_encoder_dp_unblank` computes DP M/N from timing and link rate, sets `DP_VID_N_MUL` and pixel-per-cycle mode for YCbCr420, DSC YCbCr422 non-simple, multiple OPPs, or `param->pix_per_cycle > 1`, disables DP stream, resets steer FIFO, waits for `DIG_SYMCLK_FE_ON`, programs FIFO read level, resets DIG FIFO with wait-for-done both ways, enables FIFO, delays, then enables DP video stream and traces source sequence.

`enc32_dp_set_dsc_config` only toggles DSC mode because bytes-per-pixel and slice-width registers were removed. `enc32_read_state` reads only remaining DSC/PPS state. `enc32_set_dig_input_mode`, `enc32_reset_fifo`, and `enc32_enable_fifo` manage DIG FIFO output pixel mode and reset/enable sequencing.

## Control Flow
The DCN32 function table keeps DCN30 packet/audio helpers, DCN2 DP stream attributes, and dynamic metadata, but overrides DP unblank, HDMI/DVI setup, DSC config/readback, input mode, and FIFO enable. There is no FIFO disable hook in the table.

## State and Persistence
Persistent state includes DP stream enable/status, DP VID M/N timing, DP pixel-per-cycle mode, DIG FIFO enable/reset/read-level/output mode, DSC mode, GSP11 PPS state, HDMI control registers, and AFMT audio state.

## Dependencies and Integration Points
Dependencies include DCN30 stream helper prototypes, `link_service` DP trace, `dpcd_defs`, VBIOS encoder control, `reg_helper`, and generic stream encoder contracts. Integration is via `struct stream_encoder_funcs` during DP/HDMI/DVI programming.

## Risks and Test Signals
Risks include FIFO wait timeouts if `DIG_SYMCLK_FE_ON` never asserts, wrong pixel-per-cycle handling for DSC/ODM/pix-per-cycle >1, and missing direct-programming FIFO reset in HDMI/DVI paths. Tests should cover DP unblank at standard and high pixel-per-cycle modes, DSC mode toggling, FIFO reset wait paths, HDMI scrambling/deep color, info packet reuse from DCN30, and DP trace sequencing.
