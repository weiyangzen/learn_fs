# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 37462-39888

## Scope And Purpose

This chunk is part of the generated AMDGPU DCN 4.1.0 register shift/mask header. It contains no executable C logic; it publishes compile-time bit positions and already-shifted masks for DCN display I/O registers. Consumer code pairs these `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros with register offsets from `dcn_4_1_0_offset.h` and uses the AMD display register helpers for MMIO read, write, read-modify-write, polling, and field extraction.

The assigned range starts in the tail of the `DIG3` TMDS control block, covers AFMT audio formatter masks for `AFMT0` through `AFMT3`, DME and VPG metadata/generic-packet blocks for `DIG0` through `DIG3`, the DIO I2C/DDC control surface, DIO misc power/clock/status controls, stream-to-link mapper fields for `DIG0` through `DIG6`, and the beginning of DCIO/UNIPHY A PHY routing fields.

The practical role of the chunk is to describe the bit layout used by DCN 4.1 stream encoders, audio packet generation, dynamic metadata injection, DDC/EDID I2C transactions, display I/O memory power management, stream mapper programming, and early PHY lane crossbar setup.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or variables in this chunk. The generated preprocessor macro namespace is the API surface:

- `DIG3_TMDS_CTL2_3_GEN_CNTL` and `DIG3_DIG_VERSION`: TMDS control-lane data select, delay, invert, modulation, feedback path, feedback sync, pattern output, and DIG type fields for the fourth DIG encoder instance. The first visible line also finishes a `DIG3_TMDS_CTL0_1_GEN_CNTL` mask from the previous chunk.
- `AFMT0_AFMT_*` through `AFMT3_AFMT_*`: repeated audio formatter blocks per stream/audio endpoint. They define ACP packet fields, VBI packet selection, audio layout/channel/stream-id control, HDMI/DP audio infoframe fields, IEC 60958 channel status fields, audio CRC controls/results, audio test ramp counters, status/overflow/change indicators, sample-send and acknowledgement bits, audio infoframe update/source fields, audio source select, DTO debug source/select fields, and AFMT memory-power force/disable/state fields.
- `DME0_DME_CONTROL` through `DME3_DME_MEMORY_CONTROL`: dynamic metadata engine control for hubp requestor id, engine enable, stream type, double-buffer pending/taken/clear/disable state, transmission missed status/clear, and memory power force/disable/state/default low-power fields.
- `VPG0_VPG_*` through `VPG3_VPG_*`: video packet generator fields for generic-packet indexed byte access, generic packet frame-update and immediate-update bits plus pending status for packet slots 0-14, generic conflict/lock status and clear, VPG memory power, ISRC data access, and MPEG infoframe bytes/update.
- `DC_I2C_*`: DDC/I2C controller fields for start/go/reset, DDC select, transaction count, arbitration between software/hardware/DMCU users, interrupt status/ack/mask for software and DDC1-DDC6/DDCVGA hardware operations, software and hardware status, per-DDC speed/setup/timing/enable/EDID-detect fields, four transaction descriptors, indexed data FIFO access, EDID-detect policy, and read-request interrupt status/ack/masks.
- `DIO_*`: global display I/O misc fields including DCN enabled status, scratch registers, DP ALPM wake interrupt status/clear/ack/mask, I2C and DPA-DPG memory-power state and light-sleep force/disable controls, DIO clock gate disables, power-management reset/busy flags, stereosync selection, I2S/SPDIF soft reset, HDMI RX status timer control, PSP interrupt status/message/clear, and DIO enable status.
- `DIG0_STREAM_MAPPER_CONTROL` through `DIG6_STREAM_MAPPER_CONTROL`: `DIG_STREAM_LINK_TARGET` fields used to map stream encoder instances to link encoder targets.
- `DC_GENERICA`, `DC_GENERICB`, `DCIO_CLOCK_CNTL`, `DC_REF_CLK_CNTL`, `UNIPHYA_LINK_CNTL`, and the start of `UNIPHYA_CHANNEL_XBAR_CNTL`: generic DC signal enable/select, DCIO clock test/gating, genlock reference clock output selection, UNIPHY A lane inversion, and PHY channel crossbar/source/enable fields. The `UNIPHYA_CHANNEL_XBAR_CNTL` block continues beyond this chunk boundary.

## Control Flow

This header chunk has no local runtime control flow. Runtime sequencing comes from display-core code that includes the generated DCN 4.1.0 offset and mask headers:

1. A DCN 4.1 component selects a register offset through generated register-list macros such as `SRI()`/`SR()` and a field through `SE_SF()`, `I2C_SF()`, or link-encoder field-list macros.
2. The register helper layer uses the shift/mask constants to insert a field value, extract status, acknowledge an interrupt, or poll for a power/status transition.
3. Hardware performs the state transition: sending audio or metadata packets, completing I2C transactions, entering/exiting light sleep, mapping a stream to a link, or routing PHY lanes.

Control-sensitive hardware flows implied by this chunk include AFMT audio packet updates via `AFMT_AUDIO_INFO_UPDATE` and `AFMT_60958_CS_UPDATE`, VPG generic packet update/pending handshakes, DME metadata double-buffer taken/clear and missed/clear bits, I2C arbitration request/done and transaction status, memory light-sleep force/status polling, DP ALPM wake ack/mask handling, PSP interrupt clear, and stream mapper programming before link enable.

## State And Persistence Behavior

The macros themselves are compile-time constants and persist no software state. They describe hardware-visible state in DCN 4.1.0 display I/O registers:

- AFMT state persists while the stream/audio block is powered: channel enables, layout override, DP audio stream id, IEC 60958 channel status, audio infoframe payload fields, source select, sample-send enable, test/ramp settings, CRC source/count, and AFMT memory-power controls.
- DME and VPG state holds dynamic metadata and generic packet programming across modeset phases until software updates it, clears double-buffer/status bits, disables the engine, or powers/gates the block.
- I2C/DDC state is transactional and shared. Arbitration fields grant ownership to software, hardware, or DMCU; transaction descriptors and data FIFO fields define the active transfer; status/interrupt bits report completion, abort, timeout, NACK, overflow, EDID-detect state, and read-request events.
- DIO power and clock state persists until reset or explicit reprogramming. `DIO_MEM_PWR_CTRL`, `DIO_MEM_PWR_CTRL2`, and `DIO_MEM_PWR_STATUS` coordinate light-sleep for I2C and DPA-DPG blocks; `DIO_CLK_CNTL` gates display, reference, SoC, symbol, DP reference, and HDCP-related clocks.
- Stream mapper and UNIPHY routing state determines which link target a stream encoder drives and how physical lanes are inverted or crossbar-routed. Incorrect or stale values can survive until the relevant DIO/DCIO block is reset or reinitialized.
- Interrupt/status fields are likely latched or write-to-ack/clear depending on the named field. The header exposes names such as `*_ACK`, `*_CLR`, `*_MASK`, and `*_STATUS`, but it does not encode access type or ordering.

## Dependencies And Integration Points

This chunk depends on the generated DCN 4.1.0 register-map family:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h` supplies matching register addresses.
- AMD display register helpers interpret the `__SHIFT`/`_MASK` pairs through token-pasting macros and register field tables.
- DCN 4.1 display code includes this header through resource, stream-encoder, DMUB, GPIO/I2C, link-encoder, and interrupt support for this ASIC generation.

