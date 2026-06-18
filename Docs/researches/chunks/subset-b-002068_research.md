# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 26562-28781

## Scope

This chunk is a generated DCN 3.5 register bitfield header slice. It contains only preprocessor constants: `*_SHIFT` values and matching `*_MASK` values for fields in VPG, AFMT, DME, DIG/HDMI/TMDS, and DP register blocks. There are no functions, structs, enums, branches, or local storage in this range; its behavior is entirely through compile-time expansion into AMD display register accessor tables.

The range starts in the middle of the `VPG0` ISRC/MPEG payload field definitions, covers complete `AFMT0` and later `AFMT1` audio formatter field sets, `DME0` and `DME1` metadata engine fields, large `DIG0` and `DIG1` stream encoder/HDMI/TMDS field sets, a substantial `DP0` DisplayPort field set, and the beginning-to-middle of `VPG1` video packet generator fields.

## Purpose

The constants define the exact bit positions and masks used by the AMDGPU display core to read and write DCN 3.5 hardware registers. The source file mirrors the hardware register database: each macro name encodes the instance, register, field, and whether the value is a shift or mask.

Examples of covered register families:

- `VPG0_*` and `VPG1_*`: generic packet data, frame/immediate update controls, status/conflict bits, ISRC and MPEG info payload bytes, and VPG memory power state.
- `AFMT0_*` and `AFMT1_*`: HDMI/DP audio formatter programming, audio infoframes, IEC 60958 channel status, audio CRC/test ramp registers, FIFO/status bits, source selection, and AFMT memory power.
- `DME0_*` and `DME1_*`: metadata engine enablement, HUBP requestor selection, stream type, double-buffer state, missed-transmission flags, and memory power control.
- `DIG0_*` and `DIG1_*`: front-end source selection, output CRC, test patterns, FIFO controls, HDMI control/status, HDMI generic packet scheduling, audio clock recovery, global control/AVMUTE, TMDS control characters, back-end clock/reset/source selection, and AFMT clock gating.
- `DP0_*`: DisplayPort stream/link control, MSA and VBID fields, DPHY training/scrambler/FEC/CRC fields, secondary data packet controls, MST/MSE slot allocation, generic secondary packet controls 8-11, metadata transmission, ALPM/AUX-less ALPM, DSC, MSO, and double-buffer status.

## Important APIs, Types, And Macros

This chunk does not declare public C APIs, but it feeds several AMD display macro APIs:

- `SE_SF(register, field, mask_sh)` consumes names such as `DP0_DP_SEC_CNTL` and `DP_SEC_STREAM_ENABLE` to initialize stream encoder mask/shift tables.
- `SRI_ARR(register, block, id)` consumes register names to map indexed hardware instances, for example `SRI_ARR(HDMI_GENERIC_PACKET_CONTROL0, DIG, id)` in the DCN35 resource register lists.
- `REG_UPDATE`, `REG_UPDATE_N`, `REG_SET_N`, and `REG_GET` later use those tables to perform masked read-modify-write and field extraction operations.

Important field groups in this range include:

