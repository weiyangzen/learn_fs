# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 32633-35011

## Scope And Purpose

This chunk is part of the generated AMD DCN 3.1.5 register shift/mask header. It exports preprocessor constants that describe bit positions and masks for display-controller MMIO registers. The companion `dcn_3_1_5_offset.h` header supplies the register addresses; this file supplies field layout so AMDGPU display helpers can pack writes and decode reads through `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, `FD_MASK`, and `FD_SHIFT`.

The range starts in the middle of the `DP1_DP_SEC_CNTL1` field definitions, covers the remaining DP1 secondary-data, MST/MSE, DPHY, MSA, MSO, DSC, ALPM, and GSP field definitions, then enters `dce_dc_dio_dig1_dispdec` for DIG1 HDMI/TMDS stream-encoder fields. It continues into complete DP2 field groups and the beginning of DIG2 HDMI/TMDS fields, ending at `DIG2_HDMI_GC__HDMI_PACKING_PHASE_MASK`. The final `HDMI_PACKING_PHASE_OVERRIDE_MASK` for `DIG2_HDMI_GC` is outside this chunk.

There are no functions, structs, enums, variables, includes, branches, loops, allocations, locks, or direct side effects here. The exported interface is generated macro metadata:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit for a field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register bit mask.
- `//<REGISTER>` comments delimit logical registers.
- `// addressBlock: ...` comments delimit generated hardware blocks.

Runtime behavior is created by the DCN315 display code that combines these symbols with register offsets and register helper macros. A wrong numeric value can compile but program or read the wrong hardware bits.

## Register Blocks Covered

The first partial section is the tail of `DP1_DP_SEC_CNTL1`. It contains GSP0 send, pending, missed-deadline, any-line, GSP1-7 line-reference, and GSP0 line-number masks. The corresponding shifts and earlier `DP_SEC_CNTL1` fields are in the previous chunk.

The DP1 secondary-data and audio groups include `DP1_DP_SEC_FRAMING1` through `DP1_DP_SEC_FRAMING4`, `DP1_DP_SEC_AUD_N`, `DP1_DP_SEC_AUD_M`, their readback registers, `DP1_DP_SEC_TIMESTAMP`, and `DP1_DP_SEC_PACKET_CNTL`. These fields control secondary-data packet frame/start positions, vblank/hblank/idle transmit widths, SST SDP splitting, collision/audio-mute status, DP audio N/M values, timestamp mode, and ASP coding/priority/version/channel-count override.

The DP1 MST/MSE groups include `DP1_DP_MSE_RATE_CNTL`, `DP1_DP_MSE_RATE_UPDATE`, `DP1_DP_MSE_SAT0` through `SAT2`, `DP1_DP_MSE_SAT_UPDATE`, `DP1_DP_MSE_LINK_TIMING`, `DP1_DP_MSE_MISC_CNTL`, and matching `SAT*_STATUS` registers. They define MSE X/Y rate fields, update-pending state, slot allocation table entries for sources 0-5, encryption flags/types, slot counts, link frame/line timing, timestamp/blank-code controls, and status readbacks.

The DP1 physical/link-diagnostic groups include `DP1_DP_DPHY_BS_SR_SWAP_CNTL` and `DP1_DP_DPHY_HBR2_PATTERN_CONTROL`. These fields expose bitstream/symbol-realignment swap load/count/done state and HBR2 pattern selection.

The DP1 MSA and stream-output groups include `DP1_DP_MSA_TIMING_PARAM1` through `PARAM4`, `DP1_DP_MSO_CNTL`, `DP1_DP_MSO_CNTL1`, `DP1_DP_DSC_CNTL`, `DP1_DP_DB_CNTL`, `DP1_DP_MSA_VBID_MISC`, `DP1_DP_SEC_METADATA_TRANSMISSION`, `DP1_DP_DSC_BYTES_PER_PIXEL`, and `DP1_DP_ALPM_CNTL`. These fields describe DP main-stream timing totals/starts/sync widths/polarities/active size, multi-stream output selection and pixel overlap, DSC mode, double-buffer disable, VBID6 scheduling, metadata packet enable/line scheduling, DSC bytes-per-pixel, and ALPM capability/status/enable.

The extended DP1 generic sideband packet groups include `DP1_DP_SEC_CNTL2` through `CNTL7`, `DP1_DP_GSP8_CNTL` through `GSP11_CNTL`, and `DP1_DP_GSP_EN_DB_STATUS`. They define send, pending, deadline-missed, any-line, line-reference, line-number, and PPS-related fields for GSP4 through GSP11, plus double-buffer status for GSP enable bits.