Observed local integration patterns include:

- `display/dc/dio/dcn401/dcn401_dio_stream_encoder.h` maps `DIG0_STREAM_MAPPER_CONTROL.DIG_STREAM_LINK_TARGET` and DME fields through `SE_SF(...)` for DCN 4.1 stream encoders.
- AFMT code in nearby generations, such as `display/dc/dcn31/dcn31_afmt.h`, consumes the same `AFMT0_AFMT_*` field names for audio info update, audio source select, channel enable, 60958 channel status, sample send, and AFMT memory power.
- `display/dc/dce/dce_i2c_hw.c` and `display/dc/dce/dce_i2c_hw.h` use `DIO_MEM_PWR_CTRL.I2C_LIGHT_SLEEP_FORCE`, `DIO_MEM_PWR_STATUS.I2C_MEM_PWR_STATE`, and DDC setup/control/arbitration fields while acquiring the I2C engine, programming DDC speed/transactions, and returning the block to low power.
- Link-encoder macros in adjacent DCN generations use `UNIPHYA_CHANNEL_XBAR_CNTL` fields for lane crossbar routing; this chunk provides the DCN 4.1.0 A-PHY field layout at the start of that family.

Despite the repository path being under a `ceph-client` mirror, this source is AMDGPU display hardware metadata. It has no Ceph filesystem protocol behavior, distributed filesystem control flow, or persistent filesystem state.

