# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 44192-46599

## Scope And Purpose

This chunk is part of AMD's generated DCN 3.1.4 ASIC register shift/mask header. It contains C preprocessor constants for hardware bitfields: `<REGISTER>__<FIELD>__SHIFT` gives the bit position and `<REGISTER>__<FIELD>_MASK` gives the 32-bit field mask. The companion `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h` supplies the matching `reg*` register addresses and base indices.

The range starts in the middle of the DisplayPort 3 PHY-symbol block, covers the rest of the `DP3` stream/security/audio/metadata sideband fields, then covers the `VPG4`, `AFMT4`, `DME4`, and `DIG4` blocks. It ends in the `DP4` block after `DP4_DP_ALPM_CNTL`; the following chunk continues with later DP4 fields. There are no functions, structs, branches, or direct side effects in this source. The runtime behavior comes from AMD display code that binds these generated masks and shifts into register tables and uses `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_READ`, and `REG_WAIT` helpers.

## Register Blocks Covered

The `DP3` tail covers DisplayPort PHY and stream-side control for the fourth DIO stream encoder instance:

- PHY symbol/test controls: `DP_DPHY_SYM1`, `DP_DPHY_SYM2`, 8b/10b reset/disparity controls, PRBS generation, scrambler control, CRC enable/control/result, MST CRC phase status, HBR2 patterns, byte/stream swap controls, and fast-training request/status.
- Secondary-data-packet controls: `DP_SEC_CNTL`, `DP_SEC_CNTL1` through `DP_SEC_CNTL7`, `DP_GSP8_CNTL` through `DP_GSP11_CNTL`, GSP double-buffer enable status, and metadata transmission fields.
- Audio and timing payload fields: DP audio M/N read/write registers, timestamp mode/count, packet control, MSE rate and allocation table fields, MSA timing parameters, VBID/misc override fields, MSO controls, DSC mode selection, and DP double-buffer control.
- Link power and low-power fields: `DP_ALPM_CNTL` and `DP_AUXLESS_ALPM_CNTL1` through `DP_AUXLESS_ALPM_CNTL5` for main-link sleep/standby, AUX-less ALPM enable/status/CRC/mask/timeout/ignore controls, and FEC/PHY sleep sequence state.

The `VPG4` block is the video packet generator for the same DIO instance. It defines indexed generic-packet data access, frame-update and immediate-update bits for generic packets 0 through 14, lock/conflict status and clear fields, GSP memory power state, ISRC 1/2 indexed data, and MPEG info packet bytes.

The `AFMT4` block is the audio format/infoframe block. It defines VBI and audio packet controls, audio channel/layout/sample-send fields, audio infoframe payload bytes, IEC 60958 channel-status packing for channels 0 through 7, CRC controls/results, ramp-generator controls, AFMT status and interrupts, audio source select, and AFMT memory-power fields.

The `DME4` block exposes metadata engine enable, HUBP requestor, stream type, MSI routing, and memory power state for dynamic metadata packet handling.

The `DIG4` block covers the front-end digital stream encoder and HDMI/TMDS path. It includes DIG source selection, FE enable, DVI/HDMI/DP output selection, stereosync, Dolby Vision enable, symclk FE status, output CRC controls/results, clock/test/random patterns, FIFO controls, HDMI metadata packet controls, HDMI core control/status, HDMI audio/ACR/VBI/infoframe/generic packet controls, deep color and scrambling controls, guard-band/general-control packet fields, ACR programmed and readback values for 32/44.1/48 kHz families, AFMT clock enable, BE controls, TMDS character/pattern/control/DC-balancer fields, DIG version, and force-disable fields.

The `DP4` section begins a full repeated DisplayPort stream block for the fifth DIO instance. In this chunk it covers link control, pixel format, colorimetry, config, video stream enable/status, FIFO steering, MSA misc/timing, DPHY internal/PHY/training/CRC/fast-training controls, DP secondary packet controls, audio M/N/timestamp, MSE SAT/rate fields, MSO, DSC, GSP controls, double-buffer controls, metadata packet transmission, and `DP_ALPM_CNTL`.

## Important APIs, Types, And Macros

This chunk's API is entirely generated macro metadata. The major naming families are `DP3_DP_*`, `VPG4_VPG_*`, `AFMT4_AFMT_*`, `DME4_DME_*`, `DIG4_*`, and `DP4_DP_*`. Each family must match the corresponding address macros in `dcn_3_1_4_offset.h`, such as `regDP3_DP_SEC_CNTL`, `regVPG4_VPG_GENERIC_PACKET_ACCESS_CTRL`, `regAFMT4_AFMT_AUDIO_PACKET_CONTROL`, `regDME4_DME_CONTROL`, `regDIG4_HDMI_CONTROL`, and `regDP4_DP_LINK_CNTL`.

The primary consumers are the DCN 3.1.4 display resource and DIO stream encoder paths:

- `display/dc/resource/dcn314/dcn314_resource.c` includes `dcn_3_1_4_offset.h` and `dcn_3_1_4_sh_mask.h`, builds stream encoder, VPG, AFMT, and DME register tables, and maps VPG/AFMT/DME blocks to DIO engine instances.
- `display/dc/dio/dcn314/dcn314_dio_stream_encoder.h` defines `SE_DCN314_REG_LIST(id)` and `SE_COMMON_MASK_SH_LIST_DCN314(mask_sh)`. Those macros bind fields such as `DP_SEC_STREAM_ENABLE`, `DP_SEC_GSP*`, `DP_MSA_TIMING_PARAM*`, `DP_DSC_MODE`, `DP_SEC_METADATA_PACKET_*`, `HDMI_GENERIC*`, `HDMI_ACR_*`, `DME_CONTROL`, `DIG_FIFO_*`, and `DIG_CLOCK_PATTERN` to the generated symbols in this header.
- `display/dc/dio/dcn314/dcn314_dio_stream_encoder.c` uses the bound tables to program DP/HDMI enable sequences, FIFO reset/enable, HDMI/DVI setup, secondary packet state readback, metadata packet controls, and audio/timing fields.
- `display/dc/dcn31/dcn31_vpg.h` and `display/dc/dcn31/dcn31_vpg.c` consume VPG masks for generic-packet data, frame/immediate updates, conflict clearing, and VPG memory power.
- `display/dc/dcn31/dcn31_afmt.h` and `display/dc/dcn31/dcn31_afmt.c` consume AFMT masks for audio channel status, audio info updates, audio source selection, sample sending, and AFMT memory power.
- `display/dmub/src/dmub_dcn314.c` and `display/dc/irq/dcn314/irq_service_dcn314.c` include the same generated DCN 3.1.4 headers for firmware-facing register access and interrupt tables, although this specific chunk is most directly tied to DIO stream encoder, VPG, AFMT, DME, and DP/HDMI packet programming.

## Control Flow And State Behavior

The header itself has no control flow. Runtime state is MMIO hardware state inside the DCN 3.1.4 display controller. Configuration fields remain programmed until the driver, firmware, reset logic, or power-management transitions change them. Status and telemetry fields are live or sticky hardware observations.

Typical DP stream programming uses this metadata to set pixel format, MSA timing, video M/N, stream enable, FIFO steering, and DP secondary-packet controls. `DP_SEC_CNTL` and the GSP control registers gate video stream SDPs, audio stream packets, audio timestamp packets, adaptive-sync/metadata packets, MPEG packets, and generic sideband packets. `DP_SEC_CNTL2` through `DP_SEC_CNTL7` provide send, pending, deadline-missed, any-line, line-number, double-buffer-disable, active, and in-idle state for the extended generic sideband slots.

MSA, MSE, MSO, and DSC fields are timing-sensitive. MSA timing parameters must match the active stream. MSE SAT and rate registers describe MST allocation timing and update-pending state. MSO controls split a stream across multiple output segments. `DP_DSC_CNTL.DP_DSC_MODE` gates compressed-stream behavior. Misordered or mismatched programming can leave an enabled stream with wrong timing, missing secondary packets, failed MST scheduling, or bad DSC/MSO behavior.

VPG state is indexed and update-driven. Packet payload bytes are written through `VPG_GENERIC_PACKET_ACCESS_CTRL` and `VPG_GENERIC_PACKET_DATA`; frame-update and immediate-update bits decide when packet payloads become active. Conflict/status bits are sticky diagnostic surfaces that must be cleared with the matching clear field. VPG memory power controls affect whether generic packet storage is available.

AFMT state is packet and audio-channel metadata state. Audio infoframe fields, IEC 60958 channel-status fields, audio source selection, audio sample-send, mute/validity flags, ramp controls, CRC, and AFMT memory power persist in AFMT registers. Audio programming must coordinate with HDMI/DP packet enables so that N/CTS, channel status, audio infoframes, and audio sample transmission align with the active transport.

DIG4 and HDMI/TMDS fields are the front-end and HDMI packet state for one DIG instance. HDMI generic packet controls have continuation/send/line fields for packet slots 0 through 14. ACR controls and programmed N/CTS values are stateful audio-clock recovery surfaces. FIFO reset/enable fields are actively polled in the DCN314 stream encoder; `DIG_FIFO_RESET_DONE`, `DIG_FIFO_ENABLE`, `DIG_SYMCLK_FE_ON`, and output pixel mode determine whether the stream encoder can safely feed the link.

Low-power fields (`DP_ALPM_CNTL`, AUX-less ALPM, AFMT/VPG/DME memory-power registers) interact with link training, panel self refresh, idle behavior, and suspend/resume. They are persistent control state mixed with pending/status readback, so tests need to distinguish command bits from status bits.

## Dependencies And Integration Points