The `dce_dc_dio_dig1_dispdec` block covers DIG1 stream-encoder fields. It includes front-end control, output CRC control/result, clock/test/random patterns, FIFO status, HDMI metadata/control/status, HDMI audio/ACR/VBI/infoframe/generic-packet controls, HDMI GC, HDMI DB control, ACR N/CTS programming/status for 32/44/48 kHz families, AFMT top control, backend enable/control, TMDS control characters, TMDS feedback/stereo/sync/DC-balance/control-bit generators, DIG version, and force-disable fields.

The `dce_dc_dio_dp2_dispdec` block repeats the DP transmitter layout for DP2. It starts at `DP2_DP_LINK_CNTL` and covers link control, pixel format, MSA colorimetry/config/misc/timing, stream enable/status, steering FIFO, video timing/N/M, link framing, DPHY internal/training/symbol/8b10b/PRBS/scrambler/CRC/fast-training controls, secondary-data/audio metadata controls, MSE/SAT status, MSO, DSC, double buffering, ALPM, GSP8-11, and GSP enable double-buffer status.

The final `dce_dc_dio_dig2_dispdec` block begins DIG2 stream-encoder fields. It covers DIG2 front-end, output CRC, pattern/FIFO, HDMI metadata/control/status, audio/ACR/VBI/infoframe controls, HDMI generic packet send/continuous/line-reference/update-lock fields for packet slots 0-14, immediate-send/pending fields for those slots, and most of `DIG2_HDMI_GC`.

## Important APIs, Types, And Constants

This file does not define callable APIs or C types. Its API is the macro naming contract consumed by generated register-list code.

`display/dc/resource/dcn315/dcn315_resource.c` is the main display consumer for this ASIC family. It includes `dcn/dcn_3_1_5_offset.h` and `dcn/dcn_3_1_5_sh_mask.h`, defines `SR`, `SRI`, `FD_MASK`, and `FD_SHIFT` expansion helpers, and builds static register/field tables. In this chunk, the most relevant tables are `stream_enc_regs[]`, `se_shift`, and `se_mask`, which are passed to `dcn30_dio_stream_encoder_construct()` by `dcn315_stream_encoder_create()`.

The stream-encoder register-list interface is inherited from the DCN314/DCN30 stream encoder family. `display/dc/dio/dcn314/dcn314_dio_stream_encoder.h` maps logical stream-encoder fields to generated macro names such as `DPx_DP_MSA_TIMING_PARAM*`, `DPx_DP_MSE_RATE_CNTL`, `DPx_DP_MSE_RATE_UPDATE`, `DPx_DP_SEC_CNTL*`, `DPx_DP_SEC_METADATA_TRANSMISSION`, `DPx_DP_SEC_FRAMING4`, `DPx_DP_GSP11_CNTL`, `DIGx_HDMI_GC`, `DIGx_HDMI_GENERIC_PACKET_CONTROL*`, `DIGx_HDMI_ACR_*`, and `DMEx_DME_CONTROL`. The generic field table often names instance 0 fields, while instance-specific addresses come from per-instance offset tables.

`display/dc/dio/dcn30/dcn30_dio_stream_encoder.c`, `display/dc/dio/dcn314/dcn314_dio_stream_encoder.c`, `display/dc/dio/dcn20/dcn20_stream_encoder.c`, and older `dcn10_stream_encoder.c` contain the runtime operations that use these field definitions. Examples include programming MSA timing, waiting for `DP_MSE_RATE_UPDATE_PENDING`, configuring DSC PPS sideband packet `GSP11`, reading DP metadata packet scheduling, toggling HDMI AVMUTE through `HDMI_GC_AVMUTE`, controlling generic HDMI packets, and setting `DP_SST_SDP_SPLITTING`.

`display/dmub/src/dmub_dcn315.c` includes the same generated headers and builds `dmub_srv_dcn315_regs` with `REG_OFFSET_EXP()` and `DMUB_DCN315_FIELDS()`. This chunk's DP/DIG fields are not the primary DMUB field list, but they live in the same generated DCN315 namespace and must stay synchronized with the offsets used by DMUB-visible register access.

`display/dc/irq/dcn315/irq_service_dcn315.c` also includes the generated DCN315 headers for interrupt source registration. IRQ tables that touch DIO/DIG/DP state rely on this register field namespace matching the silicon layout.

`display/dc/gpio/dcn315/hw_translate_dcn315.c` and `display/dc/gpio/dcn315/hw_factory_dcn315.c` include these headers for GPIO/DDC/AUX/HPD translation and object construction. They are not the direct consumers of the DP1/DP2/DIG1/DIG2 stream fields in this chunk, but they share the same generated DCN315 register contract.

## Control Flow And Runtime Use

This header has no runtime control flow. Its effective flow is compile-time token expansion:

