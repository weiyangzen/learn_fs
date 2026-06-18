# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 34963-37371

## Scope

This chunk is generated AMDGPU DCN 3.1.6 register shift/mask metadata. It contains C preprocessor constants only: no functions, structs, enums, variables, includes, locks, allocation paths, or executable control flow. The covered range has 2,409 source lines, 2,168 `#define` lines, 235 register/address-block comments, and 233 visible register groups.

The chunk starts inside `DIG0_HDMI_GENERIC_PACKET_CONTROL5`: the first visible lines are the tail of HDMI generic-packet immediate-send shift definitions and the complete mask list for generic packets 0 through 14. It ends inside `DP2_DP_SEC_CNTL7`, after the `DP_SEC_GSP1_SEND_ACTIVE` mask and before the remaining `DP_SEC_CNTL7` masks. Adjacent chunks are needed before making whole-register or whole-file claims.

Although this file lives under a local `ceph-client` mirror, the content is AMD display-controller hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this range is to expose bit positions and masks for DCN 3.1.6 display output blocks. Consumers combine these constants with matching register offsets from `dcn_3_1_6_offset.h` and AMD display register helpers to program memory-mapped display registers.

The macro convention is:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating or updating that field.
- `// addressBlock: ...` comments: generated grouping metadata for the following replicated register block.

The covered hardware areas are:

- Tail of `DIG0` HDMI generic-packet control and the rest of `DIG0` HDMI/TMDS/backend control.
- Full `DP1` DisplayPort link, video, PHY, secondary-data, audio, MSE/MSO, DSC, and GSP metadata controls.
- Full `DIG1` frontend, HDMI, TMDS, backend, CRC/test-pattern, FIFO/status, and force-disable controls.
- Start through middle of `DP2` DisplayPort controls, ending in secondary-packet active/idle status for GSP streams.

## Important Definitions

There are no callable APIs in this chunk. The public surface is the generated macro namespace.

Important `DIG0` and `DIG1` groups:

- `DIG*_HDMI_GENERIC_PACKET_CONTROL*`: enable, line-number, immediate-send, pending, double-buffer-pending, and generic packet scheduling fields for HDMI generic packets 0 through 14. The `DIG0` section starts at the tail of control register 5; the `DIG1` section includes metadata packet control, generic-packet control 0/1/2/3/4/5/6/7/8/9/10, and double-buffer control.
- `DIG*_HDMI_GC`: HDMI general-control packet fields including AVMUTE, continuous AVMUTE, default phase, packing phase, and packing override.
- `DIG*_HDMI_ACR_*` and `DIG*_HDMI_ACR_STATUS_*`: audio clock regeneration CTS/N fields for 32 kHz, 44.1 kHz, 48 kHz, plus status readback values.
- `DIG*_AFMT_CNTL`: audio formatting clock enable/status fields.
- `DIG*_DIG_BE_CNTL` and `DIG*_DIG_BE_EN_CNTL`: digital backend enable, symbol clock status, dual-link, swap, red/blue switch, frontend source select, mode, and HPD select fields.
- `DIG*_TMDS_*`: TMDS sync phase, control-character output enables, feedback, stereo-sync selection, sync-character patterns, control bits, DC balancer control, DC-balance character, and generated control-character fields.
- `DIG*_DIG_FE_CNTL`, `DIG*_DIG_OUTPUT_CRC_*`, `DIG*_DIG_CLOCK_PATTERN`, `DIG*_DIG_TEST_PATTERN`, `DIG*_DIG_RANDOM_PATTERN_SEED`, and `DIG*_DIG_FIFO_STATUS`: frontend enable/source/test/debug path, output CRC, clock/test/random pattern generation, and FIFO status for the `DIG1` frontend side.
- `DIG*_DIG_VERSION` and `DIG*_FORCE_DIG_DISABLE`: block version and force-disable bits.

Important `DP1` and `DP2` groups:

- `DP*_DP_LINK_CNTL`, `DP*_DP_PIXEL_FORMAT`, `DP*_DP_MSA_COLORIMETRY`, `DP*_DP_CONFIG`, and `DP*_DP_VID_STREAM_CNTL`: core DisplayPort link enable/configuration, pixel encoding, main-stream attributes, enhanced framing, training/start/stop controls, video stream enable, and stream status fields.
- `DP*_DP_MSA_MISC` and `DP*_DP_MSA_TIMING_PARAM1` through `PARAM4`: packed MSA color/depth/misc and timing fields for horizontal/vertical total, start, sync width, polarity, and active width/height.
- `DP*_DP_VID_N`, `DP*_DP_VID_M`, `DP*_DP_VID_MSA_VBID`, and `DP*_DP_VID_INTERRUPT_CNTL`: video timing generator M/N values, VBID/MSA fields, and interrupt control/status around stream timing.
- `DP*_DP_DPHY_*`: DisplayPort PHY control, training pattern selection, per-symbol training controls, 8b/10b control, PRBS, scrambling, CRC enable/control/result, MST CRC status, fast-training control/status, byte/serializer swap, and HBR2 pattern controls.
- `DP*_DP_SEC_*`: secondary-data packet control, framing, audio N/M and readback, timestamps, packet control, generic secondary packet send/pending/deadline/any-line controls, line-number controls, double-buffer disable/status, active/idle status, and GSP metadata controls.
- `DP*_DP_MSE_*`: multi-stream transport scheduling fields, including rate control/update, SAT slots/status, link timing, and miscellaneous control.
- `DP*_DP_MSO_CNTL`, `DP*_DP_MSO_CNTL1`, and `DP*_DP_DSC_CNTL`: multi-stream operation enable masks for secondary packets and Display Stream Compression mode/slice-width fields.
- `DP*_DP_DSC_BYTES_PER_PIXEL`, `DP*_DP_ALPM_CNTL`, and `DP*_DP_GSP8_CNTL` through `GSP11_CNTL`: later DP metadata controls present in `DP1`; the `DP2` range has not reached all of these by the chunk end.

## Control Flow

This header has no runtime branches or calls. Runtime sequencing is provided by AMDGPU display code:

1. DCN316 resource and DMUB code include `dcn_3_1_6_offset.h` and this `dcn_3_1_6_sh_mask.h` file.
2. `dcn316_resource.c` defines DCN base segments, then expands register-list and field-list macros for display output resources.
3. `dmub_dcn316.c` expands DMUB register and field lists into `dmub_srv_dcn316_regs`, using `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)` to copy generated constants into firmware-facing register tables.
4. Runtime stream-encoder, link-encoder, audio, HDMI, and DisplayPort code uses register helper paths such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WRITE`, `REG_READ`, and polling helpers to program fields described by this chunk.

The macros only encode bit layout. They do not encode ordering requirements for link training, HDMI packet programming, double-buffer commits, audio clock regeneration, stream enable/disable, MST scheduling, DSC setup, interrupt clearing, or status polling.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on disk. It describes MMIO-backed GPU display state:

- HDMI generic-packet and metadata state: packet enables, packet line targets, immediate-send requests, pending status, double-buffer pending state, AVMUTE/general-control behavior, metadata packet control, infoframe controls, VBI/audio/ACR packet control, and HDMI status.
- HDMI audio state: ACR N/CTS values for common sample-rate families, readback/status values, AFMT audio clock enable/on state, and audio packet controls.
- TMDS and digital backend state: sync/control-character generation, DC balancing, dual-link/backend enable, frontend source selection, output mode, HPD selection, symbol clock status, FIFO status, test patterns, output CRC, and force-disable state.
- DisplayPort link and video state: link control, pixel format, stream enable/status, M/N timing, MSA/VBID fields, enhanced framing, training patterns, DPHY symbols, scrambling, PRBS, CRC, and fast-training state.
- DisplayPort secondary-data state: audio packets, timestamps, secondary-packet framing, GSP sends, packet pending/deadline status, per-packet line numbers, double-buffer disable/status, active/idle status, and metadata packet controls.
- MST/MSO/DSC state: MSE rate/SAT/link timing, MSO secondary stream packet enables, DSC mode/slice width, and bytes-per-pixel fields.

Persistence is hardware-defined. Configuration fields usually remain until modeset reprogramming, link retraining, stream disable, power gating, suspend/resume restore, or ASIC reset. Status, pending, deadline-missed, taken, clear, active, idle, CRC, interrupt, and readback fields may be read-only, sticky, self-clearing, or write-one-to-clear depending on the hardware register. This generated header does not express access type or side effects.

## Dependencies And Integration Points

This chunk depends on the AMD-generated DCN 3.1.6 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h`, which supplies matching MMIO offsets and base-index macros.
- DCN316 base segment definitions in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`.
- DCN316 DMUB register table construction in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`.
- Common AMD display register helper macros that derive fields through generated names, including `FD_MASK`, `FD_SHIFT`, and `REG_*` helper families.

Important consumer areas:

- DCN316 resource construction uses this namespace while creating stream encoder, audio, DIO, and related display output resources.
- HDMI stream-encoder paths consume `DIG*_HDMI_*`, `DIG*_AFMT_*`, and `DIG*_TMDS_*` fields for infoframes, generic packets, audio setup, AVMUTE, TMDS formatting, and backend enable/disable.
- DisplayPort stream/link paths consume `DP*_DP_LINK_*`, `DP*_DP_DPHY_*`, `DP*_DP_MSA_*`, `DP*_DP_VID_*`, and `DP*_DP_CONFIG` fields for link training, stream timing, colorimetry, video enable, scrambling, PRBS, and CRC.
- MST/MSO/DSC code consumes `DP*_DP_MSE_*`, `DP*_DP_MSO_*`, `DP*_DP_SEC_*`, and `DP*_DP_DSC_*` fields for multi-stream scheduling, secondary-data packet transmission, DSC PPS/metadata, and line-targeted packet sends.
- DMUB firmware-facing support uses selected generated masks/shifts in `dmub_srv_dcn316_regs`, so field names shared with `DMUB_DCN31_FIELDS()` must remain stable.

