# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 37793-40200

## Purpose

This chunk is a generated DCN 4.2.0 shift/mask register contract for AMD display I/O. It contains 2,170 `#define` constants and no executable C. Each register field is represented as a `__SHIFT` macro and a `_MASK` macro; consumers combine these with register offsets from `dcn_4_2_0_offset.h` through AMDGPU display helper macros such as `SE_SF`, `LE_SF`, `HWS_SF`, `REG_UPDATE`, `REG_SET`, and field encode/decode helpers.

The line range spans the end of the DC I2C/DDC controller fields, the DIO miscellaneous block, DIG stream mapping, a DC perfmon instance, the first VPG/APG/DME blocks, the first DIG front-end/back-end/HDMI/TMDS block, and the first DP link block through the beginning of AUX-less ALPM control. It is therefore a hardware ABI description for connector sideband access, display stream encoding, audio packet generation, metadata sideband packets, DP main-link timing/training/MST, low-power modes, and packet double-buffering.

## Important APIs, Types, And Macros

This header does not define functions, structs, enums, or static data. The API is the preprocessor namespace used to populate per-IP register field tables.

- `DC_I2C_DDC2_SPEED` through `DC_I2C_DDC5_SETUP` describe hardware DDC timing and line-drive configuration: threshold, filter stall behavior, start/stop timing, prescale, data/clock drive enable, reset length, EDID detection, intra-byte delay, inter-transaction delay, and time limit. The chunk also carries the tail of `DC_I2C_DDC1_SETUP`.
- `DC_I2C_TRANSACTION0..3`, `DC_I2C_DATA`, `DC_I2C_EDID_DETECT_CTRL`, and `DC_I2C_READ_REQUEST_INTERRUPT` define the transaction descriptor, byte/index access, EDID-detect policy, and read-request IRQ/ack/mask fields for DDC1-DDC6 plus VGA DDC.
- `DIO_SCRATCH0..7`, `DIO_DP_ALPM_WAKEUP_INTERRUPT_STATUS`, `DIO_MEM_PWR_STATUS`, `DIO_MEM_PWR_CTRL`, `DIO_MEM_PWR_CTRL2`, `DIO_CLK_CNTL`, `DIO_POWER_MANAGEMENT_CNTL`, `DIO_HDMI_RXSTATUS_TIMER_CONTROL`, `DIO_PSP_INTERRUPT_STATUS`, `DIO_PSP_INTERRUPT_CLEAR`, and `DIO_STATUS` expose DIO scratch storage, per-DIG ALPM wake status, I2C/DP memory light-sleep state and controls, display/reference/symbol/SOC clock gating, reset/busy signaling, HDMI RX-status timer fields, PSP interrupt state, and DIO enable status.
- `DIG0_STREAM_MAPPER_CONTROL` through `DIG4_STREAM_MAPPER_CONTROL` map DIG stream encoders to link targets. DCN42 stream encoder code consumes `DIG0_STREAM_MAPPER_CONTROL__DIG_STREAM_LINK_TARGET`.
- `DC_PERFMON16_*` defines a display perf counter instance: counter control/select/clear/status, increment/decrement/range events, perfmon enable/clear/overflow/status, current value interrupt behavior, and 64-bit counter high/low value registers.
- `VPG0_*` covers generic packet access/data, frame-update and immediate-update controls for generic stream packets 0-11, VPG status/conflict clear, VPG memory power fields, and ISRC packet data access. These fields back HDMI/DP generic packet and infoframe update paths.
- `APG0_*` describes audio packet generator control, debug packet sources, ACP and audio-info payload fields, IEC 60958 channel-status bits, audio CRC control/result, debug ramp generation, audio/HBR/FIFO status, debug audio DTO, APG memory power, and spare register access.
- `DME0_DME_CONTROL` and `DME0_DME_MEMORY_CONTROL` define display metadata engine routing and update handshakes: HUBP requestor ID, engine enable, stream type, double-buffer pending/taken/clear/disable, missed transmission status, and DME memory low-power control.
- `DIG0_*` front-end, back-end, HDMI, and TMDS fields cover source selection, stereo sync, FE/BE clocks and resets, FIFO calibration/error state, HDMI metadata packets, scrambling, clock-channel rate, Dolby Vision enable/missed status, pixel encoding/color format, deep color, HDMI audio/ACR/VBI/infoframe/generic packet controls, HDMI double-buffering, ACR values/status, audio muxing, BE source/HPD selection, TMDS control symbols, DC balancing, pattern generation, and DIG version.
- `DP0_*` fields cover DP link status, pixel format, MSA colorimetry/misc/timing/VBID, lane count, video stream enable/defer/status, steer FIFO, video M/N generation, link framing, HBR2/DPHY test/training patterns, FEC, PRBS, scrambler, CRC, transfer unit control, secondary-data packet control, audio timestamps/N/M values, MST/MSE rates and slot-allocation tables, MSO secondary packet enables, metadata transmission, double-buffer status, ALPM, GSP8-GSP11 controls, and generic stream packet enable double-buffer pending status.