1. DCN315 display code includes the generated offset and sh/mask headers.
2. Register-list macros paste a register token, field token, and instance token into symbols from this file.
3. Constructors bind generated offsets and field tables into hardware block objects.
4. Runtime stream-encoder, link, audio, metadata, DSC, and diagnostics code uses helper macros to read, write, update, or poll the mapped registers.

For DP MSA programming, runtime code writes fields in `DP_MSA_TIMING_PARAM1` through `PARAM4` to describe totals, starts, sync widths, polarities, and active width/height. For MST/MSE, it writes rate fields and then observes update-pending state. For secondary data, it toggles GSP send/enable/line-number fields and packet scheduling bits. For HDMI, it uses `HDMI_CONTROL`, `HDMI_GC`, VBI/infoframe/generic packet controls, ACR fields, and audio packet fields to send HDMI metadata and audio.

The order in the file mirrors generated hardware organization, not execution order. Ordering-sensitive behavior is defined by the consumers and hardware programming manuals, not by this header.

## State And Persistence Behavior

The header stores no software state and persists no data. It describes bit locations for hardware state held in DP1, DP2, DIG1, and DIG2 registers.

Writable state described here includes DP secondary-data packet scheduling, audio N/M and timestamp mode, MSE rate and SAT slot allocation, MSA timing, MSO routing/overlap, DSC mode and bytes-per-pixel, metadata packet scheduling, ALPM controls, DPHY test/training fields, HDMI packet generation, HDMI AVMUTE/default/packing phase, HDMI ACR N/CTS programming, TMDS control patterns, and DIG frontend/backend enables.

Hardware-updated state described here includes send-pending and deadline-missed flags, collision and audio-mute status, MSE/SAT status readbacks, swap-done flags, stream/FIFO/CRC status, fast-training and DPHY CRC/status fields, ALPM status, GSP enable double-buffer status, HDMI status, ACR status, output CRC results, and DIG version/disable state.

Programmed values persist according to the underlying display power/reset domains. They can survive until rewritten, link or stream reinitialization, display block reset, power-gating, suspend/resume restore, GPU reset, or firmware/hardware sequencing. Status bits can change asynchronously relative to CPU code and may have write-one-to-clear, read-clear, pending, or latch semantics not encoded in this generated header.

## Dependencies And Integration Points

This chunk depends on `dcn_3_1_5_offset.h` for register addresses. Shift/mask values alone are insufficient; consumers need the matching offset header from the same register database. Mixing DCN 3.1.5 shifts with DCN 3.1.4, DCN 3.1.6, or generic DCN31 offsets is risky because many register and field names are structurally similar while positions or availability can differ.

The primary integration point is stream encoder construction in `dcn315_resource.c`. `stream_enc_regs[]` supplies instance-specific DP/DIG/DME addresses, while `se_shift` and `se_mask` supply fields like MSA timing, MSE rate, secondary-data controls, HDMI GC, generic packet controls, DSC/metadata fields, and FIFO controls. The constructed `dcn10_stream_encoder` then serves higher-level modeset, audio, infoframe, metadata, and DSC operations.

DisplayPort output integrates multiple register groups from this chunk. A DP stream can involve MSA timing, pixel format, video stream enable, DPHY training/CRC/status, secondary-data audio/metadata packets, MSE/MST slot allocation, DSC fields, ALPM, and GSP double-buffer status. Correct operation depends on the DP instance number in the offset table matching the logical engine selected by resource construction.

HDMI/TMDS output integrates DIG fields from this chunk with AFMT and VPG/DME blocks outside or adjacent to the range. The HDMI packet controls in DIG1/DIG2 schedule audio infoframes, MPEG/ACP/ISRC/null/GC packets, generic packet slots 0-14, and immediate sends. Audio clock regeneration depends on ACR control and N/CTS fields.

DSC and metadata paths depend on `DP_DSC_CNTL`, `DP_DSC_BYTES_PER_PIXEL`, `DP_SEC_METADATA_TRANSMISSION`, `DP_GSP11_CNTL`, and related GSP line-number/enable fields. Higher-level DSC mode validation and Display Mode Library logic decide whether compressed transport is used; these field definitions are the hardware packing layer for stream-encoder programming.

IRQ, DMUB, GPIO, and diagnostic code share the same generated DCN315 namespace. Even if they do not directly use every DP/DIG field in this slice, register database drift can surface across resource construction, firmware service access, interrupt registration, connector detection, and debug register dumps.

## Risks And Edge Cases

The chunk begins and ends mid-register. It starts after the shifts and early masks for `DP1_DP_SEC_CNTL1`; only the final GSP masks are present here. It ends before the final `DIG2_HDMI_GC__HDMI_PACKING_PHASE_OVERRIDE_MASK`. The merge lane must combine neighboring chunks before making complete-register claims for those registers.

