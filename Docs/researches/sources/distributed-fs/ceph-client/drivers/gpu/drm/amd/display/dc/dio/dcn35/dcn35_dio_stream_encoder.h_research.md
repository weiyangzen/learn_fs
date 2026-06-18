# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn35/dcn35_dio_stream_encoder.h

## Purpose
This header defines the DCN35 stream encoder register and mask/shift contract and exposes the DCN35 constructor plus FIFO control functions.

## Important APIs, Types, and Macros
`SE_DCN35_REG_LIST(id)` extends the DCN314-like DP/HDMI/AFMT/DME register set with `DIG_FE_EN_CNTL`, `DIG_FE_CLK_CNTL`, `DIG_FIFO_CTRL0`, and `STREAM_MAPPER_CONTROL`. `SE_COMMON_MASK_SH_LIST_DCN35(mask_sh)` maps DP pixel-per-cycle, HDMI control including TMDS pixel/color format fields, generic packet slots, DP secondary packets, metadata, DSC, DIG FE enable/mode/clock fields, FIFO fields, and stream mapper target.

The public APIs are `dcn35_dio_stream_encoder_construct`, shared DCN30 packet/audio helpers, `enc3_dp_set_dsc_pps_info_packet`, `enc35_disable_fifo`, and `enc35_enable_fifo`.

## Control Flow and State
The header defines no runtime flow. It provides the register/mask data needed by DCN35 stream functions to persist frontend clock, FIFO, stream mapping, HDMI, DP, packet, metadata, and audio state in hardware.

## Dependencies and Integration Points
It includes DCN30 VPG/AFMT, generic stream encoder, and DCN20 stream encoder headers. The implementation also relies on DCN314/32 helpers, so this header is part of a multi-generation composition.

## Risks and Test Signals
Risks include changed field locations for TMDS pixel/color format and Dolby Vision relative to earlier generations, plus new FE clock/enable and stream-mapper fields. Test signals include compile coverage, HDMI YCbCr422 field programming, FE clock/fifo enable behavior, stream mapping, DP unblank, metadata packets, and DSC PPS handling.