The generated masks and shifts depend on AMD's DCN 3.1.4 register specification and must stay synchronized with `dcn_3_1_4_offset.h`. A mismatch can compile if names still line up but can silently program the wrong bits. The macro contract also depends on AMD display's register helper conventions: `SRI(...)` selects the instance-specific register address, while `SE_SF(...)` and related field-list macros select the instance-0 field names that are reused for all instances.

This chunk integrates with the DRM/KMS display pipeline through DCN314 resource construction. It directly supports DisplayPort and HDMI stream encoders, VPG packet generation, AFMT audio packet generation, DME metadata packets, MST MSE allocation programming, DSC/MSO stream mode, dynamic metadata transmission, HDMI infoframes/generic packets, DP SDPs, audio N/CTS and channel status, FIFO enable/reset, and link low-power entry/exit.

The `DP3`, `VPG4`, `AFMT4`, `DME4`, and `DIG4` groups are a coherent DIO instance. `DP4` starts the next repeated DP stream instance. The range boundaries are therefore partial: DP3 starts before this chunk, and DP4 continues after it. File-level reconciliation should combine neighboring chunk research before treating either repeated stream encoder instance as fully covered.

## Risks And Edge Cases

Generated field drift is the primary risk. Wrong masks or shifts in this range can break DP or HDMI modes without causing obvious software errors: wrong MSA timing, incorrect pixel format, missing secondary data packets, bad HDR/VRR metadata, bad HDMI generic packet scheduling, broken audio N/CTS/channel-status programming, FIFO stalls, or display link-training failures.

DP secondary-packet controls mix enable, send, pending, deadline-missed, double-buffer, active, and in-idle fields. Full-register writes or wrong masks can accidentally drop packet enables, miss sticky failure status, or schedule packets on the wrong line. This is especially sensitive for VSC, HDR static metadata, DSC PPS/GSP11, adaptive sync, and MST sideband scheduling.

The VPG and AFMT blocks use indexed data windows and update bits. A valid mask with a stale index, wrong update mode, or powered-down packet memory writes data to the wrong packet slot or leaves payload changes pending. Conflict and interrupt status bits must be explicitly cleared with their matching masks.

HDMI generic packet controls are dense and split across several registers. Slot 0-14 continuation/send/line fields are easy to cross-wire when generated names or field-list macros are changed. A bug may only show up with multiple concurrent infoframes or dynamic metadata, not with a basic HDMI display.

Audio fields are transport-sensitive. `AFMT_*`, `HDMI_ACR_*`, `DP_SEC_AUD_*`, and `DP_SEC_TIMESTAMP` must agree with the selected DP/HDMI mode, audio sample rate, channel layout, and deep-color/scrambling state. Bad values can produce silent audio, intermittent audio, or bad channel status while video remains stable.

Power and low-power fields can create mode-change-only failures. Forcing VPG/AFMT/DME memory power down, entering ALPM/AUX-less ALPM at the wrong time, or leaving pending sleep/standby state around link training can cause failures around hotplug, PSR, idle entry, suspend/resume, and fast link retraining.

## Test Signals

Build-time coverage should catch renamed or missing symbols in `dcn314_resource.c`, `dcn314_dio_stream_encoder.h`, `dcn31_vpg.h`, and `dcn31_afmt.h`. High-signal compile failures include missing `DP0_DP_SEC_*`, `DIG0_HDMI_*`, `VPG0_VPG_*`, `AFMT0_AFMT_*`, `DME0_DME_CONTROL`, or `DIG0_DIG_FIFO_CTRL0` fields used by DCN314 register-list macros.

Runtime DP validation should exercise DCN 3.1.4 DP connectors routed through the affected DIO instances, with modes that cover SST, MST where available, DSC, MSO, HDR metadata, adaptive sync/VRR metadata, audio, hotplug, link retraining, and suspend/resume. Useful signals include correct MSA timing readback, secondary-packet enable state, no stuck MSE rate update pending, no GSP deadline-missed status, stable DSC/MSO modes, and successful audio/video after low-power transitions.

Runtime HDMI validation should cover DVI/HDMI enable paths, deep color, scrambling, audio N/CTS for 32/44.1/48 kHz families, audio infoframes, general-control packets, generic packet slots, HDR metadata, Dolby Vision enable where applicable, FIFO reset/enable polling, and repeated modesets. Expected signals are stable video, correct infoframe/metadata capture on a protocol analyzer, working audio, and no FIFO reset timeout.

VPG/AFMT/DME validation should program generic packets through indexed data windows, switch frame versus immediate update, verify conflict clear behavior, toggle memory power around idle and resume, and confirm DME metadata packet enable/line programming. Register dumps are valuable because many failures are wrong-packet or wrong-line errors rather than kernel crashes.

Low-power validation should cover DP ALPM and AUX-less ALPM entry/exit around active video, PSR-like idle paths, fast retraining, HPD cycles, and suspend/resume. Status fields such as pending bits, PHY sleep/standby requests, AUX-less CRC/result/timeout/mask fields, and memory power state should transition coherently and not leave the stream encoder unable to re-enable video or packets.
