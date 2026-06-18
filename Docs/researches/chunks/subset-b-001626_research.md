# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 39692-42127

## Scope And Purpose

This chunk is generated AMD DCN 2.0 register field metadata. It contains only C preprocessor constants: `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` definitions. There are no functions, structs, enums, variables, allocation paths, locks, or executable control flow.

The range covers a display I/O section of the DCN 2.0 mask header:

- The tail of the `DIG0` stream encoder/audio formatter/TMDS field definitions, starting inside `DIG0_AFMT_GENERIC_1`.
- The complete `DP0` DisplayPort field block.
- The complete `DIG1` stream encoder/audio formatter/TMDS field block.
- The first part of the `DP1` DisplayPort field block, ending inside `DP1_DP_MSE_SAT2_STATUS`.

This file lives under a local `ceph-client` source mirror, but this header is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior, distributed storage state, or client-side filesystem logic.

The macros in this chunk provide bit positions and positioned masks for HDMI/AFMT audio and packet generation, DIG front-end/back-end control, TMDS output controls, DisplayPort link setup, DP stream timing, DP DPHY training and diagnostics, DP secondary-data packets, DP audio timing, DP MST/MSE virtual-channel allocation, DP MSO controls, DSC enablement, metadata packet transmission, ALPM, and selected status/readback surfaces.

## Important APIs, Types, And Macro Families

