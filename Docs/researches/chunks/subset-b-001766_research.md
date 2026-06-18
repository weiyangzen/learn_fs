# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 37089-39485

## Scope

This chunk is part of the generated DCN 3.0.2 shift/mask register header used by the AMD display driver. The range begins in the tail of the `VPG2_VPG_GSP_FRAME_UPDATE_CTRL` definitions, covers the remaining DIG2 display-output register blocks, covers all of the DP2 block in this file, and then starts the DIG3 block through the beginning of `DIG3_HDMI_GENERIC_PACKET_CONTROL5`.

The chunk contains macro constants only. There are no C functions, structs, or executable control-flow bodies in this range. Its 2,170 `#define` entries map hardware register bit fields to paired `__SHIFT` and `_MASK` constants that higher-level register-helper macros use to build read/modify/write operations.

Major register families covered here are:

- `VPG2_*`: video packet generator generic-packet update, immediate-update, status, memory-power, ISRC, and MPEG info fields for DIG2.
- `AFMT2_*`: audio formatter packet, audio infoframe, IEC 60958 channel-status, CRC, ramp, status, source, infoframe update, and memory-power fields for DIG2.
- `DME2_*`: metadata-engine enable, HUBP requestor, stream type, and light-sleep/power-state fields for DIG2.
- `DIG2_*` and `DIG3_*`: front-end/back-end controls, HDMI control, audio clock regeneration, metadata, VBI/infoframe/generic-packet controls, TMDS patterns, FIFO status, CRC, double-buffering, and link-disable controls.
- `DP2_*`: DisplayPort stream enable/status, timing M/N generation, main-stream attributes, PHY training/test/CRC/scrambler controls, secondary-data-packet controls, MST/MSE slot allocation, DSC, ALPM, metadata transmission, and GSP controls for secondary-data packets 8-11.
- The beginning of the DIG3 VPG/AFMT/DME/DIG/HDMI families, mirroring the DIG2 layout for engine instance 3.

## Purpose

The purpose of this header chunk is to provide the authoritative bit layout for DCN 3.0.2 display-output register fields. The runtime display code does not hard-code bit positions. Instead, resource construction code includes this header and populates per-block shift/mask tables. Register helpers such as `REG_UPDATE`, `REG_UPDATE_2`, `REG_SET_*`, and `REG_GET` then use those tables to pack field values into MMIO register writes or extract fields from MMIO reads.

This chunk is therefore a hardware-description layer, not a behavior implementation layer. Correctness depends on exact alignment with the ASIC register specification: if a shift or mask is wrong, otherwise-correct driver logic can write the wrong bits for HDMI info packets, DP stream state, metadata packets, audio format, DSC, or link-training support.

## Important APIs, Types, And Macros

The direct "APIs" exported by this chunk are preprocessor symbols in the form:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

For example, HDMI generic-packet fields are emitted for both DIG2 and DIG3 register instances, including send/continuous/line-reference/update-lock fields for generic packets 0-14 and immediate-send/pending fields. The fields are split across control registers: packets 0-7 primarily use `HDMI_GENERIC_PACKET_CONTROL0`, packets 8-14 use `HDMI_GENERIC_PACKET_CONTROL6`, line numbers live in packet-control registers 1-4 and 7-10 in surrounding chunks, and immediate sends use `HDMI_GENERIC_PACKET_CONTROL5`.

The important consumers are not in this header but in the AMD display register framework:

- `drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c` includes `dcn_3_0_2_offset.h` and this file, then builds static shift/mask tables such as `vpg_shift`, `vpg_mask`, `afmt_shift`, `afmt_mask`, `se_shift`, and `se_mask`.
- `DCN3_VPG_MASK_SH_LIST`, `DCN3_AFMT_MASK_SH_LIST`, and `SE_COMMON_MASK_SH_LIST_DCN30` expand through `SF`/`SE_SF` style macros to reference these generated `__SHIFT` and `_MASK` symbols.
- `dcn302_stream_encoder_create()` maps stream engines through DIGE to matching VPG and AFMT instances, then calls `dcn30_dio_stream_encoder_construct()` with the register table and this chunk's shift/mask data.
- `drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_stream_encoder.[ch]` uses the resulting tables when programming HDMI info packets, DP secondary data packets, metadata transmission, DSC controls, MSA timing fields, audio controls, and DME metadata fields.

