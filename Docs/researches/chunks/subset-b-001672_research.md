# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 39581-42008

## Scope

This chunk is a generated AMDGPU DCN 2.1.0 register shift/mask header range. It contains C preprocessor constants only: no functions, structs, enums, objects, executable statements, or local storage. The exported contract is the generated naming convention `REGISTER__FIELD__SHIFT` plus `REGISTER__FIELD_MASK`, where the shift is the field low bit and the mask is already positioned in the MMIO register word.

The assigned range has 2,428 source lines with 2,165 `#define` entries: 1,085 shift constants and 1,080 mask constants. It includes 257 register or address-block comments. The chunk starts in the middle of the `DP2` DisplayPort secondary-data/audio/MST section, contains complete `DIG3` HDMI/audio-formatter and `DP3` DisplayPort blocks, and ends in the early `DIG4` audio formatter block at `DIG4_AFMT_60958_0`.

Major generated groups in this range are:

- `DP2_*`: tail of DisplayPort instance 2, covering secondary-data packet framing, audio M/N, MST/MSE slot allocation, MSA timing, MSO, DSC, double-buffering, metadata, and ALPM controls.
- `DIG3_*`: display encoder/audio formatter instance 3, covering DIG front-end/backend controls, HDMI packet/infoframe paths, audio formatter payload registers, TMDS controls, generic packet update machinery, and forced-DIG-disable control.
- `DP3_*`: DisplayPort instance 3, covering link control, pixel format, MSA, video stream timing and interrupts, DPHY training/scrambler/CRC/PRBS/fast-training, secondary-data/audio packet controls, MST/MSE/MSO, DSC, double-buffering, metadata, and ALPM.
- `DIG4_*`: beginning of display encoder/audio formatter instance 4, mirroring the early DIG/HDMI/AFMT register layout visible for `DIG3` through the first IEC 60958 channel-status register.

## Purpose

The chunk gives DCN 2.1 display code exact bit layouts for Renoir-generation display output hardware. The companion offset header identifies where a register lives; this file identifies which bits in that register carry a named control or status field. Consumers can then build register tables and use helper macros to read, update, or poll hardware fields by logical name instead of hard-coded bit arithmetic.

The `DP2` and `DP3` material models DisplayPort stream generation and link-side packetization. It covers video stream enablement, pixel format, colorimetry, MSA timing, VBID overrides, training pattern selection, DPHY symbols, 8b/10b behavior, scrambler and PRBS control, CRC capture, fast-training, secondary-data packet enable/send/status lines, audio clock M/N programming, MST slot allocation tables and status readbacks, MSO secondary-packet routing, DSC mode/bytes-per-pixel/slice width, metadata packet scheduling, double-buffer handoff state, and low-power ALPM sleep/standby requests.

The `DIG3` and `DIG4` material models encoder and audio formatter behavior used by HDMI/TMDS and display audio. It includes DIG front-end selection and reset, CRC output, test/clock/random patterns, FIFO status, HDMI control/status, audio clock regeneration packet controls, VBI/infoframe/generic packet scheduling, metadata double-buffering, Dynamic Metadata Engine controls, MPEG/audio/generic infoframe payload bytes, Audio Clock Regeneration values and readbacks, IEC 60958 channel-status fields, audio CRC and ramp controls, audio packet/VBI controls, audio source selection, backend enablement, TMDS control characters and DC-balancer settings, and AFMT clock enable/on state.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The important interface is the macro namespace itself:

- `*_SHIFT` macros are integer bit positions, often expressed in hex, used by `FD_SHIFT`, `REG_SET`, `REG_UPDATE`, and related generated register helpers.
- `*_MASK` macros are bit masks with the field already shifted into register position, used by `FD_MASK`, `REG_GET`, `REG_SET`, `REG_UPDATE_N`, and bitfield extraction helpers.
- Register-heading comments such as `//DP3_DP_DPHY_CNTL` or `//DIG3_HDMI_INFOFRAME_CONTROL0` group the fields belonging to one hardware register.
- Address-block comments such as `// addressBlock: dce_dc_dio_dig3_dispdec`, `// addressBlock: dce_dc_dio_dp3_dispdec`, and `// addressBlock: dce_dc_dio_dig4_dispdec` mark repeated display encoder/link instances.