## Control Flow

There is no runtime control flow in this file. The effective control flow is compile-time table construction followed by runtime register helper use:

1. DCN42 resource code includes this generated field header and the matching offset header.
2. Resource constructors populate register address tables and field shift/mask tables. In this tree, `dcn42_resource.c` uses `HWSEQ_DCN42_MASK_SH_LIST`, while `dcn42_dio_stream_encoder.h` and `dcn42_dio_link_encoder.h` use `SE_COMMON_MASK_SH_LIST_DCN42` and `LINK_ENCODER_MASK_SH_LIST_DCN42`.
3. Runtime DIO, stream encoder, link encoder, I2C, HW sequencer, audio, and DP helpers call generic macros such as `REG_UPDATE`, `REG_UPDATE_N`, `REG_SET`, `REG_GET`, and packet programming helpers.
4. Those helpers use the precomputed shift/mask values from this chunk to isolate fields inside MMIO register words.

The main programmed sequences represented by the fields are:

- DDC/I2C setup: enable the selected DDC engine, program bus timing/prescale/delays, describe up to four transaction segments, write/read byte data through indexed data fields, and service read-request interrupt/ack bits.
- DIO power/clock sequencing: force or release I2C/DP memory light sleep, query memory power state, gate or ungate DIO clocks, and control DIO reset/busy state.
- Stream/link binding: map each DIG stream to a link target, enable FE/BE clocks and resets, route source streams, select HPD/link backends, and enable the FE/BE datapath.
- HDMI/packet programming: enable HDMI attributes, program scrambling/deep color/clock-channel rate, schedule audio/ACR/VBI/infoframe/generic/metadata packets by line, and commit double-buffered packet updates.
- DP programming: set pixel format, MSA timing and colorimetry, M/N timing, main-link framing, DPHY training/FEC/scrambler/test/CRC controls, video stream enable/defer, secondary-data packet enables, MST slot allocation, MSO packet replication, and ALPM sleep/standby requests.

## State And Persistence

The header is stateless, but its fields describe persistent hardware state in powered DCN blocks.

- DDC/I2C state persists in controller configuration registers until changed, reset, or power-gated. It affects monitor EDID reads, AUX/DDC GPIO behavior, and read-request interrupt handling.
- DIO memory and clock bits control low-power entry for I2C, DP, VPG/APG/DME, and symbol-clock related logic. Incorrect values can leave blocks powered when they should sleep or sleeping when software expects them available.
- Stream encoder and link encoder state persists across active modes: FE/BE source routing, FIFO calibration, HDMI format attributes, TMDS control generation, DP MSA timing, secondary-data packets, MST slot allocation, and ALPM state are all mode-set or link-training sensitive.
- Packet and metadata registers often use double-buffer handshakes (`*_DB_PENDING`, `*_DB_TAKEN`, `*_DB_TAKEN_CLR`, `*_DB_DISABLE`, and update-lock fields). Software must respect pending/taken state so new packets land on the intended frame or vupdate.
- Status and clear fields are mixed with control fields. Examples include FIFO errors, HDMI audio/error interrupts, packet missed indicators, APG CRC done clear, DME missed transmission clear, DIO PSP interrupt clear, and DP GSP deadline-missed/pending/active flags.

There is no filesystem persistence. State is in MMIO-visible display hardware and is reset by GPU reset, display engine reset, suspend/resume power transitions, or explicit driver reprogramming.

## Dependencies And Integration Points

