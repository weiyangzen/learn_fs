# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_stream_encoder.h

## Purpose
This header exposes the DCN30 DIO stream encoder register/mask surface and shared `enc3_*` helper prototypes. Later stream encoder implementations include it to reuse HDMI/DP packet, DSC PPS, and audio behavior.

## Important APIs, Types, and Macros
`SE_DCN3_REG_LIST(id)` lists the DCN30 DIG, HDMI, DP, AFMT, DME, metadata, DSC, FIFO-status, and clock-pattern registers. `SE_COMMON_MASK_SH_LIST_DCN30(mask_sh)` maps fields for DP pixel format, HDMI control, generic HDMI packet slots 0-14, MST rate, DP secondary packets, DP stream enable/status, DP VID M/N, DIG start/source, HDMI/DP audio, DSC, metadata, Dolby Vision, FIFO diagnostics, SDP splitting, and clock pattern. The file also defines compatibility bit names for RDPCSTX/DPCSTX fields whose names changed.

Public prototypes include `dcn30_dio_stream_encoder_construct`, HDMI packet update/stop helpers, DP SDP update helpers, AFMT/audio wrappers, DSC PPS programming, and single HDMI packet update.

## Control Flow and State
No runtime flow is defined here. Its macros produce register access tables used by `REG_UPDATE`, `REG_GET`, and `REG_SET` in DCN30 and descendant implementations. State is DIG/DP/HDMI/AFMT/DME hardware state.

## Dependencies and Integration Points
The header includes `dcn30_vpg.h`, `dcn30_afmt.h`, `stream_encoder.h`, and `dcn20_stream_encoder.h`. It is used by DCN30, DCN314, DCN32, and DCN35 stream encoder C files and headers.

## Risks and Test Signals
Risk lies in large mask-list drift: missing packet, DSC, FIFO, or audio fields can break dependent generations. Test signals include full compile coverage, HDMI packet slots 8-14, DP GSP11 PPS, dynamic metadata, DP audio, HDMI audio, FIFO diagnostics, and any ASIC-specific register-generation tests.