## Risks And Edge Cases

- Generated mask/shift drift is high impact. A wrong field position can compile cleanly while programming the wrong MMIO bits for audio packets, DDC transfers, metadata, power state, stream mapping, or PHY routing.
- Repeated AFMT, DME, and VPG instance namespaces are easy to mix. Code must pair the correct register offset instance with matching field masks; copying `AFMT0`/`VPG0` field assumptions into a different instance without the register table abstraction can target the wrong stream.
- Several fields are status/ack/clear pairs. Misusing `*_ACK` or `*_CLR` fields as ordinary status bits, or failing to clear latch bits such as metadata missed/taken or I2C interrupts, can leave stale diagnostics or repeated interrupts.
- I2C arbitration is shared with hardware and DMCU users. Incorrect `SW_USE`, `SW_DONE`, abort, transaction-count, or DDC-select masks can break EDID reads, HDCP polling, AUX/DDC coexistence, or firmware-mediated transfers.
- Power-management fields require ordering and polling that the header cannot express. For example, forcing I2C light sleep should be paired with `I2C_MEM_PWR_STATE` checks in consumer code; disabling or forcing DPA-DPG light sleep at the wrong time can affect link bring-up and hotplug behavior.
- Stream mapper and UNIPHY crossbar fields are small multi-bit selectors. Out-of-range values or mismatched stream/link ids may route an active stream to the wrong link encoder or lane set, causing blank display or link-training failures.
- Clock-gating disables in `DIO_CLK_CNTL` are global to DIO paths. Accidentally setting gate-disable bits for display, reference, symbol, DP reference, or HDCP clocks can hide timing bugs or increase power; clearing required disables too early can gate a clock during register access.
- The chunk starts and ends mid-family. The first line belongs to a `DIG3_TMDS_CTL0_1_GEN_CNTL` block begun in the previous chunk, and the final visible `UNIPHYA_CHANNEL_XBAR_CNTL` block continues into the next chunk. Per-file conclusions must reconcile adjacent chunks.

## Test Signals

Useful validation signals for this chunk include:

- Kernel build coverage for DCN 4.1.0 display paths that include `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h`; token-pasting failures should catch missing or renamed macros.
- Generated-header consistency checks that every field has aligned `__SHIFT` and `_MASK` values, masks match expected widths, and repeated AFMT/DME/VPG/DDC instance blocks remain structurally consistent.
- Audio over HDMI and DP tests that exercise AFMT source select, channel enable, IEC 60958 status, audio infoframe updates, sample-send enable, FIFO overflow/change acknowledgement, and AFMT memory power transitions.
- Dynamic metadata and generic-packet tests for DME/VPG paths, including frame-update versus immediate-update programming, pending bits, conflict status/clear, ISRC/MPEG packet payloads, and missed-transmission clear behavior.
- DDC/EDID and HDCP-polling tests across DDC1-DDC6 and DDCVGA, including software arbitration, transaction chaining, NACK/timeout/abort paths, read-request interrupt ack/mask handling, and low-power entry/exit around I2C use.
- Power-management, hotplug, suspend/resume, and display modeset tests that observe DIO memory-power status, DP ALPM wake interrupts, PSP interrupt clear behavior, DIO clock gates, and stream mapper reprogramming.
- Link-training and multi-display tests that verify `DIG_STREAM_LINK_TARGET` selection and UNIPHY A lane inversion/crossbar programming across all valid stream and link encoder combinations.

## Chunk Boundary Notes

Line 37462 starts after the beginning of `DIG3_TMDS_CTL0_1_GEN_CNTL`; this report treats that as previous-chunk context and focuses on the fully visible `DIG3_TMDS_CTL2_3_GEN_CNTL` and following groups. Line 39888 ends inside `UNIPHYA_CHANNEL_XBAR_CNTL`, before the rest of the UNIPHY A and later PHY instances. The final per-file research document should merge this report with the adjacent chunk reports before making whole-header conclusions.