- `dcn_4_2_0_offset.h` provides the register address side for the field names in this chunk. The shift/mask macros are only useful when paired with the corresponding `reg*` offset and `_BASE_IDX`.
- `display/dc/resource/dcn42/dcn42_resource.c` populates DCN42 HW sequencer fields including `DIO_MEM_PWR_CTRL__I2C_LIGHT_SLEEP_FORCE`, connecting this chunk to display power sequencing and I2C light-sleep control.
- `display/dc/dio/dcn42/dcn42_dio_stream_encoder.h` consumes many fields from this range through `SE_COMMON_MASK_SH_LIST_DCN42`: DP pixel format, HDMI control/audio/ACR/generic packets, DP secondary packets, DP MSA timing, DME metadata, HDMI/DP metadata packets, DIG FE/FIFO/stream mapper, and audio mux fields.
- `display/dc/dio/dcn42/dcn42_dio_link_encoder.h` consumes link-side fields through `LINK_ENCODER_MASK_SH_LIST_DCN42`: DIG BE enable/source/HPD selection, DPHY training/test/FEC/PRBS/scrambler controls, link framing, DP lane configuration, MST slot allocation, AUX/HPD fields from adjacent chunks, and DIO clock gating fields from this chunk.
- Generic stream encoder implementations in `display/dc/dce/dce_stream_encoder.c` and DCN stream/link encoder code use the field tables to program HDMI generic packets, infoframes, audio/ACR, DP secondary packets, and metadata.
- Generic I2C hardware code in `display/dc/dce/dce_i2c_hw.c` uses the DIO memory power field to force/release I2C light sleep around hardware I2C operations; the rest of the DDC field family is the register contract for DDC setup and transaction programming.
- DP MST/MSO, HDR/Dolby Vision metadata, audio packet generation, DSC/PPS-related GSP11 usage, and ALPM are all represented here as field contracts but orchestrated by higher-level DC mode-set, link-training, audio, and power-management paths.

## Risks

- This is generated hardware ABI data. A wrong bit position or mask can silently corrupt unrelated fields in the same register even when the C code compiles and the register offset is correct.
- Repeated instances hide copy/paste drift. DDC2-DDC5, transaction0-3, DIG0-DIG4 stream mappers, GSP fields, MST slot fields, and generic packet fields are highly regular; one bad field affects only a particular connector, packet slot, stream, or MST source.
- Some field names differ across DCN generations. DCN42 stream/link headers deliberately choose DCN42 names such as `PIXEL_ENCODING_TYPE`, `UNCOMPRESSED_PIXEL_FORMAT`, and the DCN42 `DIO_CLK_CNTL` clock-gating fields. Reusing older DCN masks would misprogram the same logical feature.
- Packet double-buffer fields are timing-sensitive. Misplaced pending/taken/clear/disable masks can cause HDMI/DP infoframes, metadata, DSC PPS, or generic secondary packets to update late, update on the wrong frame, or miss their deadline.
- Link-training and PHY fields are high impact. Errors in DPHY training pattern, FEC, scrambler, PRBS, symbol, CRC, lane count, or link framing fields can cause blank displays, link training failures, intermittent CRC errors, or DP compliance failures.
- Power and clock fields can produce non-obvious failures. Bad `DIO_MEM_PWR_CTRL`, `DIO_MEM_PWR_CTRL2`, `DIO_CLK_CNTL`, VPG/APG/DME memory-power, or ALPM masks can surface as resume failures, I2C timeouts, audio loss, packet drops, or wakeup interrupt issues.
- Status/clear bit confusion can lose diagnostics. Interrupt ack/clear and missed/deadline/status bits share registers with enables in several blocks; a wrong clear mask may hide a real fault or clear a status before software observes it.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage with DCN 4.2 enabled. Macro renames or missing fields should fail in `dcn42_resource.c`, `dcn42_dio_stream_encoder.h`, `dcn42_dio_link_encoder.h`, and shared DCE/DCN encoder code.
- DDC/EDID tests on every connector: hardware I2C transaction success, EDID detect timing, DDC read-request interrupt ack/mask behavior, and suspend/resume recovery after I2C light sleep.
- DIO power and clock tests: runtime power management, display hotplug after idle, PSP/DIO interrupt status handling, ALPM wakeup status, and clock-gating toggles for DIG/HDCP/symbol-clock paths.
- HDMI validation: deep color, scrambling and clock-channel-rate modes, AVMUTE, audio packets, ACR CTS/N values for 32/44.1/48 kHz families, infoframes, generic packets 0-14, metadata packets, Dolby Vision enable/missed status, and double-buffer update behavior.
- DP SST validation: link training, lane-count programming, FEC, enhanced framing, video M/N timing, MSA timing/colorimetry, VBID behavior, DPHY scrambler/CRC/test pattern controls, video stream enable/defer, and stream disable interrupts.
- DP MST/MSO validation: MSE rate programming, slot allocation table programming/status for sources 0-5, SAT update handshakes, MSO secondary packet enable masks, and secondary packet replication across GSP slots.
- Audio and packet generator validation: APG enable/reset, HBR/audio status, FIFO overflow clear, IEC 60958 channel-status fields, audio CRC done/clear/result, VPG generic packet conflict status, ISRC access/data, and metadata engine double-buffer/missed-transmission handling.
- Low-power and ALPM tests: DP ML PHY sleep/standby requests and pending bits, AUX-less ALPM sleep repeat/delay/interval fields, force-scrambled-zero behavior, and link-training transitions around ALPM.
