# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn20/dcn20_stream_encoder.h

## Purpose
This header defines the DCN2 stream-encoder register surface and exported helper prototypes that later DIO stream encoders build on. It does not implement runtime control flow; its main role is to bind the generic `stream_encoder` and `dcn10_stream_encoder` abstractions to DCN2-specific registers, masks, and stream helper functions.

## Important APIs, Types, and Macros
`SE_DCN2_REG_LIST(id)` extends common stream encoder registers with HDMI generic packet controls, DP DSC controls, dynamic metadata (`DME_CONTROL`, `DP_SEC_METADATA_TRANSMISSION`, `HDMI_METADATA_PACKET_CONTROL`), and `DP_SEC_FRAMING4`. `SE_COMMON_MASK_SH_LIST_DCN20(mask_sh)` adds field mappings for HDMI packet slots 0-7, DSC mode/slice/bytes-per-pixel, VBID6 PPS timing, metadata engine fields, Dolby Vision enable, DP pixel combine, adaptive-sync SDP line programming, and SDP splitting.

The exported functions are `dcn20_stream_encoder_construct`, `enc2_stream_encoder_dp_set_stream_attribute`, `enc2_stream_encoder_dp_unblank`, `enc2_set_dynamic_metadata`, and `enc2_get_fifo_cal_average_level`. Later DCN30+ implementations reuse these function pointers for DP stream attributes, DP unblank behavior in some generations, dynamic metadata, and FIFO diagnostics.

## Control Flow and State
No executable control flow lives here. The macros become compile-time initializers for per-instance register tables and mask/shift tables. The persistent state affected by functions declared here is hardware state in DIG/DP/DME blocks, reached through implementations elsewhere.

## Dependencies and Integration Points
The file depends on `stream_encoder.h` and `dcn10/dcn10_stream_encoder.h`. It is included by DCN30, DCN314, DCN32, and DCN35 stream encoder headers, making this header a compatibility bridge between DCN1 base helpers and DCN2+ metadata/DSC behavior.

## Risks and Test Signals
Risk is concentrated in register-field accuracy: any renamed or omitted mask entry breaks later `REG_UPDATE`/`REG_GET` users at compile time or, worse, writes the wrong hardware field. Useful test signals are kernel build coverage for generated register tables, DP DSC enable/disable, HDR metadata on DP/HDMI, adaptive-sync SDP line placement, Dolby Vision metadata, and FIFO average-level reporting on DCN2-derived encoders.
