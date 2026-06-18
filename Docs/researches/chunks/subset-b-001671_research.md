# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 37153-39580

## Scope

This chunk is a generated constants-only slice of AMDGPU's DCN 2.1.0 register shift/mask header. It covers lines 37153-39580 of `dcn_2_1_0_sh_mask.h` and contains 2,164 `#define` entries: 1,081 `__SHIFT` constants and 1,083 `_MASK` constants, grouped by 258 register/address-block comments. There are no functions, structs, enums, variables, branches, loops, or local storage.

The range starts in the middle of the `DIG1` display encoder audio/HDMI block at `DIG1_AFMT_ISRC1_4`, completes many `DIG1` HDMI/audio/TMDS/DIG backend field definitions, covers the full visible `DP1` DisplayPort encoder register group, covers the full visible `DIG2` HDMI/audio/TMDS/DIG backend group, and begins the `DP2` DisplayPort encoder group through `DP2_DP_SEC_FRAMING1`. The logical hardware blocks are split by artificial chunk boundaries, so adjacent chunks are needed for the preceding `DIG1` fields and the remaining `DP2` fields.

Although this repository path is under `ceph-client`, this file is AMD display hardware metadata. It has no Ceph filesystem protocol behavior and no distributed filesystem persistence model.

## Purpose

The purpose of this range is to publish exact bit positions and already-positioned masks for DCN 2.1.0 digital display encoder registers. Runtime display code includes this header together with the matching register-address header, `dcn_2_1_0_offset.h`, then uses AMD display register helpers to encode and decode packed MMIO fields without hard-coding bit values in functional code.

The represented hardware areas are:

- Tail `DIG1` AFMT/HDMI audio packet state: ISRC bytes, generic HDMI packet line control, HDMI double-buffer control, metadata engine control, MPEG infoframe bytes, generic packet header/payload bytes, ACR N/CTS values for 32/44.1/48 kHz families, ACR status, audio infoframe bytes, IEC 60958 channel-status fields, audio CRC controls/results, audio ramp generator controls, AFMT status, audio/VBI packet control, infoframe control, and audio source selection.
- Tail `DIG1` digital encoder/TMDS state: backend routing and enablement, TMDS sync/control characters, feedback, stereo-sync selection, DC balancer controls, generated TMDS control bits, DIG version/lane enablement, AFMT control, VBI packet control, generic packet control, and force-disable.
- `DP1` DisplayPort state under `dce_dc_dio_dp1_dispdec`: link status/training, pixel format, MSA colorimetry/misc/timing, lane configuration, video stream enable and timing, link framing, HBR2 eye pattern/test symbols, DPHY training/8b10b/PRBS/scrambler/CRC/FEC/fast-training controls, secondary-data-packet controls, audio M/N values, MST/MSE slot allocation and status, MSO controls, DSC mode and bytes-per-pixel, metadata transmission, double buffering, VBID misc, and ALPM link sleep/standby controls.
- `DIG2` digital encoder state under `dce_dc_dio_dig2_dispdec`: the same family of front-end, output CRC, HDMI, AFMT/audio/infoframe, backend, TMDS, lane, VBI, generic packet, and force-disable fields for digital encoder instance 2.
- Beginning `DP2` DisplayPort state under `dce_dc_dio_dp2_dispdec`: link status/training, pixel format/MSA/video-stream setup, DPHY training/test/CRC/FEC/fast-training fields, and initial secondary packet framing fields through `DP2_DP_SEC_FRAMING1`.

## Important API Surface

There are no callable APIs in this chunk. The exported surface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask already shifted into register position.
- Register comments such as `//DP1_DP_SEC_CNTL` or `//DIG2_HDMI_CONTROL` group fields by hardware register.
- Address-block comments identify instance windows: `dce_dc_dio_dp1_dispdec`, `dce_dc_dio_dig2_dispdec`, and `dce_dc_dio_dp2_dispdec`.