The relevant runtime objects include `struct dcn10_stream_encoder`, `struct dcn10_stream_encoder_shift`, `struct dcn10_stream_encoder_mask`, `struct dcn30_vpg`, `struct dcn30_vpg_shift`, `struct dcn30_vpg_mask`, `struct dcn30_afmt`, `struct dcn30_afmt_shift`, and `struct dcn30_afmt_mask`.

## Control Flow

There is no local control flow in the chunk. All behavior appears when another compilation unit expands the macros into register metadata and passes that metadata into helper calls.

The effective runtime flow is:

1. DCN302 resource initialization includes this generated header.
2. Static register, shift, and mask tables are built from macro-list expansions.
3. Stream encoder, VPG, and AFMT objects are constructed with pointers to those tables.
4. Output paths call stream-encoder methods for HDMI, DP, audio, metadata, DSC, and infoframe programming.
5. Register helpers combine field values with the `__SHIFT` and `_MASK` constants from this header to perform MMIO read/modify/write operations.

For HDMI generic packets, `enc3_update_hdmi_info_packet()` chooses a packet index and writes `HDMI_GENERIC*_CONT`, `HDMI_GENERIC*_SEND`, and `HDMI_GENERIC*_LINE` fields. The DIG2/DIG3 definitions in this chunk provide the bit positions and masks used by those writes. For DP secondary packets, the stream encoder and related paths update fields such as `DP_SEC_STREAM_ENABLE`, `DP_SEC_GSP*_ENABLE`, `DP_SEC_GSP*_SEND`, line numbers, active/pending status, and PPS/DSC controls through the same shift/mask mechanism.

## State And Persistence Behavior

The header has no persistent state and allocates no memory. Its constants influence hardware state indirectly through MMIO writes performed by display code.

Hardware state affected by consumers includes:

- VPG generic-packet RAM access, packet-data bytes, frame-update and immediate-update request bits, pending bits, lock/conflict status, and VPG memory power mode.
- AFMT audio and infoframe state, including audio layout/channel enable, channel-status bytes, CRC test configuration/results, ramp generation, audio clock selection, audio source select, and memory power.
- DME metadata generation state, including enable, stream type, HUBP requestor selection, and memory power.
- DIG HDMI/TMDS state, including HDMI enable/status, deep color, scrambling, general control packets, null/ACP/ISRC packets, audio ACR values, metadata packets, generic packet scheduling, TMDS control characters, sync patterns, DC balancing, and FIFO diagnostics.
- DP link/stream state, including stream enable/status, pixel format, MSA fields, link framing, DPHY training/scrambling/CRC/test pattern state, secondary-packet transmission, MST/MSE allocation fields, DSC bytes-per-pixel and mode, ALPM PHY sleep/standby request bits, and GSP enable double-buffer status.

These register values persist in the display hardware until the driver rewrites them, the block is reset, or the GPU enters a power/reset transition that loses the register state.

## Dependencies

This chunk depends on the companion DCN 3.0.2 offset header for register addresses. A shift/mask pair is only useful when combined with the corresponding `mm<REGISTER>` address and base-index macros from `dcn_3_0_2_offset.h`.

It also depends on the AMD display register-helper abstraction:

- `reg_helper.h` supplies the macro machinery that turns a logical register field into a masked/shifted MMIO operation.
- DCN/DCE stream-encoder headers define the field-list macros that select which generated fields are present in a given hardware generation's register tables.
- DCN302 resource construction determines which engine IDs map to these instance-specific definitions. In this driver, DCN302 advertises five stream encoders and creates VPG/AFMT instances for engines through `ENGINE_ID_DIGE`; this chunk's DIG2 and DIG3 definitions are two entries in that per-instance set.

