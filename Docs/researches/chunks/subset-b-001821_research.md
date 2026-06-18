# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 47040-49469

## Scope

This chunk covers 2,430 lines from the generated DCN 3.1.2 shift/mask header. It contains only preprocessor constants and generated address-block comments; there are no C functions, structs, enums, storage definitions, loops, branches, or local algorithms in this range.

The range starts at the final two mask definitions for `DC_PERFMON19_PERFCOUNTER_CNTL2`, then covers complete register-field definitions for the rest of perfmon instance 19, DSC compressor instances 1 and 2, HPO top/stream-mapper fields, perfmon instances 20 through 22, HPO HDMI stream encoder 0 audio/packet blocks, HPO DP stream encoder 0, APG0, DME5/DME6, VPG5/VPG6, and the beginning of DP symbol encoder 0 sideband-packet controls. It ends inside `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL13`, after the first eight `__SHIFT` fields; the masks and remaining fields for that register continue in the next chunk.

The chunk contains 2,146 `#define` entries. Most definitions come in `__SHIFT` and `_MASK` pairs. The only boundary exceptions are the two tail masks for `DC_PERFMON19_PERFCOUNTER_CNTL2` at the beginning and the partial `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL13` shift list at the end.

## Purpose

This header slice gives DCN 3.1.2 AMD display code the bit positions and masks used to program Display Core Next hardware registers. Runtime code combines these constants with the matching offset header and AMD display register helpers to read, write, update, and decode MMIO fields without open-coded bit arithmetic.

The covered hardware domains are:

- Display Stream Compression, via `DSCC1_*`, `DSCCIF1_*`, `DSC_TOP1_*`, `DSCC2_*`, `DSCCIF2_*`, and `DSC_TOP2_*` fields.
- DC performance monitors 19 through 22, including counter selection, counter state, run/stop gating, counted-value reads, and interrupt status/ack fields.
- HPO top-level clock/reset controls and DP stream mapper target selection.
- HPO HDMI stream encoder 0 packet/audio blocks, including AFMT5, DME5, and VPG5.
- HPO DP stream encoder 0 blocks, including DP stream encoder clock/input/audio selection, APG0 audio-packet generation, DME6 metadata engine fields, VPG6 packet payload state, and DP symbol encoder 0 video/MSA/GSP sideband fields.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated preprocessor naming contract:

- `<REGISTER>__<FIELD>__SHIFT` defines the bit offset of a field.
- `<REGISTER>__<FIELD>_MASK` defines the corresponding field mask.
- Address-block comments, such as `// addressBlock: dce_dc_dsc1_dispdec_dscc_dispdec`, identify the generated hardware block that owns subsequent register groups.
- Register helper macros elsewhere concatenate register and field tokens to resolve these definitions through field-list macros such as `DSC_REG_LIST_SH_MASK_DCN20`, `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST`, and `DCN31_APG_MASK_SH_LIST`.

Important DSC register families in this chunk include:

- `DSCC{1,2}_DSCC_CONFIG0/1`, which describe slice layout, alternate ICH encoding enablement, vertical slice count, and rate-control buffer model size.
- `DSCC{1,2}_DSCC_STATUS`, exposing double-buffer update-pending state.
- `DSCC{1,2}_DSCC_INTERRUPT_CONTROL_STATUS`, mapping rate-buffer overflow/underflow status bits and per-condition interrupt-enable bits for four buffers plus rate-control model overflow bits.
- `DSCC{1,2}_DSCC_PPS_CONFIG0` through `PPS_CONFIG22`, mapping Display Stream Compression PPS fields: DSC version, PPS identifier, line buffer depth, bits per component/pixel, VBR, 4:2:2/4:2:0/native modes, chunk size, picture size, slice size, initial transmit/decode delay, scaling values, BPG offsets, initial/final offsets, flatness QP, RC model size, RC edge factor, quantization increment limits, target offsets, RC buffer thresholds, and range min/max QP and BPG offsets.
- `DSCC{1,2}_DSCC_MEM_POWER_CONTROL`, mapping memory low-power force/disable/default state and separate RAM power-state indicators.
- `DSCC{1,2}_DSCC_*_SQUARED_ERROR_*`, `MAX_ABS_ERROR*`, and rate-buffer fullness registers, exposing DSC debug/quality/error metrics and fullness counters.
- `DSCCIF{1,2}_DSCCIF_CONFIG0/1`, mapping source-select, bits per component, pixel format, back-pressure delay, and YCbCr 4:2:2 simple/stuffing/depth behavior.
- `DSC_TOP{1,2}_DSC_TOP_CONTROL` and `DSC_DEBUG_CONTROL`, mapping DSC clock enable, clock-gating disables, memory shut-down control, debug enable, and test-clock mux selection.