There are no callable APIs or C types in this range. The public interface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT` gives the low bit index of a hardware field.
- `REGISTER__FIELD_MASK` gives the already-positioned mask for that field.

The `DIG0` tail covers HDMI/AFMT and TMDS fields for stream encoder 0. Important families include:

- `DIG0_AFMT_GENERIC_1` through `DIG0_AFMT_GENERIC_7`, which pack bytes 4-31 of generic HDMI/AFMT packets.
- `DIG0_HDMI_GENERIC_PACKET_CONTROL1`, `DIG0_HDMI_GENERIC_PACKET_CONTROL5`, and `DIG0_AFMT_VBI_PACKET_CONTROL1`, which control generic packet line selection, continue/send/update behavior, frame update, and packet-indexed VBI behavior.
- `DIG0_HDMI_ACR_32_*`, `DIG0_HDMI_ACR_44_*`, `DIG0_HDMI_ACR_48_*`, and `DIG0_HDMI_ACR_STATUS_*`, which expose CTS/N values and readback fields for HDMI audio clock regeneration.
- `DIG0_AFMT_AUDIO_INFO*`, `DIG0_AFMT_60958_*`, `DIG0_AFMT_AUDIO_PACKET_CONTROL`, `DIG0_AFMT_AUDIO_SRC_CONTROL`, `DIG0_AFMT_AUDIO_CRC_*`, `DIG0_AFMT_RAMP_CONTROL*`, and `DIG0_AFMT_STATUS`, which describe HDMI/DP audio infoframes, IEC 60958 channel-status words, audio packet/sample/channel controls, test ramp generation, CRC diagnostics, and audio enable/layout state.
- `DIG0_DIG_BE_CNTL`, `DIG0_DIG_BE_EN_CNTL`, `DIG0_DIG_VERSION`, `DIG0_DIG_LANE_ENABLE`, `DIG0_AFMT_CNTL`, and `DIG0_FORCE_DIG_DISABLE`, which describe stream encoder back-end routing, enablement, mode/source selection, DIO output disable, lane enables, AFMT audio clocking, and force-disable behavior.
- `DIG0_TMDS_*`, which describe TMDS control characters, control-bit generation, DC balancer programming, sync/DC-balance characters, stereosync selection, and per-control-symbol generation settings.

The `DP0` block is complete in this chunk. It includes:

- Link and stream controls: `DP0_DP_LINK_CNTL`, `DP0_DP_CONFIG`, `DP0_DP_VID_STREAM_CNTL`, `DP0_DP_LINK_FRAMING_CNTL`, `DP0_DP_PIXEL_FORMAT`, `DP0_DP_MSA_COLORIMETRY`, `DP0_DP_MSA_MISC`, `DP0_DP_VID_TIMING`, `DP0_DP_VID_N`, `DP0_DP_VID_M`, `DP0_DP_VID_MSA_VBID`, and `DP0_DP_MSA_VBID_MISC`.
- DPHY training and diagnostics: `DP0_DP_DPHY_CNTL`, training pattern selection, symbol registers, 8b/10b control, PRBS, scrambler, CRC enable/control/result, MST CRC, fast-training controls/status, BS/SR swap controls, and HBR2 pattern control.
- Secondary-data and audio transport: `DP0_DP_SEC_CNTL`, `DP0_DP_SEC_CNTL1` through `DP0_DP_SEC_CNTL7`, `DP0_DP_SEC_FRAMING1` through `DP0_DP_SEC_FRAMING4`, `DP0_DP_SEC_AUD_N`, `DP0_DP_SEC_AUD_M`, readback registers, timestamp mode, packet control, and metadata transmission.
- MST/MSE/MSO allocation and status: `DP0_DP_MSE_RATE_CNTL`, `DP0_DP_MSE_RATE_UPDATE`, `DP0_DP_MSE_SAT0` through `SAT2`, `DP0_DP_MSE_SAT_UPDATE`, `DP0_DP_MSE_LINK_TIMING`, `DP0_DP_MSE_MISC_CNTL`, `DP0_DP_MSE_SAT*_STATUS`, `DP0_DP_MSO_CNTL`, and `DP0_DP_MSO_CNTL1`.
- Compression, double-buffer, and low-power controls: `DP0_DP_DSC_CNTL`, `DP0_DP_DSC_BYTES_PER_PIXEL`, `DP0_DP_DB_CNTL`, and `DP0_DP_ALPM_CNTL`.

The `DIG1` block repeats the stream encoder/audio formatter/TMDS layout for instance 1 and is complete in this range. It starts at `DIG1_DIG_FE_CNTL`, includes output CRC, clock/test/random pattern controls, FIFO status, HDMI packet/audio/ACR/infoframe/generic controls, metadata and DME controls, AFMT MPEG/generic/audio/60958/CRC/ramp/status controls, DIG back-end controls, TMDS controls, version/lane enable, AFMT VBI controls, and force-disable.

The `DP1` block repeats the `DP0` DisplayPort layout for instance 1 but is partial here. This chunk includes link, pixel/MSA, stream, DPHY, secondary-data, audio, MSE allocation, and MSE status fields through `DP1_DP_MSE_SAT2_STATUS`; `DP1_DP_MSA_TIMING_PARAM1` and later DP1 fields continue after the requested line range.

## Control Flow And Data Flow

The header has no runtime control flow. Its effective data flow is compile-time macro substitution:

1. DCN 2.0 display code includes `dcn_2_0_0_offset.h` for register addresses and `dcn_2_0_0_sh_mask.h` for field layouts.
2. Resource and block headers use generated table macros such as `SE_SF()` and `LE_SF()` to copy `__SHIFT` and `_MASK` constants into per-block shift/mask structures.
3. Runtime code uses `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, `REG_READ`, `REG_WRITE`, or SOC15 register helpers to compose or decode the fields.
4. Hardware interprets the resulting register values as stream encoder, link encoder, audio packet, DP link, MST, metadata, DSC, timing, diagnostic, or low-power state.

Representative local consumers show this pattern. `display/dc/dio/dcn10/dcn10_stream_encoder.h` maps many fields from this chunk into the stream encoder register/mask tables, including AFMT generic packet bytes, HDMI ACR values, DP pixel format, DP MSA timing, DP MSE rate/update, DP secondary-data controls, DP audio N/M readbacks, and HDMI/AFMT audio controls. `display/dc/dio/dcn10/dcn10_link_encoder.h` maps DP link encoder fields such as `DIG_BE_CNTL`, `TMDS_CTL_BITS`, `DP_DPHY_*`, `DP_LINK_CNTL`, `DP_LINK_FRAMING_CNTL`, `DP_MSE_SAT*`, `DP_MSE_SAT_UPDATE`, `DP_SEC_CNTL`, and `DP_VID_STREAM_CNTL`. `display/dc/resource/dcn20/dcn20_resource.c` includes the DCN 2.0 generated headers and instantiates the shift/mask tables used by DCN20 resources.

