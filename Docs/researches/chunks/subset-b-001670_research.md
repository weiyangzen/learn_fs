# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 34756-37152

## Scope

This chunk is a generated AMDGPU DCN 2.1.0 register shift/mask header segment. It contains preprocessor constants only: no functions, structs, enums, storage objects, or executable control flow. The exported surface is the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` namespace used by AMD display register helper macros to insert, extract, acknowledge, or decode fields in DCN 2.1.0 MMIO registers.

The range covers 2,397 source lines with 2,170 `#define` entries, 1,083 shift macros, 1,087 mask macros, and 219 register/address-block comments. It starts in the middle of `DP_AUX3_AUX_SW_STATUS`, completes the `DP_AUX3` AUX register group, defines the full `DP_AUX4` AUX block, then covers `DIG0`, `DP0`, and the beginning of `DIG1` display-output blocks.

## Purpose

The chunk provides exact bit positions and already-shifted masks for DCN 2.1.0 display I/O hardware fields. Higher-level AMD display code can use stable symbolic field names while this generated header supplies ASIC-specific bit layout.

Major hardware areas covered here are:

- `DP_AUX3_*` and `DP_AUX4_*`: DisplayPort AUX engine status, low-speed status, data FIFOs, DPHY TX/RX timing controls, DPHY status, GTC synchronization, interrupt/ack/mask fields, arbitration, and PHY wake handshakes.
- `DIG0_*`: digital front-end/back-end controls, output CRC/test/random pattern generation, FIFO status, HDMI packet generation, HDMI infoframes, HDMI ACR/audio control, AFMT audio packet and channel-status metadata, TMDS control character generation, lane enable, VBI packet scheduling, data-bypass controls, and forced DIG disable.
- `DP0_*`: DisplayPort link controls, pixel/MSA configuration, video stream timing and M/N values, DPHY training/scrambling/CRC/PRBS, secondary-data packet scheduling, audio M/N and timestamp programming, MST/MSE slot allocation, MSO and DSC control, metadata transmission, VBID/misc fields, ALPM control, and DisplayPort debug-bypass controls.
- `DIG1_*`: the beginning of the second digital display instance, structurally mirroring the `DIG0` front-end, FIFO, HDMI, generic-packet, GC, AFMT audio-packet, and ISRC metadata fields until the chunk ends inside `DIG1_AFMT_ISRC1_3`.

Although the repository path is under `sources/distributed-fs/ceph-client`, this source is AMDGPU display hardware metadata. It has no Ceph filesystem, distributed storage, network protocol, or userspace persistence behavior.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The contract is the generated macro naming scheme and the pairing of field shifts with masks:

- `*_SHIFT` constants hold the field low-bit position.
- `*_MASK` constants hold the field mask already shifted into register position.
- Register-heading comments such as `//DP0_DP_SEC_CNTL2` group the macros by hardware register.
- Address-block comments such as `// addressBlock: dce_dc_dio_dp_aux4_dispdec`, `// addressBlock: dce_dc_dio_dig0_dispdec`, `// addressBlock: dce_dc_dio_dp0_dispdec`, and `// addressBlock: dce_dc_dio_dig1_dispdec` mark generated register windows.

Representative AUX macros include `DP_AUX4_AUX_CONTROL__AUX_EN_MASK`, `DP_AUX4_AUX_SW_CONTROL__AUX_SW_START_DELAY_MASK`, `DP_AUX4_AUX_INTERRUPT_CONTROL__AUX_SW_DONE_ACK_MASK`, `DP_AUX4_AUX_SW_STATUS__AUX_SW_REPLY_BYTE_COUNT_MASK`, `DP_AUX4_AUX_DPHY_TX_REF_CONTROL__AUX_TX_REF_DIV_MASK`, `DP_AUX4_AUX_DPHY_RX_CONTROL0__AUX_RX_DETECTION_THRESHOLD_MASK`, `DP_AUX4_AUX_GTC_SYNC_CONTROLLER_STATUS__AUX_GTC_SYNC_CRITICAL_ERR_OCCURRED_ACK_MASK`, and `DP_AUX4_AUX_PHY_WAKE_CNTL__DP_AUX_PHY_WAKE_ACK_MASK`. The `DP_AUX3` group uses the same layout for AUX instance 3 but this chunk begins after that register group's first heading and first several shift definitions.

