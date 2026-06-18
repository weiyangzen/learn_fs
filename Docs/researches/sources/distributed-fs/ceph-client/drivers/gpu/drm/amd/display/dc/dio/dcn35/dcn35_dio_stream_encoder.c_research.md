# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn35/dcn35_dio_stream_encoder.c

## Purpose
This file implements the DCN35 stream encoder, combining DCN314/32 stream behavior with a newer DIG frontend clock/enable model, stream-to-link mapping, HDMI TMDS format fields, and pixel-per-cycle readback.

## Important APIs and Functions
DVI setup mirrors DCN32 direct/VBIOS behavior. HDMI setup mirrors DCN30/314 but enables FIFO in direct mode, sets `TMDS_PIXEL_ENCODING` for YCbCr422, and clears `TMDS_COLOR_FORMAT`. `enc35_stream_encoder_enable` programs `DIG_FE_MODE` for DVI, HDMI, DP SST, DP MST, eDP, and virtual streams when enabling.

`enc35_stream_encoder_dp_unblank` computes DP M/N and pixel-per-cycle like DCN32, disables DP stream, resets steer FIFO, delays, enables DP stream, then calls `enc314_enable_fifo`. `enc35_stream_encoder_map_to_link` writes `DIG_STREAM_LINK_TARGET` in `STREAM_MAPPER_CONTROL`. `enc35_reset_fifo`, `enc35_enable_fifo`, `enc35_disable_fifo`, and `enc35_is_fifo_enabled` use `DIG_FE_CLK_CNTL`/`DIG_FE_EN_CNTL` and `DIG_FIFO_CTRL0`; FIFO enable turns on FE clock and FE enable before reset, while disable clears FIFO, FE enable, and FE clock. `enc35_get_pixels_per_cycle` maps FIFO output pixel mode to 1 or 2.

## Control Flow
The DCN35 function table reuses DCN314 ODM combine, blank, input mode, DSC config/readback, and DCN30 packet/audio helpers. It overrides HDMI/DVI setup, DP unblank, stream enable, FIFO hooks, stream-to-link mapping, and pixels-per-cycle query. Constructor is standard pointer assignment.

## State and Persistence
Persistent state includes DIG FE mode/clock/enable, FIFO reset/enable/read-level/output pixel mode, stream-to-link mapping, DP stream enable/status, DP VID M/N timing, HDMI TMDS encoding/color fields, DSC mode, packet state, and AFMT audio state.

## Dependencies and Integration Points
Dependencies include DCN30, DCN314, and DCN32 stream headers, `link_service`, `dpcd_defs`, VBIOS encoder control, AFMT/VPG helpers, and generic stream encoder function tables. Integration points include link mapping for decoupled stream/link encoders and DP trace sequencing.

## Risks and Test Signals
Risks include mixing `enc314_enable_fifo` in DP unblank while DCN35 has its own FE-clock-aware FIFO routine, stream-to-link assertion limits of `<5`, FE clock/enable sequencing, and HDMI YCbCr422 TMDS field changes. Tests should cover DP unblank and FIFO enable/disable, stream-to-link mapping for all valid instances, DP/HDMI/DVI frontend mode programming, pixels-per-cycle readback, HDMI YCbCr422, DSC, packet/audio reuse, and blank-time FIFO disable through DCN314 blank hook.