Representative `DIG1`/`DIG2` audio and HDMI macros include `DIG1_HDMI_DB_CONTROL__HDMI_DB_PENDING_MASK`, `DIG1_DME_CONTROL__METADATA_ENGINE_EN_MASK`, `DIG1_AFMT_GENERIC_HDR__AFMT_GENERIC_HB0_MASK`, `DIG1_HDMI_ACR_32_0__HDMI_ACR_CTS_32_MASK`, `DIG1_AFMT_60958_0__AFMT_60958_CS_CHANNEL_NUMBER_L_MASK`, `DIG1_AFMT_AUDIO_PACKET_CONTROL__AFMT_AUDIO_SAMPLE_SEND_MASK`, `DIG2_HDMI_CONTROL__HDMI_DATA_SCRAMBLE_EN_MASK`, `DIG2_AFMT_AUDIO_PACKET_CONTROL2__AFMT_AUDIO_CHANNEL_ENABLE_MASK`, `DIG2_AFMT_STATUS__AFMT_AUDIO_FIFO_OVERFLOW_MASK`, and `DIG2_DIG_BE_CNTL__DIG_MODE_MASK`.

Representative TMDS/DIG backend macros include `DIG1_DIG_BE_CNTL__DIG_FE_SOURCE_SELECT_MASK`, `DIG1_DIG_BE_EN_CNTL__DIG_BE_EN_MASK`, `DIG1_TMDS_SYNC_CHAR_PATTERN_0_1__TMDS_SYNC_CHAR_PATTERN0_MASK`, `DIG1_TMDS_DCBALANCER_CONTROL__TMDS_DCBALANCER_EN_MASK`, `DIG1_TMDS_CTL0_1_GEN_CNTL__TMDS_CTL0_DATA_SEL_MASK`, `DIG2_DIG_FE_CNTL__DIG_SOURCE_SELECT_MASK`, `DIG2_TMDS_CTL_BITS__TMDS_CTL0_MASK`, and `DIG2_FORCE_DIG_DISABLE__FORCE_DIG_DISABLE_MASK`.

Representative DisplayPort macros include `DP1_DP_LINK_CNTL__DP_LINK_TRAINING_COMPLETE_MASK`, `DP1_DP_PIXEL_FORMAT__DP_PIXEL_ENCODING_MASK`, `DP1_DP_CONFIG__DP_UDI_LANES_MASK`, `DP1_DP_VID_STREAM_CNTL__DP_VID_STREAM_ENABLE_MASK`, `DP1_DP_DPHY_CNTL__DPHY_FEC_EN_MASK`, `DP1_DP_DPHY_FAST_TRAINING_STATUS__DPHY_FAST_TRAINING_COMPLETE_OCCURRED_MASK`, `DP1_DP_SEC_CNTL__DP_SEC_GSP0_ENABLE_MASK`, `DP1_DP_MSE_SAT0__DP_MSE_SAT_SLOT_COUNT0_MASK`, `DP1_DP_DSC_CNTL__DP_DSC_MODE_MASK`, `DP1_DP_ALPM_CNTL__DP_ML_PHY_SLEEP_SEND_MASK`, `DP2_DP_LINK_CNTL__DP_EMBEDDED_PANEL_MODE_MASK`, `DP2_DP_DPHY_CNTL__DPHY_FEC_ACTIVE_STATUS_MASK`, and `DP2_DP_SEC_FRAMING1__DP_SEC_FRAME_START_LOCATION_MASK`.