Important perfmon register families include:

- `DC_PERFMON{19,20,21,22}_PERFCOUNTER_CNTL` and `CNTL2`, configuring eight counters through event selection, counted-value type, hardware stop selectors, count-off selector, and secondary selector fields.
- `DC_PERFMON{19,20,21,22}_PERFCOUNTER_STATE`, mapping each counter's two-bit state and per-counter state selector.
- `DC_PERFMON{19,20,21,22}_PERFMON_CNTL` and `CNTL2`, defining perfmon run state, report count, count-off interrupt enable/status/ack, count-off interrupt type, clock enable, and run-enable start/stop selectors.
- `DC_PERFMON{19,20,21,22}_PERFMON_CVALUE_INT_MISC`, `CVALUE_LOW`, `HI`, and `LOW`, exposing counter interrupt status/ack bits and low/high counted-value readback fields.

Important HPO and stream encoder families include:

- `HPO_TOP_CLOCK_CONTROL`, which has a dense set of 15 clock-enable and 15 clock-on fields for DTO, stream encoder, DP link encoder, DPG, PHY, stream encoder clock, HDMI stream encoder, audio, DMU, DIO, DISPCLK, DPREFCLK, SYMCLK, and ALINK clocks.
- `HPO_TOP_HW_CONTROL`, mapping global HPO enable.
- `DP_STREAM_MAPPER_CONTROL0` through `CONTROL3`, mapping DP stream link target fields.
- `DP_STREAM_ENC0_DP_STREAM_ENC_*`, mapping stream encoder clock enable, pixel/audio input mux selection, clock-ramp FIFO reset/enable/status/level, and spare bits.
- `DP_SYM32_ENC0_DP_SYM32_ENC_CONTROL`, `VID_FIFO_CONTROL`, `VID_MSA_DOUBLE_BUFFER_CONTROL`, `VID_PIXEL_FORMAT_DOUBLE_BUFFER_CONTROL`, `VID_PIXEL_FORMAT`, `VID_MSA0` through `VID_MSA8`, and `HBLANK_CONTROL`, mapping symbol encoder reset/enable status, pixel-to-symbol FIFO state, MSA and pixel-format double buffering, pixel encoding/depth, MSA lane payload words, and minimum hblank symbol width.
- `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL0` through the partial `CONTROL13`, mapping generic secondary data packet transmission modes: video/idle continuous transmission, one-shot triggers, trigger position, double buffering, payload size, SOF reference, deadline missed/pending states, double-buffer pending state, and transmission line number.

Important HDMI/DP packet and audio families include:

- `AFMT5_AFMT_*`, mapping HDMI audio and infoframe behavior: VBI packet control, audio packet layout/send behavior, audio info bytes, IEC 60958 channel-status words, audio CRC control/result, ramp control, AFMT status, audio source selection, infoframe control, interrupt status, and memory power.
- `DME5_DME_*` and `DME6_DME_*`, mapping data/metadata engine enable, update, generic packet, multi-frame, line-number, double-buffer, pending, immediate update, and memory power control fields.
- `VPG5_VPG_*` and `VPG6_VPG_*`, mapping generic packet access/data, GSP frame-update and immediate-update controls for multiple packets, generic status, memory power, ISRC access/data, and MPEG infoframe payload fields.
- `APG0_APG_*`, mapping DP audio packet generator reset/status, enable, stream ID, debug audio channel generation, packet control, audio CRC, status, memory power, and spare bits.

