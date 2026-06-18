# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h lines 15539-17539

## Scope

This chunk covers the final 2,001 lines of the generated-style AMD DCN 2.0 register offset header. It contains only C preprocessor constants: no functions, structs, enums, inline helpers, or executable statements. The range starts in the middle of the `DSCL5` scaler block, covers the full `CM5` color-management block, a DPP5 performance monitor, the HDA/Azalia controller and stream descriptor maps, legacy VGA indexed-register indices, Azalia codec/endpoint indirect register indices, and ends at the file's closing `#endif`.

The source region contains 1,762 `#define` entries. `mm*` names are MMIO register offsets paired with `*_BASE_IDX` macros; `ix*` names are indirect register indices used through index/data windows such as Azalia endpoint and VGA indexed access paths. Most DPP5/DCN display offsets in this chunk use base index `2`, Azalia controller/stream registers mainly use base index `0`, and some aliases such as wall-clock/LPIB readback use base index `1`.

## Purpose

The macros provide the address constants consumed by DCN 2.0 display and audio code when programming hardware blocks:

- Tail of DPP5 display scaler (`DSCL5`): scaler mode, tap control, horizontal/vertical fixed-point ratios and phases for luma/RGB and chroma, black offset, update/autocal controls, overscan, OTG blanking mirrors, recout and MPC sizes, line-buffer format/control/status, DSCL memory power status/control, and output-buffer control.
- DPP5 color management (`CM5`): input color-space conversion, gamut remap, biases, degamma/blend-gamma/shaper LUT index/data/write-enable registers, RAM A/B region/start/slope/end controls, HDR multiplier, coefficient format, memory power controls, 3D LUT programming, output normalization/offset, and debug index/data.
- `DC_PERFMON28`: a DPP5 performance counter/perfmon register set with control, state, selected counter value, and high/low readback offsets.
- HDA/Azalia controller MMIO: CORB/RIRB command-response ring controls, immediate command/response registers, DMA position buffer base addresses, wall-clock alias, endpoint/root immediate command windows, and output stream descriptor registers for streams 0-7.
- VGA indirect indices: sequencer, CRTC, graphics-controller, and attribute-controller index values for legacy VGA paths.
- Azalia codec and endpoint indirect indices: F2 codec pin, descriptor, sink-info, input/output CRC result, root, stream latency, endpoint, and input-endpoint register spaces.
- Repeated F0 output endpoints 0-7 and input endpoints 0-7: converter parameters/controls, stream IDs, digital converter controls, pin parameters, widget controls, multichannel/HBR/channel allocation, hotplug, unsolicited response, configuration defaults, LPIB/status/infoframe, sink/audio descriptor fields, codec status overrides, and audio enable/format-change interrupt status.

## Important Macro Families

`mmDSCL5_*` continues a DPP instance that began before this chunk. The first line is the `mmDSCL5_SCL_MODE_BASE_IDX` companion for the preceding `mmDSCL5_SCL_MODE` offset. The remaining DSCL5 macros cover scaler setup and memory/output-buffer control from offsets `0x3763` through `0x3781`, all in base index `2`.

`mmCM5_*` spans offsets `0x3790` through `0x3860` under `dce_dc_dpp5_dispdec_cm_dispdec`. The block includes paired matrix coefficient registers for ICSC and gamut remap, A/B RAM layouts for degamma and blend gamma, larger region tables for shaper RAMs, `CM_3DLUT_*` programming registers, and memory power/status registers. These offsets are instance-specific for DPP/color-management pipe 5.

`mmDC_PERFMON28_*` maps a compact perfmon register set at offsets `0x389a` through `0x38a2`, also base index `2`. It follows the standard DC perfmon pattern: counter control, secondary control, state, perfmon control, selected counter-value interrupt/misc state, and high/low counter data.

`mmCORB_*`, `mmRIRB_*`, `mmIMMEDIATE_*`, `mmDMA_POSITION_*`, `mmAZENDPOINT_*`, `mmAZROOT_*`, and `mmAZSTREAM0_*` through `mmAZSTREAM7_*` describe HDA/Azalia controller and output stream descriptor MMIO. Stream descriptor offsets advance by the HDA stream stride, with control/status, LPIB, cyclic buffer length, last valid index, FIFO/format, BDL pointer low/high, and LPIB alias registers.

`ixSEQ*`, `ixCRT*`, `ixGRA*`, and `ixATTR*` are legacy VGA indexed-register numbers, not direct MMIO offsets. They are meaningful only through VGA index/data accessors.

`ixAZALIA_F2_*`, `ixAUDIO_DESCRIPTOR*`, `ixSINK_DESCRIPTION*`, `ixAZALIA_INPUT_CRC*`, `ixAZALIA_CRC*`, `ixAZALIA_F2_CODEC_INPUT_*`, and `ixAZALIA_F2_CODEC_ROOT_*` are indirect Azalia codec/control indices. They describe codec verbs/registers for pin capabilities, multichannel setup, LPIB snapshotting, channel status, root/function parameters, sink description strings, and CRC result channels.