Consumers generally do not treat these long identifiers as business logic. DCN code expands them through register-list and field-list macros, then passes the resulting addresses, shifts, and masks to helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_WAIT`, and related AMD display MMIO wrappers.

## Control Flow

This header has no local runtime control flow. The practical control flow is in the display driver that consumes the constants:

1. DCN 2.1 code includes `dcn_2_1_0_offset.h` for register addresses and this file for field layout.
2. Resource, GPIO, IRQ, DMUB, link encoder, audio, and stream-encoder setup code builds tables or inline helper arguments from the generated macro names.
3. Higher-level display code performs modeset, link training, stream enablement, audio setup, metadata packet programming, hotplug handling, or power-management operations.
4. Register helpers combine the target register address with the corresponding `__SHIFT` and `_MASK` values from this header to update or read packed hardware fields.

The control-sensitive flows represented by this chunk include HDMI scrambling/deep-color setup, HDMI/DP audio packet enablement, infoframe and generic packet scheduling, audio clock-regeneration programming, metadata double-buffer handoff, TMDS control-symbol generation, DisplayPort link training and video-stream enablement, secondary data packet transmission, MST slot allocation, DSC activation, DP CRC diagnostics, FEC and fast-training state, and ALPM sleep/standby requests.

Ordering, access type, volatility, reset values, and write-one-to-clear behavior are not encoded here. Callers must know when fields are status-only, sticky interrupt state, self-clearing, double-buffered, safe only while a stream is disabled, or synchronized to vblank/link-training hardware.

## State And Persistence Behavior

The file itself stores no software state and performs no persistence. It describes hardware register state that persists according to DCN 2.1.0 display-engine rules until software reprograms the block, hardware updates status bits, display power management resets the block, or the GPU resets.

State represented in this range includes:

- HDMI/audio payload state: ISRC/UPC bytes, MPEG infoframe bytes, generic packet headers and payload bytes, generic packet target lines, VBI/audio packet controls, ACR CTS/N values, audio infoframe bytes, IEC 60958 channel status, ramp generator values, CRC controls/results, audio FIFO/status flags, HBR state, and audio source selection.
- Metadata and double-buffer state: HDMI DB pending/taken/lock/disable fields, vupdate DB state, metadata engine enablement, requestor ID, stream type, and metadata DB pending/taken/disable fields.
- DIG/TMDS routing and electrical-symbol state: FE source selection, stereo-sync selection, start/bypass/input-pixel selection, backend mode, dual-link/swap/RB switch, HPD selection, symbol clock enablement, lane enablement, TMDS control characters, sync patterns, generated control bits, feedback paths, DC balancer controls, and force-disable state.
- DisplayPort link/video state: link training complete/status, embedded panel mode, pixel encoding/depth/combine, lane count, MSA colorimetry and timing parameters, video N/M, VBID, stream interrupt controls, link framing, DPHY test symbols, training patterns, 8b10b reset/dispersion, PRBS/scrambler controls, CRC configuration/readback, MST CRC phase status, FEC, fast training, and stream disable acknowledgements.
- DisplayPort secondary packet and MST/DSC state: ASP/ATP/AIP/ACM/GSP/MPG enable bits, ISRC and GSP send/line/deadline state, audio M/N values and readbacks, secondary packet timestamp/coding fields, MSE rate and slot allocation tables/status, MSO controls, DSC mode/slice width/bytes-per-pixel, metadata transmission, and ALPM sleep/standby pending bits.

Some fields are programmed configuration latches, some are live readbacks, some are interrupt/status acknowledgements, and some are update-pending indicators. A wrong mask or shift can therefore create state that survives until the next modeset, audio reconfiguration, hotplug sequence, suspend/resume cycle, or GPU reset.

## Dependencies And Integration Points

The direct companion for this file is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`

