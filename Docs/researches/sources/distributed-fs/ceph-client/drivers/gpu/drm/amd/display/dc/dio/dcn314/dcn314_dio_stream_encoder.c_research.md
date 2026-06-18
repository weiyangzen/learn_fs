# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn314/dcn314_dio_stream_encoder.c

## Purpose
This file implements the DCN314 stream encoder, a DCN30-derived stream encoder with explicit DIG FIFO control and revised DP unblank/DSC behavior for newer register definitions.

## Important APIs and Functions
`enc314_reset_fifo`, `enc314_enable_fifo`, `enc314_disable_fifo`, and `enc314_is_fifo_enabled` control `DIG_FIFO_CTRL0`, wait on `DIG_FIFO_RESET_DONE` when `DIG_SYMCLK_FE_ON` is active, and program read-start level `0x7`. `enc314_dp_set_odm_combine` uses `DP_PIXEL_PER_CYCLE_PROCESSING_MODE` rather than the older `DP_PIXEL_COMBINE`.

The DVI and HDMI attribute functions mirror DCN30 VBIOS/direct setup but call `enc314_enable_fifo` when direct programming is used. HDMI setup repeats DCN30 deep-color, scrambling, audio-infoframe, and AVMUTE programming. `enc314_stream_encoder_dp_blank` can disable FIFO after DP video stream disable when `debug.dig_fifo_off_in_blank` is set. `enc314_stream_encoder_dp_unblank` computes initial M/N, handles 4:2:0, DSC 4:2:2, and ODM/OPP combining, disables DP video, resets steer FIFO, enables DP stream, then explicitly enables the DIG resync FIFO.

`enc314_dp_set_dsc_config` only toggles `DP_DSC_MODE` because bytes-per-pixel and slice-width registers were removed in newer hardware. `enc314_read_state` omits removed DSC fields. `enc314_set_dig_input_mode` maps a two-pixel container to `DIG_FIFO_OUTPUT_PIXEL_MODE`.

## Control Flow
The DCN314 function table keeps DCN30 packet/audio helpers but overrides HDMI/DVI attributes, DP blank/unblank, ODM combine, DSC config/readback, FIFO hooks, and input mode. Constructor initialization follows the standard stream encoder pointer assignment pattern.

## State and Persistence
Persistent state includes DIG FIFO enable/reset/read-level, DP stream enable/status, DP VID M/N timing, DP pixel-per-cycle mode, DSC mode, PPS packet registers, HDMI controls, AFMT audio state, and debug-flag-driven FIFO state across blank/unblank.

## Dependencies and Integration Points
The file depends on DCN30 stream helpers, `link_service` for DP trace sequencing, `dpcd_defs`, VBIOS encoder control, AFMT/VPG callbacks, and DC debug flags. It integrates with link programming through the `stream_encoder_funcs` table.

## Risks and Test Signals
Risks center on FIFO sequencing: enabling too early or disabling at blank can corrupt video if clocks are not stable. Removed DSC fields require callers not to rely on bytes-per-pixel/slice-width writes. Tests should cover DP unblank with 1/2 pixels per cycle, ODM/OPP >1, DSC 4:2:2 simple and non-simple, `dig_fifo_off_in_blank`, HDMI direct and VBIOS setup, FIFO reset wait when symclk is off, and DSC state readback.