`ixAZF0STREAM0_*` through `ixAZF0STREAM15_*` expose per-stream FIFO sizing and latency counters. Each stream has the same five indices: FIFO size control, latency counter control, worst-case latency count, cumulative latency count, and cumulative request count.

`ixAZF0ENDPOINT0_*` through `ixAZF0ENDPOINT7_*` repeat a 71-index output endpoint layout. Each endpoint has converter controls, pin parameters, 14 audio descriptor slots, multichannel and HBR controls, sink info slots, hotplug and unsolicited response controls, configuration defaults, codec channel-status overrides, LPIB snapshot/readback, coding/format-change controls, wireless display/keepalive, and audio enable/disable/format-change interrupt status indices.

`ixAZF0INPUTENDPOINT0_*` through `ixAZF0INPUTENDPOINT7_*` repeat a smaller 23-index input endpoint layout for input converter and input pin programming: converter capabilities/format/stream ID/digital converter, stream format and supported-rate parameters, input pin capabilities, unsolicited response and sense, widget control, multichannel/HBR/channel allocation, hotplug, configuration defaults, LPIB snapshot/readback, input-status control, and infoframe.

## APIs, Types, and Functions

There are no callable APIs or C types in this chunk. The macros are the hardware-facing address API for generated ASIC register tables:

- `mmREGISTER` constants give register offsets for direct MMIO or register-helper access.
- `mmREGISTER_BASE_IDX` selects the register base aperture/table used by the AMD display register access macros.
- `ixREGISTER` constants give indices for indirect register windows, especially VGA and Azalia endpoint/codec spaces.

Consumers pair these offsets with companion DCN 2.0 shift/mask headers and with AMDGPU display register helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, and indirect index/data helpers. The header is included by DCN 2.0 display resource setup, IRQ service, GPIO factory code, clock manager code, DMUB DCN 2.0 code, and `gmc_v10_0.c`.

## Control Flow

The header has no runtime control flow. Hardware programming flow is implied by the register groups:

1. Select the intended hardware instance and access path: direct MMIO for `mm*`, indexed VGA for `ixSEQ`/`ixCRT`/`ixGRA`/`ixATTR`, or Azalia index/data windows for `ixAZALIA*`, `ixAZF0ENDPOINT*`, and `ixAZF0INPUTENDPOINT*`.
2. For scaler/color management, program `DSCL5` ratios/phases/taps and `CM5` matrices/LUTs/3D LUT while respecting update, LUT index/data, RAM A/B, memory-power, and display-pipe timing rules.
3. For perfmon, select events and controls, start/stop or clear counters, then read state and high/low counter values from `DC_PERFMON28`.
4. For Azalia controller output, set up CORB/RIRB or immediate-command paths, configure stream descriptors and BDL pointers, program endpoint converter/pin registers through indirect indices, and monitor LPIB/status/interrupt fields.
5. For sink and audio capability reporting, read or populate descriptor/sink-info endpoint indices and codec parameter indices.
6. For status and diagnostics, read CRC result indices, stream latency counters, audio enable/disable/format-change interrupt status, and input endpoint status/infoframe indices.

Sequencing-sensitive areas include scaler coefficient and update latching, CM LUT/3D-LUT index-data programming, Azalia command ring pointer updates, stream descriptor enable/BDL programming, codec endpoint indirect access, LPIB snapshot timing, and any clear-on-write or latched status behavior in audio interrupt/status registers.

## State and Persistence

The file stores no software state. It describes hardware state that persists until explicit driver writes, reset, display modeset teardown, audio stream teardown, suspend/resume, firmware intervention, or power-gating transitions.

Important state domains in this chunk include:

- DSCL5 display scaling state: tap selection, fixed-point scale ratios, filter phases, overscan, recout/MPC geometry, line-buffer format and memory control, and DSCL/OBUF power state.
- CM5 color pipeline state: conversion/remap matrices, degamma/blend/shaper LUT contents and RAM regions, HDR multiplication, shaper scaling/offsets, 3D LUT contents and normalization/output offsets, coefficient format, debug selection, and CM memory power state.
- DPP5 perfmon state: active/counting configuration, event selection, latched state, overflow/interrupt status, and counter values.
- HDA controller state: CORB/RIRB ring pointers and control/status, immediate command status, DMA position buffer address, wall-clock readback, output stream descriptor registers, stream format, buffer descriptor pointers, and LPIB aliases.
- Azalia codec/endpoint state: converter formats and stream IDs, pin widget/hotplug/unsolicited response controls, audio descriptors, sink info, multichannel/HBR/channel allocation, channel status overrides, LPIB snapshots, format-change/audio-enable status, root/function power/reset and capability parameters, CRC results, and latency counters.
- Legacy VGA indexed state: sequencer, CRTC, graphics, and attribute registers reachable through the VGA access path.

Because these are raw hardware offsets and indices, callers must use the correct base index and access path. An `ix*` index used as direct MMIO, or an `mm*` offset used through an indirect endpoint window, would compile but address the wrong hardware surface.

## Dependencies and Integration Points

This chunk depends only on the C preprocessor, but it is useful only with the rest of AMD's DCN 2.0 generated register data:

- The companion `dcn_2_0_0_sh_mask.h` field definitions provide the bit positions/masks for these offsets.
- DCN 2.0 display resource code includes this header to construct register tables for DPP/scaler/color-management and other display blocks.
- DCN 2.0 IRQ, GPIO, and clock-manager code include it for interrupt source mapping, DDC/GPIO translation, and clock/power register access.
- DMUB DCN 2.0 code includes it for firmware-facing display register programming.
- Audio integration code uses the Azalia/HDA offsets and indirect indices to drive HDMI/DP audio stream setup, endpoint capability reporting, sink info, channel allocation, LPIB/status tracking, and interrupt handling.
- Shared register-helper infrastructure supplies the accessors that combine `mm*` offsets, `*_BASE_IDX` values, and field masks/shifts.

The repeated endpoint and input-endpoint layouts are a major integration signal. Driver code should select endpoint instances through tables or generated macros rather than constructing names or assuming all ASIC generations preserve the same endpoint count and stride.

## Risks

The primary risk is silent hardware misprogramming. Incorrect offsets or base indices compile cleanly but can write or read the wrong register aperture, causing display pipe corruption, bad color transforms, broken scaler state, perfmon readback failures, audio stream setup failures, or incorrect endpoint capabilities.

Chunk-boundary risk exists at the beginning. The slice starts on `mmDSCL5_SCL_MODE_BASE_IDX`; the matching `mmDSCL5_SCL_MODE` offset is immediately before the requested range. The final per-file reconciliation should merge the preceding chunk before describing the full DSCL5 scaler map.

Direct-vs-indirect access is a recurring hazard. `ix*` names are register indices for VGA/Azalia windows, not direct MMIO addresses. Treating them like `mm*` offsets, or using the wrong endpoint index/data pair, can touch unrelated registers or return misleading zeros.

The color-management and LUT families are order-sensitive. Programming LUT index/data/write-enable registers or RAM A/B region controls without the expected update protocol can leave partial degamma, blend-gamma, shaper, or 3D LUT contents active on a live pipe. That would show up as incorrect color, HDR errors, or transient artifacts.

HDA/Azalia controller registers have side effects and ordering constraints. CORB/RIRB pointer/control updates, immediate command status, stream descriptor enable, BDL pointer programming, and LPIB snapshots must follow HDA hardware rules. Incorrect sequencing may hang audio commands, report stale positions, underrun/overrun streams, or break HDMI/DP audio enumeration.

Status and interrupt-like endpoint indices require hardware semantics beyond the offset value. Audio enable/disable/format-change status, unsolicited responses, hotplug controls, CRC result indices, and input status fields may be latched, write-one-to-clear, or snapshot-based; blind read/modify/write can lose events or clear diagnostics unexpectedly.

Instance mix-ups are easy because endpoint and stream blocks repeat with near-identical register names. Mixing `AZSTREAMn`, `AZF0STREAMn`, `AZF0ENDPOINTn`, and `AZF0INPUTENDPOINTn` namespaces can wire the wrong stream to the wrong endpoint or read unrelated latency/status counters.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for all translation units that include `dcn_2_0_0_offset.h`, catching duplicate/missing macros and malformed generated definitions.
- Generated-header consistency checks that every `mm*` register has the expected `*_BASE_IDX`, repeated endpoint/input-endpoint/stream blocks preserve equivalent layouts, and offset progressions match the authoritative DCN 2.0 register database.
- Static checks that `mm*` offsets are consumed by direct register helpers and `ix*` indices are consumed only through the intended indexed accessors.
- Modeset and scaling tests on pipe/DPP instance 5, covering scaler ratios/phases, overscan, recout/MPC size, line-buffer state, DSCL update/autocal behavior, and memory-power transitions.
- Color-management tests for DPP5 that program ICSC, gamut remap, degamma, blend gamma, shaper LUTs, HDR multiplier, and 3D LUT paths, then verify output through CRC, readback, or visual/colorimetry validation.
- Perfmon tests that start, stop, clear, and read `DC_PERFMON28` counters and verify high/low counter behavior and state bits.
- HDMI/DP audio tests covering HDA CORB/RIRB or immediate command operation, stream descriptor setup, BDL/LPIB behavior, endpoint converter format and stream ID, hotplug/unsolicited response, channel allocation, multichannel/HBR, and format-change events.
- Sink capability tests that verify audio descriptor and sink-info indices are populated/read correctly across endpoints 0-7.
- Input audio/endpoint tests for input endpoints 0-7, including input converter format, pin sense, input status control, LPIB snapshot, and infoframe handling.
- Suspend/resume and runtime power tests that verify CM5/DSCL5 memory power states and HDA/Azalia stream/endpoint state are restored coherently.

## Cross-Chunk Notes

This is the terminal slice of `dcn_2_0_0_offset.h`. The final per-file research document should merge it with the previous chunk for the start of the `DSCL5` block and with earlier chunks that define the matching DPP, HDA, VGA, and Azalia index/data access registers. Treat this chunk as a generated register-map tail, not as a standalone module with local algorithms.