Representative DisplayPort field groups include:

- Link and stream setup: `DP3_DP_LINK_CNTL__DP_LINK_TRAINING_COMPLETE_MASK`, `DP3_DP_PIXEL_FORMAT__DP_PIXEL_ENCODING_MASK`, `DP3_DP_CONFIG__DP_UDI_LANES_MASK`, `DP3_DP_VID_STREAM_CNTL__DP_VID_STREAM_ENABLE_MASK`, and `DP3_DP_VID_TIMING__DP_VID_M_N_GEN_EN_MASK`.
- Main Stream Attribute and VBID fields: `DP3_DP_MSA_MISC__DP_MSA_MISC0_MASK`, `DP3_DP_MSA_TIMING_PARAM1__DP_MSA_VTOTAL_MASK`, `DP3_DP_MSA_TIMING_PARAM3__DP_MSA_HSYNCPOLARITY_MASK`, and `DP3_DP_MSA_VBID_MISC__DP_VBID1_OVERRIDE_EN_MASK`.
- DPHY training and diagnostics: `DP3_DP_DPHY_CNTL__DP_DPHY_ATEST_SEL_MASK`, `DP3_DP_DPHY_TRAINING_PATTERN_SEL__DPHY_TRAINING_PATTERN_SEL_MASK`, `DP3_DP_DPHY_SCRAM_CNTL__DPHY_SCRAMBLER_BS_COUNT_MASK`, `DP3_DP_DPHY_CRC_CNTL__DPHY_CRC_CONT_EN_MASK`, and `DP3_DP_DPHY_FAST_TRAINING_STATUS__DPHY_RX_FAST_TRAINING_COMPLETE_MASK`.
- Secondary data and audio: `DP3_DP_SEC_CNTL__DP_SEC_STREAM_ENABLE_MASK`, `DP3_DP_SEC_CNTL1__DP_SEC_GSP0_SEND_PENDING_MASK`, `DP3_DP_SEC_FRAMING4__DP_SEC_AUDIO_MUTE_MASK`, `DP3_DP_SEC_AUD_N__DP_SEC_AUD_N_MASK`, `DP3_DP_SEC_AUD_M__DP_SEC_AUD_M_MASK`, and `DP3_DP_SEC_PACKET_CNTL__DP_SEC_ASP_CODING_TYPE_MASK`.
- MST/MSO/DSC/metadata: `DP3_DP_MSE_RATE_CNTL__DP_MSE_RATE_Y_MASK`, `DP3_DP_MSE_SAT0__DP_MSE_SAT_SLOT_COUNT0_MASK`, `DP3_DP_MSO_CNTL__DP_MSO_NUM_OF_SSTLINK_MASK`, `DP3_DP_DSC_CNTL__DP_DSC_MODE_MASK`, `DP3_DP_DSC_BYTES_PER_PIXEL__DP_DSC_BYTES_PER_PIXEL_MASK`, and `DP3_DP_SEC_METADATA_TRANSMISSION__DP_SEC_METADATA_PACKET_LINE_MASK`.

Representative DIG/HDMI/AFMT field groups include:

- Encoder front/back end and diagnostics: `DIG3_DIG_FE_CNTL__DIG_SOURCE_SELECT_MASK`, `DIG3_DIG_OUTPUT_CRC_CNTL__DIG_OUTPUT_CRC_EN_MASK`, `DIG3_DIG_TEST_PATTERN__DIG_TEST_PATTERN_MASK`, `DIG3_DIG_FIFO_STATUS__DIG_FIFO_READ_PTR_MASK`, `DIG3_DIG_BE_CNTL__DIG_HPD_SELECT_MASK`, and `DIG3_DIG_BE_EN_CNTL__DIG_BE_ENABLE_MASK`.
- HDMI packetization: `DIG3_HDMI_CONTROL__HDMI_ENABLE_MASK`, `DIG3_HDMI_STATUS__HDMI_STREAM_STATUS_MASK`, `DIG3_HDMI_AUDIO_PACKET_CONTROL__HDMI_AUDIO_PACKETS_PER_LINE_MASK`, `DIG3_HDMI_ACR_PACKET_CONTROL__HDMI_ACR_SEND_MASK`, `DIG3_HDMI_INFOFRAME_CONTROL0__HDMI_AUDIO_INFO_SEND_MASK`, and `DIG3_HDMI_GENERIC_PACKET_CONTROL0__HDMI_GENERIC0_SEND_MASK`.
- Generic and metadata payloads: `DIG3_AFMT_GENERIC_HDR__AFMT_GENERIC_HB0_MASK`, `DIG3_AFMT_GENERIC_0__AFMT_GENERIC_BYTE0_MASK`, `DIG3_HDMI_GENERIC_PACKET_CONTROL1__HDMI_GENERIC0_LINE_MASK`, `DIG3_HDMI_DB_CONTROL__HDMI_DB_PENDING_MASK`, and `DIG3_DME_CONTROL__METADATA_ENGINE_EN_MASK`.
- Audio formatting: `DIG3_AFMT_AUDIO_INFO0__AFMT_AUDIO_INFO_CC_MASK`, `DIG3_AFMT_AUDIO_INFO1__AFMT_AUDIO_INFO_CA_MASK`, `DIG3_AFMT_60958_0__AFMT_60958_CS_SAMPLING_FREQUENCY_MASK`, `DIG3_AFMT_AUDIO_CRC_CONTROL__AFMT_AUDIO_CRC_EN_MASK`, `DIG3_AFMT_AUDIO_PACKET_CONTROL__AFMT_AUDIO_SAMPLE_SEND_MASK`, and `DIG3_AFMT_CNTL__AFMT_AUDIO_CLOCK_EN_MASK`.
- TMDS and HDMI physical formatting: `DIG3_TMDS_CNTL__TMDS_PIXEL_ENCODING_MASK`, `DIG3_TMDS_CONTROL_CHAR__TMDS_CONTROL_CHAR0_MASK`, `DIG3_TMDS_DCBALANCER_CONTROL__TMDS_DCBALANCER_EN_MASK`, and `DIG3_TMDS_CTL0_1_GEN_CNTL__TMDS_CTL0_USE_FEEDBACK_MASK`.

The `DP2`, `DP3`, `DIG3`, and `DIG4` definitions are instance-specific copies. They are expected to be structurally similar to other generated instances, with only the register prefix changing unless the ASIC database intentionally describes per-instance differences.

## Control Flow

This header has no local control flow. Runtime control flow is created by AMD display code that includes this header and expands generated register macros into register tables. Typical use is:

1. A DCN 2.1 module includes `dcn_2_1_0_offset.h` and `dcn_2_1_0_sh_mask.h`.
2. Local register-list macros paste register and field names into `mm...` offsets, `FD_MASK(reg, field)`, and `FD_SHIFT(reg, field)`.
3. Driver objects such as resource, IRQ, GPIO, DIO, AUX/I2C, link encoder, stream encoder, DMUB service, and audio formatter code call register helpers.
4. The helpers use the generated masks and shifts to perform MMIO read/modify/write, extract status bits, set update triggers, clear pending bits, or wait for hardware state changes.

Control-sensitive hardware flows represented by this range include DisplayPort link training completion, training pattern and symbol programming, scrambler enable/reset, CRC capture, video stream enablement, MSA/VBID generation, secondary data packet scheduling, audio mute and audio M/N programming, MST slot table updates, DSC enablement, metadata packet transmission, ALPM sleep/standby requests, HDMI packet send/update sequencing, generic infoframe frame/immediate updates, audio sample packet emission, AFMT clock gating, TMDS control-character generation, and DIG back-end enablement.

The macros do not encode access type, ordering, volatility, self-clearing behavior, write-one-to-clear semantics, or safe update windows. Those rules remain in the display driver logic and hardware programming sequences.

## State And Persistence Behavior

The file itself stores no state and persists nothing. It describes stateful hardware fields whose values live in DCN 2.1 display MMIO registers until changed by software, reset by hardware, altered by hardware state machines, or lost across power/reset events.

State represented by this chunk includes:

- DisplayPort link and stream state: lane/link training completion, pixel encoding, lane count, stream enablement, FIFO steering, MSA fields, VBID overrides, training pattern selection, DPHY symbol values, scrambler mode, PRBS mode, CRC capture state, fast-training status, and ALPM pending/sending states.
- Secondary-data and display-audio state: SDP packet enable bits, generic stream packet send requests and pending/deadline status, line scheduling, frame start positions, idle widths, audio mute status, audio N/M values and readbacks, ASP coding/version/channel override fields, and metadata packet line control.
- MST/MSO/DSC state: MSE rate numerator/denominator, SAT source/slot assignments, SAT update status, MSE link timing, MSO SST-link count and secondary-packet enables, DSC mode, slice width, and bytes-per-pixel.
- DIG/HDMI state: source select, DIG clock/reset controls, CRC enable/results, test pattern selection, FIFO status, HDMI enable/status, ACR packet controls, VBI/infoframe/generic packet sends, packet line numbers, packet double-buffer pending/taken/lock/disable bits, and metadata-engine double-buffer state.
- Audio formatter state: MPEG/audio infoframe payload bytes, AFMT generic payload bytes, ACR CTS/N values and status readbacks, IEC 60958 channel-status values, audio CRC controls/results, ramp controls, audio packet sample layout, VBI packet enablement, audio source selection, and AFMT clock enable/on status.
- TMDS/backend state: backend enable, HPD select, TMDS enable, pixel encoding, control characters, sync pattern fields, CTL bits, DC balancer enable/test state, feedback control, and force-disable state.

