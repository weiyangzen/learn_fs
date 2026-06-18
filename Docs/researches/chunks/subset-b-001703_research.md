# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 39588-41983

## Purpose

This chunk is generated AMD DCN 3.0 register field metadata. It contains no executable C code; it publishes `#define` constants for bit shifts and bit masks used to access fields inside DCN 3.0 display MMIO registers. Runtime display code pairs these field constants with register offsets from `dcn_3_0_0_offset.h` and with register helper macros such as `REG_UPDATE`, `REG_SET`, `REG_GET`, and `REG_WAIT`.

The range covers 2,172 shift/mask macros. It starts in the middle of the `DP0` DisplayPort secondary-data block, covers `VPG1`, `AFMT1`, `DME1`, `DIG1`, and a large `DP1` link/stream block, then enters the beginning of `VPG2`. Although this tree path is under a `ceph-client` source mirror, the file is AMDGPU display-driver hardware metadata and has no distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this chunk. The public interface is the macro naming contract:

- `<register>__<field>__SHIFT`: bit index for a field.
- `<register>__<field>_MASK`: bit mask for that field.
- Register comments, such as `//DP1_DP_DPHY_CNTL`, group the following field macros by hardware register.

Major register families in this chunk:

- `DP0_*`: secondary-data packet, audio `M/N`, MST multi-stream encoder allocation, MSA timing, MSO, DSC, metadata, ALPM, generic-stream-packet slots 8-11, and double-buffer status fields for DisplayPort instance 0.
- `VPG1_*`: generic packet RAM index/data, frame-update and immediate-update controls for generic packets 0-14, conflict status, memory power, ISRC data, and MPEG info fields.
- `AFMT1_*`: HDMI/DP audio formatter packet control, audio infoframe fields, IEC 60958 channel-status fields, ramp and CRC controls, status, source selection, infoframe update, and memory-power fields.
- `DME1_*`: metadata engine enable, requestor ID, stream type, source select, pixel format, line reference, line number, and memory-control fields.
- `DIG1_*`: digital stream encoder fields for front-end control, output CRC, clock/test/random patterns, FIFO status, HDMI metadata, HDMI control/status, audio/ACR/VBI/infoframe/generic-packet controls, AVMUTE/general-control, TMDS controls, lane enable, and forced disable.
- `DP1_*`: full DisplayPort instance 1 field coverage for link control, pixel format, MSA colorimetry/misc/timing/VBID, video stream, steer FIFO, video `M/N`, DPHY training/test/CRC/fast-training/FEC fields, secondary-data/audio/metadata fields, MST slot allocation, MSO, DSC, ALPM, generic-stream-packet controls, and double-buffer status.
- `VPG2_*`: beginning of generic packet access/data and update/status fields for video packet generator instance 2.

The chunk is consumed indirectly by DCN object declarations. Examples from nearby AMD display code include `VPG_DCN3_REG_LIST`, `DCN3_VPG_MASK_SH_LIST`, `AFMT_DCN3_REG_LIST`, `DCN3_AFMT_MASK_SH_LIST`, `SE_DCN3_REG_LIST`, `SE_COMMON_MASK_SH_LIST_DCN30`, and `LINK_ENCODER_MASK_SH_LIST_DCN30`. These macros copy the generated shifts into `struct dcn30_vpg_shift`, `struct dcn30_afmt_shift`, `struct dcn10_stream_encoder_shift`, and `struct dcn10_link_enc_shift`, and copy masks into matching `*_mask` structs.

## Control Flow

This header has no runtime control flow. The runtime sequence is provided by the display driver:

1. DCN30/302 resource, IRQ, GPIO, clock, and DMUB code includes `dcn_3_0_0_offset.h` and this matching `dcn_3_0_0_sh_mask.h`.
2. Resource construction in `dcn30_resource.c` creates register tables for VPG, AFMT, stream encoders, and link encoders. `SRI(...)` builds per-instance register addresses from the offset header, while `SE_SF(...)` and `LE_SF(...)` pull shift/mask fields from this header.
3. `dcn30_stream_encoder_create()` maps a `DIG` engine to matching VPG/AFMT/DME instances, allocates `struct dcn10_stream_encoder`, `struct vpg`, and `struct afmt`, and passes the generated register, shift, and mask tables into `dcn30_dio_stream_encoder_construct()`.
4. Link encoder construction uses the `DP0`-style field names from this header to initialize per-link `dcn10_link_enc_shift`/`mask` state for DP training, MST allocation, DPHY test patterns, AUX/HPD integration, and stream enablement.
5. Later modeset, hotplug, audio, DP, HDMI, DSC, metadata, and MST paths call helper macros that apply these shifts and masks to MMIO reads/writes.

The macro values do not encode sequencing. Correct order is still enforced by higher-level stream/link/audio code: link training, video timing programming, info-packet updates, audio setup, DSC PPS packet programming, metadata engine enablement, double-buffer commits, and status/ack polling all happen outside this generated file.

## State And Persistence Behavior

The file stores no software state and persists nothing on disk. It describes fields in persistent or semi-persistent GPU MMIO registers.

Hardware state represented here includes DP stream enablement, link/framing/timing settings, MST slot allocation, DPHY training/test/CRC state, secondary-data packet enables and send/pending/deadline state, audio `M/N` values, HDMI/TMDS packet generation, VPG generic packet RAM contents and update requests, AFMT audio channel/status fields, DSC enable and bytes-per-pixel fields, ALPM sleep/standby requests, and metadata packet scheduling.