## Risks And Edge Cases

- Field drift is the central risk. These are untyped constants; a wrong shift or mask can compile cleanly while programming the wrong MMIO bits.
- Chunk boundaries are not semantic. `DIG0_HDMI_GENERIC_PACKET_CONTROL5` is incomplete at the start, and `DP2_DP_SEC_CNTL7` is incomplete at the end. Adjacent chunks must be merged for complete register-pair validation.
- Repeated output instances are copy-sensitive. `DIG0`/`DIG1` and `DP1`/`DP2` blocks are similar but not interchangeable; instance-prefixed fields must match the selected encoder/link instance.
- HDMI packet controls include pending and double-buffered state. Misprogramming immediate-send, line-number, pending, or DB fields can drop infoframes/metadata, send stale packets, or leave packet state stuck.
- HDMI ACR and audio fields affect sink audio lock. Incorrect N/CTS masks or packet controls can produce silent audio, clock drift, or sample-rate-specific failures.
- TMDS/backend controls are mode-sensitive. Wrong control-character, packing, DC-balance, frontend source, backend enable, mode, or HPD fields can cause blank output, link errors, or bad HDMI/DVI behavior.
- DisplayPort DPHY and training fields are link-critical. Incorrect training-pattern, symbol, scrambling, PRBS, CRC, fast-training, or HBR2 pattern masks can cause training failure or intermittent high-rate link instability.
- MSA/VBID/timing fields are packed and sink-visible. Bad masks can produce incorrect active size, sync polarity, colorimetry, dynamic range, stream attributes, or VBID state.
- Secondary-packet and GSP send fields are timing-sensitive. Wrong send, pending, deadline, any-line, line-number, active/idle, or DB-disable fields can lose HDR/static metadata, DSC PPS, audio timestamps, or other sideband packets.
- MST/MSO and DSC fields are tightly coupled to stream allocation and compression setup. Bad masks can corrupt slot allocation, secondary stream enables, DSC mode, slice width, or bytes-per-pixel programming.
- Status/clear/interrupt fields may have side effects that are not represented here. Driver code must rely on hardware documentation and existing helpers for write-one-to-clear, readback, and polling semantics.

## Test Signals

Useful validation is mostly compile-time, generated-header consistency, and hardware integration:

- Build AMDGPU/DC with DCN316 enabled. Undefined or renamed field macros should fail in `dcn316_resource.c`, `dmub_dcn316.c`, and shared HDMI/DP/DIO/stream-encoder users.
- Mechanically verify that each visible `__SHIFT` field in this range has the expected companion `_MASK` field where the generated schema defines one, while allowing the known leading and trailing boundary exceptions.
- Compare this slice against AMD's authoritative DCN 3.1.6 register database and adjacent DCN 3.1.x headers where block layouts are expected to match.
- Exercise HDMI modes that use generic packets, infoframes, metadata packets, AVMUTE, ACR audio, TMDS control-character generation, DVI/HDMI mode switching, and audio sample rates 32 kHz, 44.1 kHz, and 48 kHz.
- Exercise DisplayPort SST and MST links across link rates and lane counts, including training/retraining, scrambling, PRBS/CRC diagnostics, MSA timing/colorimetry, VBID, hotplug, suspend/resume, and stream enable/disable.
- Validate DSC and metadata paths with HDR/static metadata, DSC PPS packets, GSP packets, MSO/MST secondary packet enables, and line-targeted sends. Watch for deadline-missed, stuck-pending, active/idle, or double-buffer status anomalies.
- Run DRM page-flip and modeset tests across outputs backed by `DIG0`/`DIG1` and `DP1`/`DP2`, checking for blank screens, link training failures, metadata loss, audio dropouts, CRC/test-pattern mismatches, and resume-only regressions.

## Cross-Chunk Notes

- Prefix distribution in this range: 34 visible `DIG0` register groups, 52 `DIG1` groups, 78 `DP1` groups, 68 `DP2` groups, and three address-block comments.
- `DIG0` starts mid-HDMI generic-packet control; earlier `DIG0` HDMI metadata/control/status fields are in the previous chunk.
- `DP2` continues after this chunk with the rest of `DP2_DP_SEC_CNTL7` and later DP2 DB/MSA metadata/GSP status fields.
- The final per-file research document should be produced later by the reconciliation lane after all chunks for `dcn_3_1_6_sh_mask.h` are available.