## Control Flow

This chunk has no runtime control flow. Its effective control flow is compile-time token resolution:

1. DCN 3.1.2 display code includes `dcn_3_1_2_sh_mask.h` with the matching DCN 3.1.2 offset header.
2. Resource constructors and hardware-block headers define per-block register, shift, and mask tables by expanding macros such as `DSC_SF`, `SE_SF`, and `SRI_ARR`.
3. Runtime MMIO helpers such as `REG_GET`, `REG_SET`, `REG_SET_N`, and `REG_UPDATE` use the resulting register address, shift, and mask tables to isolate or update hardware fields.

The source order mirrors generated hardware address-block order. Within most register comments, all `__SHIFT` macros for the register are emitted first and all `_MASK` macros follow. The chunk boundaries split two generated groups, so whole-file analysis must reconcile the missing beginning of `DC_PERFMON19_PERFCOUNTER_CNTL2` and the missing tail of `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL13`.

## State And Persistence Behavior

The header itself stores no state and persists no data. It describes the bit layout of state held by DCN 3.1.2 display hardware:

- DSC PPS, slice, rate-control, DSCCIF, and top-control fields persist in the DSC hardware until reprogrammed, reset, power-gated, or restored across suspend/resume.
- DSC status, interrupt, error, fullness, and memory power-state fields can change asynchronously as compression runs, buffers fill or drain, interrupts occur, or memory power management changes state.
- Perfmon control fields configure hardware counters, while counter state, interrupt status, and counted-value fields reflect live hardware measurement state. Interrupt ack fields are write-sensitive and should be handled according to the hardware programming guide, not inferred from this header alone.
- HPO clock and hardware-enable fields control hardware availability. Clock-on/status fields report live clock state and may lag requested enable bits.
- AFMT, APG, DME, VPG, DP stream encoder, and DP symbol encoder fields persist programmed packet, audio, metadata, stream, MSA, and double-buffer state until reprogramming or reset. Pending/status/deadline fields are live hardware observations.

This file does not specify reset values, legal enumerations, read/write permissions, sticky semantics, write-one-to-clear behavior, or sequencing requirements. Those behaviors come from the ASIC register specification and the driver code that consumes these macros.

## Dependencies And Integration Points

This chunk depends on generated DCN 3.1.2 register files remaining synchronized:

- The matching `dcn_3_1_2_offset.h` supplies register offsets and base indices for the same register names.
- AMD display register helper macros depend on the exact suffix convention used here: `__SHIFT` for bit positions and `_MASK` for masks.
- DSC integration occurs through `drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.*` and resource files that expand `DSC_REG_LIST_DCN20` and `DSC_REG_LIST_SH_MASK_DCN20` for DSC instances.
- HPO DP stream encoder integration occurs through `drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h`, whose DCN3.1 mask/shift list references fields from `DP_STREAM_MAPPER_CONTROL0`, `DP_STREAM_ENC0_*`, and `DP_SYM32_ENC0_*`.
- APG integration occurs through `drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.h`, which references `APG0_APG_CONTROL`, `APG0_APG_CONTROL2`, `APG0_APG_DBG_GEN_CONTROL`, and `APG0_APG_MEM_PWR` fields from this range.
- DMUB and IRQ code include this generated header directly for DCN 3.1.2 display management and interrupt handling.

The main contract is compile-time naming plus numeric correctness. Missing or renamed fields usually produce build failures in generated field-list expansions; wrong masks or shifts can build successfully and cause bad MMIO writes or incorrect status decoding.

## Risks And Edge Cases