Register persistence is hardware-defined. Configuration bits generally remain until another modeset, link reconfiguration, power-gating event, suspend/resume, or ASIC reset. Many status and control fields in this chunk are side-effect-sensitive: `*_PENDING`, `*_ACTIVE`, `*_STATUS`, `*_DEADLINE_MISSED`, `*_ACK`, `*_CLR`, `*_DB_TAKEN_CLR`, CRC-valid, FIFO-error, collision, conflict, fast-training-complete, and memory-power status fields may be read-only, sticky, write-one-to-clear, self-clearing, or timing-sensitive. This generated header only gives bit positions; consumers must know each field's access semantics.

## Dependencies And Integration Points

This chunk must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`, which provides the matching MMIO register addresses and base indices.
- DCN base-address definitions such as `DCN_BASE__INST0_SEG*`, used by resource macros to turn offsets into absolute MMIO addresses.
- AMD display helper macros in `reg_helper.h` and DCN resource code, which depend on the generated token names compiling exactly.

Key integration points in this source tree:

- `display/dc/resource/dcn30/dcn30_resource.c`: builds `vpg_regs`, `afmt_regs`, `stream_enc_regs`, `link_enc_regs`, `vpg_shift`, `afmt_shift`, `se_shift`, and `le_shift` from the generated constants.
- `display/dc/dcn30/dcn30_vpg.h` and `.c`: use `VPG_GENERIC_PACKET_ACCESS_CTRL`, `VPG_GENERIC_PACKET_DATA`, frame-update, immediate-update, and conflict fields for generic info-packet programming.
- `display/dc/dcn30/dcn30_afmt.h` and `.c`: use AFMT audio and IEC 60958 fields for HDMI/DP audio setup, mute, update, and memory-power control.
- `display/dc/dio/dcn30/dcn30_dio_stream_encoder.h` and `.c`: use DIG/HDMI/DP/DSC/metadata fields for stream attribute programming, info packets, DP audio, HDMI audio, DSC PPS packets, and state readback.
- `display/dc/dio/dcn10/dcn10_link_encoder.h` and link encoder implementations: use DP DPHY, link framing, MST slot allocation, and stream-enable fields for physical link setup and diagnostics.
- `display/dmub/src/dmub_dcn30.c` and `dmub_dcn302.c`: include the same DCN 3.0 generated headers for DMUB-facing register access.

## Risks And Edge Cases

- Register drift is the primary risk. These are untyped numeric constants; a wrong bit shift or mask can compile cleanly while programming or reading the wrong hardware field.
- The chunk is instance-heavy. `DP0`, `DP1`, `DIG1`, `VPG1`, `VPG2`, `AFMT1`, and `DME1` names are structurally similar, so copy-generation mistakes can affect only one connector, stream engine, packet generator, or audio formatter.
- Some runtime field lists use instance-0 field names as canonical mask/shift sources, for example `DP0_*`, `DIG0_*`, `VPG0_*`, and `AFMT0_*`. This works only if repeated instances have identical field layouts; any instance-specific layout difference requires explicit handling.
- Status/control fields are easy to misuse. Pending, ack, clear, collision, conflict, deadline-missed, CRC-valid, FIFO-error, and double-buffer bits often have hardware side effects or required polling windows.
- Packet update timing matters. VPG and HDMI generic packet frame/immediate updates, DP secondary packet sends, GSP line numbers, metadata packet line references, and double-buffer pending bits interact with vertical blank, line timing, and packet RAM locking.
- DisplayPort MST/MSO and DSC fields are coupled to link bandwidth and stream allocation decisions. Incorrect `DP_MSE_*`, `DP_MSO_*`, `DP_DSC_*`, or GSP PPS fields can produce failures only with MST, DSC, high refresh, high bpp, or multi-display modes.
- Audio failures can be subtle. Bad AFMT or DP secondary audio masks may only show as silent audio, incorrect channel status, bad IEC 60958 metadata, wrong audio clock regeneration, or packet underflow with specific sample rates.
- HDMI/TMDS packet fields cover many generic packet slots. Mask errors can corrupt AVI/audio/vendor/infoframe scheduling or cause missed metadata/AVMUTE behavior without a direct kernel error.

## Test Signals

Useful validation signals are mostly integration and hardware-facing:

- Build coverage for AMDGPU display with DCN30/302 paths enabled catches missing or renamed generated macros in `dcn30_resource.c`, `dcn30_vpg.h`, `dcn30_afmt.h`, stream encoder, link encoder, IRQ, GPIO, clock, and DMUB include paths.
- Boot and modeset on DCN 3.0 hardware with DP and HDMI outputs should show stable link training, no blank displays, correct hotplug, and no stream-disable or FIFO-level errors.
- DP audio and HDMI audio tests should verify audio presence, channel layout, mute/unmute, IEC 60958 channel-status fields, and sample-rate changes.
- Info-packet tests should exercise HDMI generic packets, DP secondary-data packets, metadata packets, ISRC/MPEG data, and immediate/frame update paths.
- MST validation should cover slot allocation, payload updates, multiple streams, and `DP_MSE_*` status/pending behavior.
- DSC validation should cover enabling/disabling DSC, PPS packet delivery through GSP11, slice width/bytes-per-pixel fields, and high-bandwidth modes.
- Low-power and eDP tests should watch ALPM sleep/standby fields and resume behavior.
- Diagnostic readback should monitor `*_PENDING`, `*_DEADLINE_MISSED`, `*_COLLISION_STATUS`, `VPG_GENERIC_CONFLICT_OCCURED`, HDMI packet missed/error, DIG FIFO error, DPHY CRC validity, fast-training complete, and double-buffer taken/pending bits.