The hardware protocol dependencies are HDMI, DisplayPort, audio infoframe/channel-status, DisplayPort secondary-data-packet handling, Display Stream Compression, MST/MSE slot allocation, metadata transmission, and panel/link low-power signaling.

## Integration Points

The main integration point is `dcn302_resource.c`, which includes this header and builds the DCN302 hardware tables. The `stream_enc_regs`, `se_shift`, and `se_mask` tables are passed into `dcn30_dio_stream_encoder_construct()`, while `vpg_shift`/`vpg_mask` and `afmt_shift`/`afmt_mask` are passed to `vpg3_construct()` and `afmt3_construct()`.

The most visible downstream integration is `dcn30_dio_stream_encoder.c`. Its HDMI info-packet code calls the VPG packet-data updater, then sets the HDMI generic-packet control fields defined here. Its DP paths program `DP_SEC_*`, `DP_MSA_*`, `DP_DSC_*`, `DP_MSE_*`, and metadata fields through the same tables. Audio paths use AFMT and HDMI ACR fields. Link and stream setup paths use `DIG_FE_CNTL`, `DIG_BE_CNTL`, `DP_VID_STREAM_CNTL`, `DP_PIXEL_FORMAT`, and FIFO/status fields.

Because this is an instance-specific generated header, integrations rely on naming regularity. `DIG2_*` and `DIG3_*` fields must match the generic `DIG0_*` field-list names after macro substitution, and field names must remain identical across instances where the shared stream-encoder code expects them.

## Risks

The highest risk is silent hardware misprogramming from a wrong mask or shift. A compile succeeds as long as the symbol exists, but an incorrect bit layout can break output without an obvious software error. Examples include:

- HDMI or DP info packets not being sent, sent continuously when they should not be, or sent on the wrong line.
- Audio failures from wrong AFMT channel, layout, ACR, or IEC 60958 channel-status fields.
- DP stream bring-up failures from wrong `DP_VID_STREAM_ENABLE`, `DP_VID_STREAM_STATUS`, M/N, MSA, DPHY, or link-framing fields.
- MST/MSE allocation errors from wrong slot-count, SAT update, or per-slot fields.
- DSC or PPS transport failures from wrong `DP_DSC_*` or GSP11/PPS-related fields.
- Metadata and HDR packet loss from wrong DME, HDMI metadata, or DP secondary metadata fields.
- Power-management issues if light-sleep or memory-power fields are mis-specified for VPG/AFMT/DME.

Boundary risk is present in this research chunk because it starts mid-register at the remaining `VPG2_VPG_GSP_FRAME_UPDATE_CTRL` mask definitions and ends mid-register in `DIG3_HDMI_GENERIC_PACKET_CONTROL5`. The final per-file reconciliation should merge adjacent chunks so that those split register definitions are described as complete blocks.

## Test Signals

Useful test signals are mostly integration and hardware-observation signals rather than unit tests for this generated header:

- A successful AMDGPU/DC build for DCN302 confirms all expected shift/mask symbols still exist and macro-list expansions compile.
- Booting on DCN 3.0.2 hardware with HDMI and DP displays confirms basic stream encoder, link, and packet register programming.
- HDMI validation should check AVI/vendor/SPD/HDR/VTEM infoframes, deep color, scrambling, audio packets, ACR/N/CTS values, and generic-packet scheduling.
- DP validation should check stream enable/status, MSA timing, audio SDP, VSC/SPD/HDR secondary packets, MST/MSE allocation where applicable, DSC/PPS transmission, and metadata packets.
- Register readback through debugfs or driver tracing should show field values landing in the expected bits for `DIG2_*`, `DP2_*`, and `DIG3_*` registers after `REG_UPDATE` and `REG_SET_*` calls.
- Negative signals include black screens after link training, FIFO level errors, missing HDR metadata, HDMI audio loss, DP audio loss, DSC negotiation failures, MST stream allocation failures, or repeated pending bits in generic-packet/frame-update registers.