Repeated instance layouts are copy-sensitive. DP1 and DP2, and DIG1 and DIG2, largely duplicate field names with only the instance prefix changed. A generator or merge error can leave a field present for one instance but wrong for the next, and reviews may miss it because the blocks are visually repetitive.

Wrong shifts or masks in this file can compile cleanly. If macro names still exist, the driver may write a plausible 32-bit value with a wrong field position. Likely symptoms include broken DP link training, MST slot allocation errors, invalid MSA timing, incorrect DSC packetization, missing HDR/metadata packets, stuck GSP pending bits, HDMI audio or infoframe failures, or misleading CRC/status diagnostics.

Packed high-bit fields are particularly sensitive. Examples include line-number fields using upper 16 bits, MSE rate X/Y splits, MSA timing packed into low/high 16-bit halves, sync polarity high bits, and generic packet controls that pack four per-slot bits across the whole register.

Status and command fields sit close together. For example, send bits are adjacent to pending/deadline-missed bits, collision status is adjacent to collision ACK, immediate-send fields are adjacent to immediate-send-pending fields, and enable fields are adjacent to double-buffer status. Blind read-modify-write operations must respect hardware access rules that are not documented in this header.

Generic sideband packet slots are easy to misindex. DP GSP4-11 fields and HDMI generic packet slots 0-14 are represented through repeated bit layouts. Off-by-one slot selection can route PPS, metadata, audio, ISRC/MPEG, or vendor packets to the wrong hardware packet slot.

DSC state is cross-field dependent. `DP_DSC_CNTL`, `DP_DSC_BYTES_PER_PIXEL`, GSP11 PPS scheduling, MSA/VBID fields, and secondary-data timing must be coherent with the selected stream timing and link bandwidth. Bad field metadata may show up as sink corruption rather than an obvious kernel failure.

ALPM, DPHY, CRC, and fast-training fields describe live link state. Tests that read these fields must account for asynchronous hardware updates, stale diagnostic state, and power-management transitions.

## Test Signals

Build-time coverage should catch missing or renamed macros in DCN315 builds that compile `dcn315_resource.c`, `dcn314_dio_stream_encoder.h`, `dcn30_dio_stream_encoder.c`, `dcn20_stream_encoder.c`, `dmub_dcn315.c`, `irq_service_dcn315.c`, and DCN315 GPIO translation/factory code. A successful build does not prove numeric correctness, but missing field macros fail early.

A mechanical consistency check should verify that complete registers in this line range have matching `__SHIFT` and `_MASK` definitions for each field, while excluding the partial first and last registers. It should also compare DP1 versus DP2 and DIG1 versus DIG2 repeated fields for expected structural equivalence.

DisplayPort validation should exercise DCN315 DP1/DP2-capable routes across multiple modes, lane counts, link rates, MST/MSE allocations, DSC-required modes, HDR/static metadata, audio packets, ALPM transitions, suspend/resume, hotplug, and link retraining. Useful signals are stable modesets, no AUX or training timeouts, correct DPCD/EDID reads, no unexpected CRC/training/status errors, and no stuck MSE/GSP update-pending bits.

HDMI/TMDS validation should exercise DIG1/DIG2 routes with audio, AVMUTE transitions, ACR programming, infoframes, generic packet slots, immediate packet sends, VBI packets, deep color, DVI/TMDS fallback, output CRC, and hotplug/resume. Good signals are correct sink-reported infoframes, stable audio/channel status, expected ACR values, no FIFO/status anomalies, and clean packet analyzer captures.

Metadata and DSC validation should cover dynamic metadata enable/disable, DP metadata packet line scheduling, HDMI metadata packets, GSP11 PPS enable/line selection, DSC bytes-per-pixel programming, DSC compressed modes, and mode changes between DSC and non-DSC streams. Signals include correct PPS/metadata captures, successful high-bandwidth modesets, no corrupted compressed output, and sane status readbacks.

Diagnostic validation should cover output CRC, DPHY CRC, MSE SAT status, fast-training status, ALPM status, HDMI status, ACR status, and generic packet pending bits. Tests should clear or initialize diagnostic state before reading it so stale status does not hide field-layout errors.

## Open Cross-Chunk Notes

The previous chunk is needed to describe `DP1_DP_SEC_CNTL1` completely. This chunk only contains the final masks for that register. The next chunk is needed to complete `DIG2_HDMI_GC`, because this range ends after `DIG2_HDMI_GC__HDMI_PACKING_PHASE_MASK` and before the override mask. Whole-file research should also reconcile this slice with adjacent DCN315 sh/mask chunks that contain the offset-matched DP0, DIG0, later DIG2, AFMT, AUX, DCIO, DIO, PWRSEQ, and DSC blocks.