- AFMT audio send/control fields: `AFMT_AUDIO_SAMPLE_SEND`, `AFMT_AUDIO_CHANNEL_ENABLE`, `AFMT_60958_CS_UPDATE`, `AFMT_AUDIO_LAYOUT_OVRD`, `AFMT_60958_OSF_OVRD`, `AFMT_MEM_PWR_FORCE`, `AFMT_MEM_PWR_DIS`, and `AFMT_MEM_PWR_STATE`.
- VPG generic packet fields: `VPG_GENERIC_DATA_INDEX`, `VPG_GENERIC_DATA_BYTE0..3`, `VPG_GENERIC0..14_FRAME_UPDATE`, `VPG_GENERIC0..14_IMMEDIATE_UPDATE`, pending bits, conflict status/clear fields, and VPG memory power fields.
- HDMI packet fields: `HDMI_GENERIC0..14_SEND`, `HDMI_GENERIC0..14_CONT`, line-reference and line-number fields, immediate-send/pending bits, generic-packet enable double-buffer pending bits, `HDMI_DB_*`, `HDMI_ACR_*`, `HDMI_GC_AVMUTE`, and HDMI status/error fields.
- DP secondary data fields: `DP_SEC_STREAM_ENABLE`, audio packet controls (`DP_SEC_ASP_ENABLE`, `DP_SEC_ATP_ENABLE`, `DP_SEC_AIP_ENABLE`, `DP_SEC_ACM_ENABLE`), generic secondary packet enables, send/pending/deadline bits, packet framing and metadata controls, and `DP_SEC_GSP8..11_*`.
- DP link/PHY fields: stream enable/status/deferred disable, pixel format, `DP_VID_M/N`, link framing, FEC and scrambler controls, training pattern, PRBS, DPHY CRC and fast-training fields.
- DP MST/MSO/ALPM fields: MSE rate and slot allocation, MSO controls, `DP_ALPM_CNTL`, `DP_AUXLESS_ALPM_CNTL1..5`, wakeup/interrupt fields, and GSP enable double-buffer status.

## Control Flow

There is no runtime control flow in this chunk. The practical flow is compile-time and data-driven:

1. Generated macro names provide register field positions and masks.
2. DCN35 resource headers build per-instance register address lists for VPG, AFMT, stream encoder/DIG, and DP blocks.
3. Encoder, VPG, and AFMT headers build mask/shift field tables with `SE_SF`.
4. Runtime display code calls `REG_UPDATE`, `REG_SET`, or `REG_GET`; those helpers combine the register address, field mask, and shift to modify or extract a bitfield.

The duplicated `0` and `1` instance blocks in this chunk let the same runtime code operate on selected hardware instances through register-list indirection. The `DP0` field names are commonly used as the base names for mask/shift tables even when register addresses are supplied per DP instance.

## State And Persistence Behavior

The header itself has no mutable state and persists nothing. The macros describe hardware state that lives in display engine registers. Important state represented by the fields includes:

- Double-buffer and update state: `*_DB_PENDING`, `*_DB_TAKEN`, `*_DB_TAKEN_CLR`, `*_DB_LOCK`, `*_DB_DISABLE`, VPG frame/immediate update pending bits, HDMI generic packet enable pending bits, and DP GSP enable pending bits.
- Interrupt/status/ack state: HDMI error status and error ack, AFMT FIFO overflow and audio-enable-change ack, DPHY fast-training complete/ack bits, DP video stream disable interrupt/ack/mask bits, and AUX-less ALPM wakeup interrupt state.
- Power state: `AFMT_MEM_PWR_*`, `DME_MEM_PWR_*`, and `VPG_GSP_MEM_*` fields for memory power forcing, disabling, and state readback.
- Link/stream state: DP link training complete/status, DP video stream enable/status, DPHY FEC active/ready bits, MSE slot state, and ALPM state.

Several fields are hardware-latched or write-one-to-clear style by convention (`*_ACK`, `*_CLR`, `*_PENDING`, `*_TAKEN`). Callers must respect the hardware programming sequence; this header only supplies the bit encoding.

## Dependencies

Direct dependencies are purely preprocessor-level:

- The companion DCN 3.5 offset header supplies the register addresses that correspond to these masks and shifts.
- AMD display resource files include this header and map registers into block-specific register structs.
- Common AMD display register helper macros require each field to have a matching `_SHIFT` and `_MASK`.

Observed integration points in the tree include:

- `display/dc/resource/dcn35/dcn35_resource.h` uses `SRI_ARR` for `VPG_*`, `AFMT_*`, `HDMI_*`, `DP_*`, and `DME` register arrays that correspond to fields in this chunk.
- `display/dc/dcn31/dcn31_afmt.h` maps AFMT fields from `AFMT0_*` into AFMT mask/shift lists used by audio formatter code.
- `display/dc/dcn31/dcn31_vpg.h` maps VPG generic packet update/status fields.
- `display/dc/dio/dcn32/dcn32_dio_stream_encoder.h` and related DIO stream encoder headers map HDMI generic packet, DP secondary data, MSA, MSE, stream-control, and timing fields into stream encoder register tables.
- `display/dmub/src/dmub_dcn35.c` includes the same DCN 3.5 mask header for DMUB register access, though this specific chunk is mostly display stream/packet oriented rather than DMUB control oriented.

## Integration Notes

The naming pattern is the contract. For a field such as `DP0_DP_SEC_CNTL__DP_SEC_STREAM_ENABLE`, the register helper layer expects both:

- `DP0_DP_SEC_CNTL__DP_SEC_STREAM_ENABLE__SHIFT`
- `DP0_DP_SEC_CNTL__DP_SEC_STREAM_ENABLE_MASK`

The mask values are unshifted hardware masks, while the shift values identify the least-significant bit of the field. Runtime helpers use them to clear, shift, and merge values into a 32-bit MMIO register. If either side is missing or mismatched, compilation or field programming fails.

The chunk also shows several extended DCN35-era capabilities: more HDMI generic packet controls up to packet 14, DP secondary packet controls for GSP8-GSP11, DP metadata transmission, ALPM/AUX-less ALPM controls, and DME metadata engine double-buffering.

## Risks

- A wrong mask or shift can silently program an adjacent hardware field, causing display link training failures, missing infoframes, audio dropouts, corrupted metadata packets, or power-state hangs.
- Instance prefix errors are high risk. `AFMT0`/`AFMT1`, `DME0`/`DME1`, and `DIG0`/`DIG1` blocks are structurally similar, so a generated value copied to the wrong instance can compile but target the wrong register encoding.
- Ack/clear fields must be used carefully. Misusing `*_ACK`, `*_CLR`, or `*_TAKEN_CLR` fields can drop hardware events or leave stale pending state.
- Packet timing fields are sensitive to blanking and line-number programming. Incorrect HDMI generic packet or DP secondary packet line/reference fields can cause deadline-missed status, missing HDR/InfoFrame metadata, or invalid audio/ACR behavior.
- Memory power control fields can affect low-power entry and exit for AFMT, VPG, and DME blocks. Incorrect force/disable/state masks can lead to register-access timing issues or blocks not waking as expected.
- Since this is generated hardware data, manual edits are especially risky. Review should compare against the authoritative register database or vendor drop rather than treating values as hand-maintained logic.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware behavior signals:

- Build coverage for DCN35 AMDGPU display code, ensuring all `SE_SF`/`SRI_ARR` references resolve and no mask/shift macro is missing.
- Register-table initialization tests or compile checks for AFMT, VPG, DIO stream encoder, and DCN35 resource headers.
- Display smoke tests on DCN 3.5 hardware for HDMI and DP: link training, mode set, stream enable/disable, suspend/resume, and hotplug.
- HDMI audio tests covering AFMT channel enable, IEC 60958 status updates, ACR programming, audio sample send, and FIFO overflow status.
- InfoFrame and metadata tests for HDMI generic packets 0-14, VPG generic packet updates, DP secondary data packets, HDR metadata transmission, and packet deadline/pending status.
- DP MST/MSO tests covering MSE rate/slot allocation, GSP enable double-buffer status, stream secondary packet scheduling, and DSC/MSO metadata if supported by the target platform.
- Power-management tests for AFMT/VPG/DME memory power fields and DP ALPM/AUX-less ALPM transitions, including wakeup interrupt status/clear behavior.
- CRC/test-pattern diagnostics using DIG output CRC, AFMT audio CRC, DPHY CRC, PRBS, and TMDS/DIG test pattern fields.