- The chunk starts mid-register at `DC_PERFMON19_PERFCOUNTER_CNTL2`; only two masks are present here. The previous chunk must be merged to describe the whole register.
- The chunk ends mid-register at `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL13`; only the first eight shift definitions are present here. The next chunk must supply the remaining shifts and masks.
- DSC1 and DSC2 register blocks are nearly identical. Prefix mistakes can route PPS or control writes to the wrong DSC instance and may only appear when multiple compressed streams are active.
- DSC PPS fields are tightly packed and protocol-sensitive. Mask/shift mistakes in bits-per-pixel, slice size, RC model, thresholds, or range QP/BPG fields can produce blanking, link training failures, visible corruption, or underrun/overflow interrupts.
- Interrupt-control registers pack status and enable fields into the same word. Consumers must not infer clear or acknowledge behavior from the mask name alone.
- Perfmon fields mix selectors, live state, counted values, interrupt status, and ack bits. Using the wrong counter instance or selector can silently invalidate performance telemetry.
- HPO clock-enable fields and clock-on fields are adjacent and repetitive. Confusing request bits with status bits can make reset or enable sequencing unreliable.
- DP symbol encoder GSP controls repeat the same field layout across many packet slots. A single wrong packet index can transmit the right sideband payload at the wrong cadence or scanline.
- Several fields use full-width masks such as `0xFFFFFFFFL`; consumers should avoid signed intermediate assumptions and should use the driver helper types consistently.
- Cross-generation reuse is risky. DCN 3.1, 3.1.2, 3.2, and later HPO/DSC blocks share names and layouts in many places but are not guaranteed to be numerically identical.

## Test Signals

Useful validation signals are mostly build-time, static-comparison, and hardware-integration oriented:

- Build AMDGPU display code for DCN 3.1.2 configurations to catch unresolved field names in `DSC_REG_LIST_SH_MASK_DCN20`, `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST`, `DCN31_APG_MASK_SH_LIST`, IRQ, and DMUB include paths.
- Compare this header against the matching `dcn_3_1_2_offset.h` and the authoritative register database to verify that every register in this range has matching offsets and that every mask matches the documented bit range.
- Exercise DSC enable/disable and compressed DisplayPort modes across one and two DSC instances; verify PPS programming, slice dimensions, bits-per-pixel, DSCCIF input format, top clock enable, double-buffer update pending, and absence of rate-buffer overflow/underflow interrupts.
- Run display suspend/resume, hotplug, and modeset tests with DSC enabled to confirm DSC, DSCCIF, and DSC_TOP state is restored or reprogrammed correctly.
- Exercise HPO DP link bring-up and stream mapping, checking stream target selection, stream encoder clock/input mux state, FIFO reset/enable/done transitions, symbol encoder reset/enable/done transitions, MSA programming, pixel-format double buffering, and hblank symbol width.
- Test DP sideband packet scheduling for GSP packet slots covered here, including continuous transmission, one-shot transmission, SOF reference, transmission line number, double-buffer pending, and missed-deadline status.
- Exercise HDMI and DP audio packet paths, checking AFMT/APG enablement, stream ID selection, audio info fields, IEC 60958 status fields, audio CRC results, memory power controls, and mute/packet enable behavior.
- Validate DME/VPG generic packet and infoframe paths by changing metadata and observing double-buffer pending/status transitions plus correct ISRC/MPEG/generic payload transmission.
- Use perfmon instances 19 through 22 to count a known display event, then verify counter state transitions, low/high counted value readback, interrupt status, and ack behavior.

## Open Cross-Chunk Questions

- The merge lane should combine this with the previous chunk to reconstruct the full `DC_PERFMON19_PERFCOUNTER_CNTL2` field list.
- The merge lane should combine this with the next chunk to finish `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL13`.
- Whole-file analysis should verify whether DCN 3.1.2 resource code intentionally exposes all packet slots and DSC instances covered by this generated header, or whether some definitions are generated but unused on specific ASIC variants.