Direct include sites visible in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.c`

For this specific chunk, the strongest functional integration is the DCN stream/link encoder and audio machinery. Shared display code uses the generated instance fields to program HDMI and DisplayPort encoders during stream creation, audio endpoint setup, DP link training, infoframe/metadata packet updates, MST scheduling, DSC enablement, and low-power link transitions. IRQ and DMUB code may also consume related status/ack/mask fields when reporting display events or coordinating firmware-controlled display paths.

The instance suffixes are part of the contract. `DIG1` and `DIG2` are separate digital encoder instances, and `DP1` and `DP2` are separate DisplayPort encoder instances with mostly mirrored but not safely interchangeable field names. The matching `*_offset.h` entries, such as `mmDIG1_AFMT_ISRC1_4`, `mmDP1_DP_LINK_CNTL`, `mmDIG2_HDMI_CONTROL`, and `mmDP2_DP_SEC_FRAMING1`, provide the address side of the same generated contract.

Cross-generation headers such as `dcn_2_0_1_sh_mask.h`, `dcn_3_*_sh_mask.h`, and `dcn_4_*_sh_mask.h` contain similarly named fields but may add, remove, or move fields. Generated constants should be compared against the correct DCN 2.1.0 register database rather than copied across generations.

## Risks And Edge Cases

- Silent hardware misprogramming is the main risk. A wrong shift or mask compiles cleanly but can write adjacent bits, fail to acknowledge status, or leave the intended field unchanged.
- Repeated instance blocks are easy to confuse. `DIG1` versus `DIG2` and `DP1` versus `DP2` names often mirror each other, but instance-specific generated values and offsets must stay paired.
- Chunk boundaries are not semantic boundaries. This slice starts after earlier `DIG1_AFMT_ISRC1_*` definitions and ends before completing the `DP2` secondary packet/audio block, so absence of a field in this chunk does not imply absence from the file or hardware.
- HDMI audio and infoframe fields are packed byte-by-byte. Incorrect masks in `AFMT_GENERIC_*`, `AFMT_MPEG_INFO*`, `AFMT_AUDIO_INFO*`, or `AFMT_60958_*` can corrupt only selected payload bytes, making failures dependent on sink EDID, audio layout, or metadata type.
- Double-buffer and metadata fields have sequencing semantics outside this file. Misusing pending/taken/clear/lock/disable masks can drop packet updates, latch old metadata, or race vupdate handoff.
- DisplayPort link and DPHY fields are timing sensitive. Bad training, scrambler, PRBS, 8b10b, FEC, fast-training, or CRC masks can cause intermittent link-training failures, blank screens, or diagnostics that look valid but measure the wrong field.
- Secondary packet and MST/MSE fields combine source IDs, slot counts, line numbers, pending/deadline states, and status readbacks. Incorrect masks can affect only MST, DSC PPS/GSP packets, high-bandwidth audio, or specific stream counts.
- DSC fields are compact and mode-dependent. Incorrect `DP_DSC_MODE`, slice width, or bytes-per-pixel masks can produce stream corruption only when DSC is enabled.
- ALPM fields combine request and pending state. Confusing send and pending masks can wedge link low-power transitions or make power-management tests flaky.
- Status and acknowledge fields often sit next to mask fields with similar names, such as `*_MASK_MASK` generated identifiers. Consumers must distinguish hardware interrupt masks from C preprocessor masks.

## Test Signals

Useful validation for changes to this generated range is mostly build-time, generated-header comparison, and hardware display coverage:

- Build AMDGPU display code that includes `dcn_2_1_0_sh_mask.h`, especially DCN21 resource, IRQ, GPIO translation/factory, and DMUB translation units.
- Compare every shift/mask in this line range against the authoritative DCN 2.1.0 register database and the matching addresses in `dcn_2_1_0_offset.h`.
- Run HDMI modeset coverage across 8/10/12 bpc, deep color, scrambling, audio enable/disable, HBR audio, infoframes, generic packets, VBI packets, and metadata update paths.
- Run DisplayPort SST and MST coverage across link rates, lane counts, training retries, stream enable/disable, MSA timing/colorimetry changes, FEC where supported, fast training where supported, and CRC diagnostics.
- Exercise DSC over DP, including slice-width and bytes-per-pixel programming, and verify sink stability and visual correctness.
- Exercise secondary packet paths: audio M/N readback, ASP/ATP/AIP/ACM/GSP/MPG packet enablement, ISRC/generic packet scheduling, PPS/GSP sends, deadline-missed status, and metadata transmission.
- Stress hotplug, suspend/resume, runtime power transitions, ALPM sleep/standby, and repeated modesets while watching for stuck pending bits, missed acknowledgements, audio FIFO overflow, link retraining loops, and unexpected blanking.
- Use cross-generation diffs only as a sanity signal. Similar fields in other DCN headers help detect obvious generator drift, but DCN 2.1.0-specific generated values remain authoritative for this file.

## Cross-Chunk Notes

This is one large-file chunk from a generated shift/mask header. The final per-file reconciliation should merge it with adjacent `dcn_2_1_0_sh_mask.h` chunks to describe complete `DIG1`, `DP1`, `DIG2`, and `DP2` register families. This chunk should not be treated as a complete logical file report.