Representative DIG/HDMI/AFMT macros include `DIG0_DIG_FE_CNTL__DIG_SOURCE_SELECT_MASK`, `DIG0_DIG_OUTPUT_CRC_CNTL__DIG_OUTPUT_CRC_CONT_EN_MASK`, `DIG0_DIG_FIFO_STATUS__DIG_FIFO_OVERFLOW_MASK`, `DIG0_HDMI_CONTROL__HDMI_DATA_SCRAMBLE_EN_MASK`, `DIG0_HDMI_ACR_PACKET_CONTROL__HDMI_ACR_AUTO_SEND_MASK`, `DIG0_HDMI_GENERIC_PACKET_CONTROL0__HDMI_GENERIC7_CONT_MASK`, `DIG0_AFMT_AUDIO_PACKET_CONTROL2__AFMT_AUDIO_CHANNEL_ENABLE_MASK`, `DIG0_AFMT_60958_0__AFMT_60958_CS_CHANNEL_NUMBER_L_MASK`, `DIG0_AFMT_AUDIO_PACKET_CONTROL__AFMT_60958_CS_UPDATE_MASK`, `DIG0_TMDS_DCBALANCER_CONTROL__TMDS_DCBALANCER_EN_MASK`, and `DIG0_FORCE_DIG_DISABLE__FORCE_DIG_DISABLE_MASK`. `DIG1` repeats the same generated families for the second DIG instance, but this range only covers the initial part of the instance.

Representative DP0 macros include `DP0_DP_LINK_CNTL__DP_LINK_TRAINING_COMPLETE_MASK`, `DP0_DP_PIXEL_FORMAT__DP_PIXEL_ENCODING_MASK`, `DP0_DP_VID_STREAM_CNTL__DP_VID_STREAM_ENABLE_MASK`, `DP0_DP_STEER_FIFO__DP_STEER_FIFO_RESET_MASK`, `DP0_DP_DPHY_CNTL__DPHY_BS_SR_SWAP_MASK`, `DP0_DP_DPHY_FAST_TRAINING__DPHY_RX_FAST_TRAINING_CAPABLE_MASK`, `DP0_DP_SEC_CNTL__DP_SEC_STREAM_ENABLE_MASK`, `DP0_DP_SEC_CNTL2__DP_SEC_GSP4_SEND_MASK`, `DP0_DP_MSE_SAT0__DP_MSE_SAT_SRC0_MASK`, `DP0_DP_MSO_CNTL__DP_MSO_ENABLE_MASK`, `DP0_DP_DSC_CNTL__DP_DSC_ENABLE_MASK`, and `DP0_DP_ALPM_CNTL__DP_ALPM_ENABLE_MASK`.

## Control Flow

This header has no local runtime control flow. Runtime behavior is created by consumers that include `dcn_2_1_0_offset.h` with this shift/mask header, assemble register tables, and then access MMIO through AMD display helper macros.

A typical flow is:

1. DCN21 resource, IRQ, GPIO, DMUB, AUX/DDC, link-encoder, stream-encoder, or audio code includes the generated offset and shift/mask headers.
2. Generation-specific register lists use macro-pasting helpers such as `REG_OFFSET`, `SF`, `SRI`, `FD_MASK`, `FD_SHIFT`, and resource/IRQ register-table macros.
3. Driver code issues `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, or equivalent helper calls.
4. The helpers combine the offset header's register addresses with this file's masks and shifts to read status, program configuration, clear sticky/ack fields, or build packed register values.

Control-sensitive flows represented by this chunk include AUX transaction completion and error decoding, AUX low-speed updates, HPD disconnect detection during AUX operations, AUX GTC synchronization lock/error handling, HDMI packet scheduling, HDMI/AFMT audio infoframe and channel-status programming, TMDS symbol/control-character generation, DisplayPort link training and video-stream enablement, secondary-data packet insertion, MST slot allocation, DSC enablement, ALPM entry/exit, and interrupt/status acknowledgement.

The macros do not encode ordering, access type, volatility, reset value, read-only/write-only semantics, or write-one-to-clear behavior. Those constraints remain in the calling code and hardware programming sequences.

## State And Persistence Behavior

The file itself stores no software state and performs no persistence. It describes hardware register fields whose state persists according to DCN/DIO register semantics until changed by software, hardware state machines, power management, modeset reset, or GPU reset.

State represented in this range includes:

- AUX engine state: request/done bits, reply byte counts, timeout state, overflow/partial-byte/error flags, non-AUX mode detection, low-speed update state, AUX data byte/index windows, PHY TX/RX timing, GTC lock acquisition and maintenance state, GTC error counters/status, and PHY wake pending/ack state.
- DIG and HDMI state: source selection, front-end enable, CRC/test-pattern controls, FIFO underflow/overflow indicators, metadata and generic-packet send/continuous/line-reference controls, HDMI scramble/deep-color/AVMUTE state, ACR selection, null/GC/ISRC/infoframe scheduling, and HDMI/AFMT audio packet controls.
- AFMT audio metadata state: audio layout/channel enable, DP audio stream ID, ISRC bytes, MPEG/generic packet payload bytes, audio infoframe bytes, IEC 60958 channel-status override bytes, audio CRC control/result, ramp controls, AFMT status, VBI packet insertion, and audio source control.
- TMDS/DIG back-end state: DIG back-end enable, TMDS output enable, control-character patterns, stereo sync selection, sync-character patterns, CTL bit generation, DC balancer controls, lane enable, and forced-disable state.
- DP0 link state: link training complete, pixel format, MSA colorimetry/misc/timing fields, stream enable, video timing, link framing, DPHY lane/symbol/training/scrambling/CRC controls, secondary stream/audio packet controls, MST/MSE allocation state, MSO controls, DSC enablement, metadata transmission, DSC bytes-per-pixel, and ALPM state.

Some fields are configuration latches, some are live status readbacks, and some are interrupt/status/ack/mask fields. Incorrect writes can persist through normal display operation until a modeset, hotplug cycle, suspend/resume path, power-gate cycle, or full GPU reset reinitializes the affected block.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`, which supplies matching register offsets. This file supplies bit layouts within those registers. The constants also depend on AMD display helper conventions that paste register and field names into `*_MASK` and `__SHIFT` identifiers.

Direct include sites visible in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`, which includes the DCN 2.1.0 headers while building Renoir/DCN21 display resources such as DIO, AUX/DDC, GPIO, stream encoders, clocks, IRQs, and related register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`, which includes the headers for DCN21 interrupt source mapping and register mask definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.c`, which include the generated DCN21 headers for GPIO/AUX/HPD register object construction and translation.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`, which includes the same offset/mask headers while assembling DMUB service register metadata.

Functional integration points are broader than the include list. AUX fields feed DCE/DCN AUX and DDC operations, HPD sideband handling, DisplayPort link training, EDID/DPCD transactions, and GTC synchronization. DIG/HDMI/AFMT fields feed stream encoder setup, HDMI/DP audio programming, infoframe construction, metadata insertion, CRC/test-pattern diagnostics, and TMDS output programming. DP0 fields feed link encoder and stream encoder code for DP video, MST, secondary-data packets, DSC, MSO, and ALPM.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A wrong shift or mask can compile cleanly but target the wrong bit, truncate a field, leave stale bits set after a read/modify/write, miss a status condition, or acknowledge the wrong event.