Some fields are programmed configuration latches, some are live readbacks, some are hardware pending/status bits, and some are update or clear triggers. A bad read/modify/write can therefore persist until the next modeset, stream reprogramming, connector hotplug sequence, audio reconfiguration, display power transition, suspend/resume, or full GPU reset.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`, which supplies the register offsets matching these field names. This chunk also depends on AMD display register helper conventions in `reg_helper.h` and related DCN macros that paste register and field identifiers into `FD_MASK` and `FD_SHIFT` lookups.

Visible include sites for `dcn_2_1_0_sh_mask.h` in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`, which builds DCN 2.1 resource tables for Renoir display hardware and maps generated registers into display objects.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`, which includes the mask and offset headers while defining DCN 2.1 interrupt service behavior.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.c`, which use generated DCN 2.1 register metadata for GPIO/HPD/DDC/AUX construction and translation.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`, which expands common DMUB register fields using the DCN 2.1 generated masks and shifts.

The `DP2` and `DP3` definitions integrate with DisplayPort link encoder and stream encoder programming, MST bandwidth/slot allocation, DSC setup, metadata packet transport, and low-power link states. The `DIG3` and `DIG4` definitions integrate with DIO/DIG stream encoders, HDMI/TMDS output, audio formatter setup, generic infoframe programming, HDR or vendor metadata transport, and display audio paths.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata. It has no Ceph filesystem, distributed storage, network protocol, or application persistence behavior.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These are compile-time constants, so an incorrect shift or mask can pass C compilation while directing register helpers to the wrong bit, truncating a value, failing to observe a status bit, or clearing/updating the wrong field.

DisplayPort fields are especially sensitive during link training and modeset sequencing. Bad `DP3_DP_DPHY_*`, `DP3_DP_LINK_*`, `DP3_DP_VID_*`, `DP3_DP_MSA_*`, or `DP3_DP_DSC_*` definitions can produce link-training failures, black screens, wrong color/pixel encoding, incorrect timing advertised in MSA, broken DSC transport, missing CRC diagnostics, or errors that only appear on certain lane counts, link rates, monitors, docks, MST topologies, or low-power transitions.

Secondary-data, metadata, and audio fields are protocol-visible. Incorrect SDP, GSP, infoframe, metadata, audio N/M, ASP coding, ACR, IEC 60958, or audio packet masks can result in missing HDMI/DP audio, wrong sample-rate recovery, stale HDR/vendor metadata, malformed AVI/audio/generic infoframes, muted audio, GSP deadline misses, or update-pending bits that never settle.

MST/MSO state has repeated source/slot fields and update controls. Off-by-one field widths or copied masks in `DP*_DP_MSE_SAT*`, `DP*_DP_MSO_CNTL*`, or `DP*_DP_SEC_CNTL*` can allocate the wrong virtual channel payload slots, misroute secondary packets, or break multi-stream and multi-SST-link displays while single-stream panels still work.

DIG/TMDS/HDMI fields mix normal configuration, live status, update triggers, double-buffer handoff bits, and clear bits. Register helpers that use a wrong mask around `DIG*_HDMI_DB_CONTROL`, `DIG*_DME_CONTROL`, `DIG*_HDMI_GENERIC_PACKET_CONTROL*`, or `DIG*_AFMT_VBI_PACKET_CONTROL1` could lose metadata updates, lock a packet buffer, report stale pending state, or send packets on the wrong line.

Repeated generated instances create copy hazards. `DP2` and `DP3` should remain structurally aligned for shared DP register families, and `DIG3` and `DIG4` should mirror each other for the common DIG/HDMI/AFMT families visible in this range. A one-off shift or mask difference should be treated as suspicious unless corroborated by the ASIC register database or matching offset/header generation.

Chunk boundaries are artificial. The range starts after the `DP2_DP_SEC_FRAMING1` heading and first two field shifts, so the `DP2_DP_SEC_FRAMING1` register is split with the previous chunk. It ends inside `DIG4_AFMT_60958_0`, before the remaining masks for that register and later `DIG4` registers. The final merged file research should not infer whole-register completeness at either boundary.

## Test Signals

Useful validation signals are mostly generated-header consistency checks plus hardware/display behavior:

- Build coverage for DCN 2.1 display modules that include `dcn_2_1_0_sh_mask.h`, especially `dcn21_resource.c`, `irq_service_dcn21.c`, DCN21 GPIO translation/factory code, DMUB DCN21 support, DIO/link encoder code, and display audio paths.
- Generated-register validation that every `REGISTER__FIELD__SHIFT` has the expected `REGISTER__FIELD_MASK`, that masks match field widths and shifts, and that matching registers exist in `dcn_2_1_0_offset.h`.
- Structural diff checks across repeated instances: `DP2` versus `DP3`, `DIG3` versus `DIG4`, and adjacent DCN 2.x generated headers where hardware revisions are supposed to be layout-compatible.
- DisplayPort link-training tests across link rates and lane counts, including DPHY training patterns, scrambler reset, CRC diagnostics, PRBS paths, fast-training status, and link-training-complete observation.
- Modeset and stream tests that exercise MSA timing, VBID override, pixel encoding/colorimetry, video stream enable/disable, DSC enablement and bytes-per-pixel programming, and double-buffer update/taken/clear state.
- MST/MSO tests with multiple streams or tiled panels to confirm MSE rate programming, SAT source/slot assignment, SAT updates, MSO secondary packet enables, and metadata packet scheduling.
- HDMI/TMDS tests for HDMI enable/status, ACR CTS/N values, audio sample packets, IEC 60958 channel-status bits, generic infoframes, AVI/audio/vendor/HDR metadata, packet line scheduling, and packet frame/immediate update pending bits.
- Hotplug, suspend/resume, runtime power, display off/on, and ALPM tests that verify link, packet, AFMT, metadata, and double-buffer state is reprogrammed or restored correctly.

Regression symptoms from bad constants in this chunk include black screen after modeset, failed DP link training, MST stream loss, broken DSC panels, stale or missing HDR metadata, no HDMI/DP audio, wrong audio sample rate or channel status, stuck packet update-pending bits, bad CRC diagnostics, HDMI/TMDS output instability, and failures isolated to connector/link instances backed by `DP2`, `DP3`, `DIG3`, or `DIG4`.

## Cross-Chunk Notes

This is one chunk of the generated `dcn_2_1_0_sh_mask.h` file. The previous chunk owns the beginning of the `DP2` secondary-data region, and the next chunk owns the rest of `DIG4_AFMT_60958_0` and later generated `DIG4` definitions. The merge/reconciliation lane should combine this document with adjacent chunks before making final whole-file statements about register-family completeness, instance counts, or generated-header endings.