The chunk also aligns with older DCE/DCE10-style direct uses in this tree. For example, DCE HDMI audio code uses `HDMI_ACR_32_0__HDMI_ACR_CTS_32__SHIFT` and related ACR fields to program HDMI N/CTS values, while DCN link encoder code uses the `DP_MSE_SAT*` and `DP_MSE_SAT_UPDATE` fields to program DP MST stream allocation tables and wait for the SAT update/keepout status to clear.

## State And Persistence Behavior

This file stores no software state and persists nothing itself. The constants describe state held in DCN 2.0 display hardware registers. That hardware state can persist until modeset, link retraining, audio reconfiguration, MST payload update, suspend/resume restore, power-gating transition, GPU reset, firmware action, or an explicit register write changes it.

State represented by this chunk includes:

- HDMI/AFMT packet state: generic packet payload bytes, packet header bytes, packet send/update/continue controls, metadata packet controls, infoframe controls, VBI packet controls, and double-buffer status bits.
- Audio state: HDMI ACR CTS/N programming and status readback, AFMT audio infoframe payload, IEC 60958 channel-status values, audio layout/channel/sample controls, audio source selection, CRC/test-ramp controls, and audio enable/status bits.
- Stream encoder and TMDS state: DIG source/backend selection, enable bits, lane enables, force-disable flags, TMDS control characters, TMDS control symbols, DC balancer configuration, sync characters, and test/CRC/pattern controls.
- DisplayPort link and stream state: lane count, enhanced framing, link training complete, stream enable, pixel encoding/depth, MSA timing/colorimetry/misc/VBID values, video timing, M/N values, FIFO steering, and DP double-buffer controls.
- DisplayPort PHY state: DPHY reset/bypass/test selections, training patterns, programmed symbols, PRBS and scrambler controls, CRC selection/results, MST CRC status, fast-training status, HBR2 pattern selection, and BS/SR swap state.
- DisplayPort secondary-data and audio state: SDP stream/ASP/ATP/AIP/ACM/GSP/MPG enables, send/pending/deadline flags, line references and line numbers, packet framing widths, audio N/M/readback, timestamp mode, audio packet coding/version/channel-count fields, and metadata transmission line/enable fields.
- MST/MSO/DSC/ALPM state: MSE rate numerator/denominator, SAT source/slot count rows and status readbacks, SAT update and 16-MTP keepout state, MSO per-SST-link enables, DSC mode/bytes-per-pixel fields, and ALPM enable/timing controls.

Some fields are durable configuration bits; others are live status bits, readback counters, update-pending bits, self-clearing command bits, sticky error/status bits, or write-one-to-clear acknowledgements. The header does not encode access type or reset value, so callers must rely on hardware documentation and existing block helpers when deciding whether read-modify-write is safe.

## Dependencies And Integration Points

