# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn42/dcn42_dio_stream_encoder.h

## Purpose
Defines the DCN42 stream encoder register field list and public DCN42 stream encoder entry points. The header gives resource construction and inherited helper code access to DCN42 stream, packet, audio, metadata, FIFO, and mapper registers.

## Important APIs, Types, And Functions
`SE_COMMON_MASK_SH_LIST_DCN42(mask_sh)` enumerates DP pixel format, HDMI control/VBI/audio/ACR, DP MSE/secondary packets, DP video timing, generic packet slots, DSC PPS/VBID, DME metadata, DIG frontend enable/clock, FIFO, stream mapping, and APG audio fields. It declares `dcn42_dio_stream_encoder_construct()`, `enc42_se_enable_audio_clock()`, and `enc42_reset_hdmi_stream_attribute()`.

## Control Flow
No runtime control flow exists in the header. Runtime behavior is installed by the constructor in the C file, and the macro drives compile-time register shift/mask table creation.

## State And Persistence
The file stores no state. It describes register field access; constructed stream encoder instances keep context, BIOS, VPG/APG, register table, shift table, and mask table pointers.

## Dependencies And Integration Points
Includes DCN30 VPG, `stream_encoder.h`, and DCN20 stream encoder definitions. Resource code and DCN42 stream implementation depend on the macro matching generated hardware register names, especially for APG fields added relative to DCN401.

## Risks
Field omissions or wrong register variants break DCN42 stream functionality at build time or runtime. The header intentionally differs from DCN401 in audio-line register placement and APG fields; accidental reuse of DCN401 assumptions can break HDMI audio/infoframe programming. Generic packet field coverage must stay aligned with VPG slot use.

## Test Signals
Compile DCN42 with full register headers, run HDMI/DP mode sets, enable/disable APG audio, update HDMI generic info packets, send DSC PPS packets, and verify stream-to-link/FIFO paths inherited from DCN401 still program valid DCN42 fields.