AUX fields are connector-critical. Bad `DP_AUX3` or `DP_AUX4` status, data, interrupt, DPHY, GTC, or PHY wake constants can break EDID/DPCD reads, DisplayPort link training, HPD-disconnect handling during transactions, timeout/error classification, link-service updates, AUX-GTC synchronization, or power-management wake handshakes. Some failures will be board-, connector-, cable-, or resume-specific.

DIG/HDMI/AFMT fields are protocol-visible. Incorrect packet-control, ACR, generic-packet, infoframe, ISRC, MPEG, audio-channel, IEC 60958, TMDS, deep-color, or scramble masks can produce missing HDMI/DP audio, wrong channel count/sample-rate metadata, malformed infoframes, no AVMUTE, invalid TMDS control symbols, broken compliance-test patterns, or audio behavior that regresses only after hotplug or modeset.

DP0 fields affect link bring-up and display correctness. Bad DPHY/training/scramble/CRC, MSA, video timing, M/N, secondary-data, MST/MSE, DSC, MSO, metadata, or ALPM masks can cause link-training failures, black screens, incorrect colorimetry, unstable MST allocation, missing audio secondary packets, DSC corruption, or low-power link-management failures.

The repeated generated instances create copy/generation hazards. `DP_AUX3` and `DP_AUX4` are structurally similar, and `DIG0`/`DIG1` should align for the covered registers. One-off differences should be treated as suspicious unless the ASIC register database requires them.

Chunk boundaries matter. The range starts after the `DP_AUX3_AUX_SW_STATUS` heading and first several shift definitions, so the full register group is split with the previous chunk. The range ends inside `DIG1_AFMT_ISRC1_3`, so the rest of the `DIG1` instance belongs to a later chunk. The final merge lane should avoid drawing whole-file conclusions from this artificial slice alone.

## Test Signals

Useful validation signals are generated-header consistency checks plus DCN21 display, connector, AUX, DP, HDMI, and audio behavior:

- Build coverage for DCN21 resource, IRQ, GPIO, DMUB, AUX/DDC, link, stream-encoder, and audio paths that include `dcn_2_1_0_sh_mask.h`.
- Generated-register validation that every field in this chunk has a matching register definition in `dcn_2_1_0_offset.h`, masks match their shifts and field widths, and repeated `DP_AUX3`/`DP_AUX4` and `DIG0`/`DIG1` layouts remain intentionally aligned.
- AUX/DDC tests for EDID reads, DPCD reads/writes, link-service updates, HPD-disconnect during transactions, timeout/error reporting, PHY wake behavior, and suspend/resume reinitialization.
- DisplayPort tests for link training, MSA timing/colorimetry, stream enable/disable, scrambling, PRBS/CRC diagnostics, audio secondary packets, MST/MSE slot allocation, DSC operation, MSO operation, metadata transmission, and ALPM transitions.
- HDMI/DVI tests for scrambling, deep color, TMDS control characters, AVMUTE, ACR packet generation, generic-packet scheduling, infoframes, audio channel layouts, ISRC/MPEG/generic payload handling, and hotplug/modeset recovery.
- Interrupt/status tests that verify AUX done/error acks, GTC sync errors, FIFO underflow/overflow indicators, HDMI error status, DP video interrupts, and audio-format/status updates report and clear as expected.

Regression symptoms from bad constants include failed EDID/AUX transactions, missing HPD-related AUX aborts, black screen after link training, incorrect colorimetry or timing, no HDMI/DP audio, wrong audio channel metadata, malformed infoframes, stuck AUX/GTC/DP/HDMI status bits, MST allocation failures, DSC corruption, or failures limited to AUX4, DP0, DIG0, or DIG1 instance-specific paths.

## Cross-Chunk Notes

This is a generated constants-only chunk of `dcn_2_1_0_sh_mask.h`. Adjacent chunks own the beginning of `DP_AUX3_AUX_SW_STATUS` and the continuation of `DIG1` after `DIG1_AFMT_ISRC1_3`. The later per-file report should merge this with neighboring chunks to describe the complete DCN 2.1.0 register layout contract rather than treating this line range as an independently designed module.