This chunk depends on the generated AMD DCN 2.0 ASIC register set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h` supplies the matching `mm...` register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/soc15/navi10_ip_offset.h` and related base helpers supply the IP segment bases used with the offsets.
- AMD display register helper layers provide `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, `SE_SF`, `LE_SF`, `SRI`, and related table-building macros.

Direct include points for `dcn_2_0_0_sh_mask.h` in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

Practical integration points are DRM/KMS stream encoder setup, HDMI mode programming, HDMI/DP audio enablement, infoframe and generic metadata packet transmission, DP link training, DP stream enable/disable, DP MST virtual-channel payload programming, DP MSO configuration, DP DSC setup, ALPM, link diagnostics/CRC, stream encoder output CRC, force-disable/recovery paths, hotplug-driven modesets, suspend/resume state restoration, and debug register snapshots.

## Risks And Edge Cases

- A wrong shift or mask can compile cleanly while corrupting the wrong hardware bit. In this chunk that can break HDMI audio clocking, infoframes, DP stream timing, link training, MST payload allocation, DSC/MSO setup, ALPM, metadata packets, or diagnostic readback.
- The chunk boundaries are artificial. The first line is inside `DIG0_AFMT_GENERIC_1` and the last line is inside `DP1_DP_MSE_SAT2_STATUS`; the final per-file report must merge adjacent chunks before claiming complete `DIG0` or `DP1` coverage.
- `DIG0`/`DIG1` and `DP0`/`DP1` are repeated instance blocks. Copy or generator drift can affect one connector/stream instance while the other continues to work, so validation must cover more than instance 0.
- Status and command fields require careful semantics. `*_SEND_PENDING`, `*_SEND_DEADLINE_MISSED`, `*_UPDATE_PENDING`, `DP_MSE_SAT_UPDATE`, `DP_MSE_16_MTP_KEEPOUT`, CRC done/result fields, fast-training status, DB pending/taken fields, and force-disable controls should not be treated as ordinary read/write storage.
- Audio fields are tightly packed. Incorrect ACR CTS/N, 60958 channel-status, audio layout, channel enable, sample-send, or source-selection masks can produce silent audio, drift, wrong channel mapping, or failures only for specific sample rates.
- DP MST fields are sequencing-sensitive. SAT source/slot rows must be programmed consistently, then committed through `DP_MSE_SAT_UPDATE`, and software must wait for update and keepout status before depending on the allocation. Bad masks here can produce bandwidth allocation failures that only appear with MST docks or multi-stream displays.
- DP MSA/timing fields are display-critical. Incorrect horizontal/vertical total/start/sync/active width, polarity, pixel format, M/N, or VBID masks can cause black screens, unstable timing, wrong color depth, or receiver-side link errors.
- TMDS and HDMI packet controls interact with link mode. Bad TMDS control/DC-balance/encoding or HDMI deep-color/scrambling/infoframe fields can cause HDMI-only failures, especially at high pixel clocks or deep-color modes.
- Some fields are present for diagnostics or test modes, including PRBS, CRC, random/test pattern, ramp, and HBR2 pattern controls. Accidentally enabling them through wrong masks can disrupt normal scanout or link training.

## Test Signals

Useful validation combines generated-header checks, build coverage, and hardware behavior:

- Build AMDGPU/DC with DCN 2.0 support enabled. Missing or renamed macros should fail in DCN20 resource, stream encoder, link encoder, DMUB, IRQ, GPIO, clock-manager, and GMC/DC integration paths.
- Diff every `__SHIFT`/`_MASK` pair in this range against AMD's authoritative DCN 2.0 register database or a known-good upstream header. Check that masks fit 32-bit registers and match the bit widths implied by the field names.
- Exercise both stream/link instances represented here: HDMI and DP modes on ports using DIG0/DP0 and DIG1/DP1, including hotplug, modeset, blank/unblank, suspend/resume, and GPU reset restore.
- Validate HDMI/AFMT behavior with AVI/audio infoframes, generic packets, metadata packets, ACR generation at 32/44.1/48 kHz families, IEC 60958 channel status, multi-channel audio, audio CRC/status readback, and high-clock TMDS modes.
- Validate DP link behavior with lane-count changes, link training patterns, enhanced framing, scrambler/PRBS paths where testable, stream enable/disable, pixel format/depth changes, MSA timing, M/N values, and DPHY CRC/debug readback.
- Validate MST/MSO paths with MST hubs or docks: SAT source/slot programming, SAT update completion, 16-MTP keepout handling, MSE rate programming, MSE status readback, per-stream allocation changes, and teardown/reallocation.
- Validate DSC and ALPM where supported by hardware and sink capabilities, including DSC enable/disable, bytes-per-pixel programming, metadata transmission, low-power transitions, and link recovery.
- Monitor negative signals in kernel logs and user-visible behavior: black screens, flicker, bad color depth, missed vblank or page-flip completion, DP link-training failure, MST allocation failure, no HDMI/DP audio, audio drift/channel-map errors, malformed infoframes, AUX/HPD recovery loops, interrupt storms, CRC mismatches, or resume-only display failures.

## Cross-Chunk Notes

Adjacent chunks are required for the final per-file research document. Earlier lines define the start of the `DIG0` stream encoder block and `DIG0_AFMT_GENERIC_0`; later lines complete `DP1` with MSA timing, MSO, DSC, secondary-data, double-buffer, metadata, and ALPM fields before moving on to later DIG/DP instances. This chunk should be reconciled as a DIO/DIG/DP field-layout slice, not as an independently complete hardware block.
