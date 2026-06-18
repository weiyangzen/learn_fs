# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_stream_encoder.h

## Purpose
This header defines the DCN32 stream encoder mask/shift surface and declares constructor plus FIFO/unblank helpers.

## Important APIs, Types, and Macros
`SE_COMMON_MASK_SH_LIST_DCN32(mask_sh)` maps DCN32 stream fields for DP pixel format and pixel-per-cycle mode, HDMI control/audio/generic-packet slots, DP secondary packets, DP M/N timing, metadata, DSC mode, Dolby Vision, `DIG_SYMCLK_FE_ON`, SDP splitting, clock pattern, and DIG FIFO control fields.

The public prototypes are `dcn32_dio_stream_encoder_construct`, `enc32_enable_fifo`, and `enc32_stream_encoder_dp_unblank`.

## Control Flow and State
No runtime flow is in the header. The macros drive generated register access used by the C file. The declared functions modify persistent DP/DIG/HDMI hardware register state.

## Dependencies and Integration Points
It includes DCN30 VPG/AFMT headers, `stream_encoder.h`, and DCN20 stream encoder helpers. DCN35 includes this header for reuse and compatibility.

## Risks and Test Signals
Risk is concentrated in field compatibility with the C implementation, especially FIFO and pixel-per-cycle fields. Test signals include compile coverage, DP unblank with FIFO enable, HDMI packet/audio programming, DSC mode readback, and dependent DCN35 build coverage.
