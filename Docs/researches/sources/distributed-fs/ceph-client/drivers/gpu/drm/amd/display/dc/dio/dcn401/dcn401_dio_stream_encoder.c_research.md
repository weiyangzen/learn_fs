# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn401/dcn401_dio_stream_encoder.c

## Purpose
Implements the DCN401 stream encoder operations for DVI, HDMI, DisplayPort SST/MST-style stream setup, stream enablement, FIFO/input-mode programming, dynamic metadata, stream-to-link mapping, and DSC-related state readback. This is hardware-facing code: most behavior is register programming through the `REG_*` helpers, with the BIOS parser used for TMDS setup unless debug configuration requests direct programming.

## Important APIs, Types, And Functions
The constructor `dcn401_dio_stream_encoder_construct()` initializes a `struct dcn10_stream_encoder` instance and installs `dcn401_str_enc_funcs`. Public entry points include `enc401_stream_encoder_dvi_set_stream_attribute()`, `enc401_stream_encoder_hdmi_set_stream_attribute()`, `enc401_stream_encoder_dp_set_stream_attribute()`, `enc401_stream_encoder_dp_unblank()`, `enc401_stream_encoder_enable()`, `enc401_set_dynamic_metadata()`, `enc401_set_dig_input_mode()`, `enc401_stream_encoder_map_to_link()`, and `enc401_read_state()`. It depends on `struct dc_crtc_timing`, `struct encoder_unblank_param`, `enum signal_type`, and the DCN stream encoder register/shift/mask tables from the inherited DCN10/DCN30/DCN32/DCN35 stream encoder stack.

## Control Flow
DVI and HDMI setup optionally call VBIOS `encoder_control()` first, then program local stream attributes. HDMI setup configures deep color, scrambling above 340 MHz, general control/null/audio info packets, immediate audio info update, and AVMUTE state. DP setup translates timing and color-space state into `DP_PIXEL_FORMAT`, MSA colorimetry, MSA timing registers, and SDP splitting. DP unblank computes initial M/N video timing when a link rate is known, resets and enables DP steer FIFO and DIG FIFO in a specific order, then enables `DP_VID_STREAM_ENABLE` and emits a DP trace source sequence. Dynamic metadata toggles DME, DP metadata SDP, HDMI metadata packets, and Dolby Vision mode depending on `dynamic_metadata_mode`.

## State And Persistence
The file persists no heap or disk state. State lives in hardware registers and in the initialized `stream_encoder` object: context, BIOS pointer, engine id, VPG/AFMT pointers, register tables, masks, and stream encoder instance. `enc401_read_state()` snapshots DSC/PPS/VBID fields into `struct enc_state` for later logging. Timing calculations are transient and are not cached across calls.

## Dependencies And Integration Points
The stream encoder plugs into resource construction in DCN401 resource code and reuses lower-generation helpers such as `enc1_stream_encoder_*`, `enc3_*`, and `enc35_*`. It integrates with VBIOS, AFMT audio, VPG generic packet handling, link service DP trace hooks, DPCD source sequence definitions, and DC debug flags. Register access is abstracted through `reg_helper.h` and the stream encoder mask/shift tables declared in the matching header.

## Risks
The code assumes valid timing parameters and register tables; many invalid combinations are only protected by `ASSERT`. DP M/N math depends on `link_rate`, pixel clock, and pixel-per-container logic for YCbCr420 and DSC 4:2:2. FIFO reset ordering and wait timeouts are hardware-sensitive. HDMI audio setup asserts `enc->afmt`, so missing AFMT wiring is fatal in debug builds. Colorimetry handling intentionally leaves many newer color spaces as no-ops, relying on VSC SDP or other paths.

## Test Signals
Useful signals are successful mode set for HDMI/DVI/DP, no FIFO timeout during DP unblank, stable video after mode transitions, correct HDMI scrambling at and above 340 MHz, correct DP MSA values for RGB/YCbCr/DSC/interlace timings, audio info packet emission, dynamic metadata packet emission for DP/HDMI/Dolby Vision, and `enc401_read_state()` logs matching expected DSC state. Compile coverage should catch missing register fields or function pointer signature drift.
