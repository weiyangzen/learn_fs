# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 1-2508

## Scope

This chunk is the opening portion of AMDGPU DCN 3.1.6 generated register metadata. It contains copyright/license text, the header guard, and C preprocessor constants for register-field shifts and masks. It is not executable code and defines no functions, structs, enums, or runtime storage.

The exact range spans line 1 through line 2508 of `dcn_3_1_6_sh_mask.h`. It starts at the file prologue and enters these hardware address blocks:

- HDA/Azalia controller, endpoint, input endpoint, root, and output stream descriptor blocks.
- Legacy VGA register windows in `dce_dc_mmhubbub_vga_dispdec`.
- DCCG display clock generator DFS and clock-control blocks.
- Two DCCG DC perfmon blocks.
- The beginning of the DMCU block, ending mid-register inside `DMCU_INTERRUPT_STATUS`.

The chunk has 2,101 `#define` lines. Each meaningful definition follows the generated AMD register convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field bit mask.

## Purpose

The purpose of this chunk is to publish DCN 3.1.6 bitfield layout for low-level display, audio, clocking, diagnostics, and microcontroller registers. The companion address header names register addresses; this shift/mask header tells AMDGPU display code how to pack and unpack individual fields for memory-mapped register access.

Major covered areas:

- `AZCONTROLLER0` and partial `AZCONTROLLER1`: HDA controller capability, version, global control/status, wake/status, stream interrupt masks/status, wall-clock, CORB/RIRB base address and pointer fields, immediate command/response registers, and DMA position buffer fields.
- `AZENDPOINT*`, `AZINPUTENDPOINT*`, and `AZROOT*`: immediate command data/index register fields for HDA codec endpoint/root interactions.
- `AZSTREAM0_1` through `AZSTREAM7_1`: replicated HDA output stream descriptor controls, cyclic buffer state, last valid index, FIFO size, sample format, buffer descriptor list base addresses, and link-position aliases.
- Legacy VGA fields: `VGA_MEM_*_PAGE_ADDR`, `CRTC8_*`, `GENFC_*`, `GENS*`, `ATTR*`, `GENMO_*`, `SEQ8_*`, `DAC_*`, and `GRPH8_*`.
- DCCG clocking: `DENTIST_DISPCLK_CNTL`, PHY PLL pixel clock resync controls, DP/DTB/DPP/DSC/HDMI/audio DTO phase and modulo registers, clock source selectors, gate-disable controls, CGTT delay controls, soft reset, force-disable fields, pixel-rate controls for OTG0-OTG3, and vsync counter/latch controls.
- Perfmon: `DC_PERFMON0_*` and `DC_PERFMON1_*` counter selection, state, run/stop, interrupt, compare-value, and high/low counter fields.
- DMCU: reset/enable/status, firmware start/end/checksum fields, ERAM/IRAM host access, event trigger, internal interrupt status, static-screen interrupt controls, and the opening fields of DMCU interrupt status.

## Important Definitions

This header's API surface is macro-only. Driver code consumes the constants through AMD display register helpers such as generated `REG_GET`, `REG_SET`, and `REG_UPDATE` style macros rather than by linking symbols from this file.

Important groups in this chunk:

- HDA controller fields: `AZCONTROLLER0_GLOBAL_CAPABILITIES`, `AZCONTROLLER0_GLOBAL_CONTROL`, `AZCONTROLLER0_INTERRUPT_CONTROL`, `AZCONTROLLER0_INTERRUPT_STATUS`, `AZCONTROLLER0_STREAM_SYNCHRONIZATION`, CORB/RIRB registers, immediate command status, and DMA position buffer address fields define audio controller capabilities, reset/flush/unsolicited-response control, stream interrupt enable/status bits, command/response DMA ring programming, and position-buffer DMA.
- HDA stream descriptor fields: each `AZSTREAM*_1_OUTPUT_STREAM_DESCRIPTOR_*` group provides stream reset/run, interrupt enables, FIFO/descriptor error flags, FIFO readiness, stream number, cyclic buffer length, last-valid index, FIFO size, sample format, BDL base address, and link-position fields. The eight stream blocks use the same field layout.
- VGA compatibility fields: the VGA page, CRTC, sequencer, graphics, attribute, DAC, feature-control, miscellaneous-output, and status fields expose legacy display register state through the DCN register map.
- DCCG clock programming fields: `DENTIST_DISPCLK_CNTL`, `DISPCLK_FREQ_CHANGE_CNTL`, `DP_DTO*_PHASE`, `DP_DTO*_MODULO`, `DTBCLK_DTO*_PHASE`, `DTBCLK_DTO*_MODULO`, `DPPCLK*_DTO_PARAM`, `DSCCLK*_DTO_PARAM`, `HDMISTREAMCLK0_DTO_PARAM`, and audio DTO registers describe fractional clock generation and ramping.
- DCCG gate/source fields: `DCCG_GATE_DISABLE_CNTL`, `DCCG_GATE_DISABLE_CNTL2`, `DCCG_GATE_DISABLE_CNTL3`, `DCCG_GATE_DISABLE_CNTL4`, `DPSTREAMCLK_CNTL`, `SYMCLK32_*`, `HDMISTREAMCLK_CNTL`, `HDMICHARCLK0_CLOCK_CNTL`, and `PHY*SYMCLK_CLOCK_CNTL` describe source selection, enable/force-enable, and clock gating for display, DP, HDMI, PHY, DPP, DSC, DMCUB, AOM, and related clocks.
- OTG pixel-rate fields: `OTG0_PIXEL_RATE_CNTL` through `OTG3_PIXEL_RATE_CNTL` and `OTG*_PHYPLL_PIXEL_RATE_CNTL` encode DTO enable/status, add/drop pixel controls, half-rate output, FIFO error reporting, error counts, DTO division, and PHY PLL pixel-rate source selection.
- Vsync/time-base fields: `MILLISECOND_TIME_BASE_DIV`, `MICROSECOND_TIME_BASE_DIV`, `DCCG_VSYNC_CNT_CTRL`, `DCCG_VSYNC_CNT_INT_CTRL`, and `DCCG_VSYNC_OTG*_LATCH_VALUE` define timebase divisors, clock source selection, vsync counter control, per-OTG latch enable/trigger selection, interrupt status/clear/mask fields, and latched values.
- Perfmon fields: each `DC_PERFMON{0,1}` block defines event selection, counter value source, count mode, hardware stop/start controls, run enable, interrupt controls, active state, counted value type, counter state selectors, report count, count-off interrupt status/ack, compare-value interrupt status/clear/mask, and 64-bit high/low readback registers.
- DMCU fields: `DMCU_CTRL`, `DMCU_STATUS`, firmware address/checksum registers, ERAM/IRAM access control/data registers, `DMCU_EVENT_TRIGGER`, `DMCU_UC_INTERNAL_INT_STATUS`, `DMCU_SS_INTERRUPT_CNTL_STATUS`, and the visible portion of `DMCU_INTERRUPT_STATUS` describe host control of the display microcontroller, firmware memory windows, software/internal interrupts, static-screen interrupts, and power-domain event interrupts.

Generated field names ending in `_MASK_MASK`, such as `DCCG_VSYNC_CNT_INT_CTRL__DCCG_VSYNC_CNT_OTG0_LATCH_MASK_MASK` and `DC_PERFMON0_PERFCOUNTER_CNTL__PERFCOUNTER_OFF_MASK_MASK`, are intentional: the hardware field itself is named `*_MASK`, and the generator appends `_MASK` for the bit mask constant.

## Control Flow and State

There is no C control flow in this header. Runtime behavior is created by code that includes this file and applies the constants to register reads and writes. Typical usage is:

1. DC/AMDGPU code selects the DCN 3.1.6 register address for a hardware block.
2. It uses the matching `__SHIFT` and `_MASK` constants to insert or extract a field.
3. The write updates memory-mapped hardware state, or the read observes current hardware state.
4. Later reads check status, interrupt, pending, done, or error fields to complete the protocol.

The stateful hardware protocols represented in this chunk include:

- HDA command/response rings: CORB and RIRB base addresses, read/write pointers, size, DMA enable, reset, memory-error, response interrupt, and overrun fields persist in audio-controller hardware after programming.
- HDA output DMA streams: stream reset/run, BDL pointer, cyclic buffer length, last-valid index, format, FIFO readiness, and error flags control and report audio DMA stream execution.
- Clock programming and handshakes: DENTIST, DTO, pixel-rate, and frequency-ramp fields configure generated clocks; fields such as `*_CHGTOG`, `*_DONETOG`, `*_CHG_DONE`, `*_ENABLE_STATUS`, `DISPCLK_FREQ_RAMP_DONE`, and FIFO error counters report asynchronous clock transitions.
- Clock gating and reset state: DCCG gate-disable, soft-reset, force-disable, CGTT delay, and source-select fields persist as display-clock control state and directly affect whether downstream display/audio/PHY paths can run.
- Perfmon counters: perfmon run/stop, event selection, counter state, interrupt enable/status/ack, and high/low counter registers form a hardware measurement state machine.
- DMCU host control: reset/enable/wait/stop status, firmware address/checksum setup, ERAM/IRAM access windows, software events, internal interrupt status, and static-screen/DMCU interrupt clear bits represent host-visible microcontroller state.

## Dependencies and Integration Points

This file depends on the generated AMD ASIC register naming contract. It is useful only with the corresponding DCN 3.1.6 address header and the AMDGPU display register access layer.

Primary integration points:

- AMD DC register helpers that expect field shift/mask macros paired with register addresses.
- HDA/HDMI audio setup paths that initialize Azalia controller, codec immediate commands, stream descriptors, CORB/RIRB rings, and audio DTOs.
- Display clock generator code that programs DISPCLK, DPPCLK, DPREFCLK, DTBCLK, DSCCLK, PHY pixel clocks, HDMI stream clocks, and gate-disable or reset controls.
- Link/pipe timing code that uses OTG pixel-rate, DP DTO, DTB DTO, and vsync counter/latch fields.
- Diagnostics and performance tooling that configures DCCG perfmon counters and reads counter high/low values or compare interrupts.
- DMCU/DMCUB-related power, firmware, static-screen, and interrupt handling paths that touch the legacy DMCU register block.

The header itself has no persistence. Persistence is in hardware registers after MMIO writes and in the compiler output after macros are expanded into constants.

## Risks and Edge Cases

- Generated-header drift is high impact. A wrong mask or shift silently targets the wrong hardware bits and can break audio DMA, clock generation, display timing, diagnostics, DMCU control, or interrupt handling.
- Several fields share a bit position for status and clear semantics, for example DCCG vsync latch interrupt status/clear, DMCU static-screen occurred/clear, and DMCU interrupt occurred/clear fields. The header names the bits but does not encode write-one-to-clear or read-only/write-only semantics; caller sequencing must come from the register spec and driver conventions.
- Chunk boundaries are not semantic boundaries. This chunk starts cleanly at the file prologue but ends inside `DMCU_INTERRUPT_STATUS`: lines after 2508 contain the remaining masks and subsequent DMCU fields. The merge lane must combine adjacent chunks before making whole-register claims about `DMCU_INTERRUPT_STATUS`.
- `AZCONTROLLER0` is complete for the common controller fields in this range, while `AZCONTROLLER1` begins later and only includes the CORB/RIRB/immediate-command/DMA-position subset in this chunk. Absence of an `AZCONTROLLER1` field here should not be interpreted as absence from the full file or hardware.
- Repeated stream and clock blocks are easy to update inconsistently by hand. The source is generated; manual edits to one `AZSTREAM*_1`, `OTG*_PIXEL_RATE_CNTL`, `DC_PERFMON*`, or PHY clock family risk breaking replicated hardware instances.
- Many fields are full-width `0xFFFFFFFFL` counters, data windows, or address fragments; consumers must use the correct register width and must avoid signed arithmetic surprises when composing values in C.
- Address-alignment and unimplemented-bit fields in CORB/RIRB, BDL, and DMA position base addresses indicate reserved low bits. Callers must respect alignment requirements instead of assuming arbitrary byte addresses are accepted.

## Test Signals

There are no unit-testable functions in this chunk. Useful validation signals are compile-time, structural, and hardware-integration focused:

- Build coverage: AMDGPU/DC code that includes `dcn_3_1_6_sh_mask.h` should compile without undefined field macros for DCN 3.1.6 paths.
- Generated consistency checks: each mask should align with its shift and expected field width; replicated families such as `AZSTREAM0_1` through `AZSTREAM7_1`, `OTG0` through `OTG3`, PHY PLL resync controls, and `DC_PERFMON0`/`DC_PERFMON1` should retain matching layouts where hardware instances are replicated.
- Audio validation: HDMI/DP audio bring-up should exercise CORB/RIRB command response, immediate codec commands, stream descriptor DMA, BDL programming, position-buffer reporting, interrupts, and FIFO/descriptor error fields.
- Clock/timing validation: display mode set, clock switching, deep-color modes, DSC/DPP clock DTO programming, DP/DTB DTO programming, and pixel-rate changes should complete without FIFO errors and should observe expected `*_DONE`, `*_STATUS`, latch, and error-count behavior.
- Perfmon validation: configuring both DCCG perfmon blocks should produce monotonic high/low counter values, correct active state, and expected compare-value interrupt status/ack behavior.
- DMCU validation: firmware-memory access, reset/enable status, software/internal interrupt delivery, static-screen interrupt clear, and visible power-domain interrupt bits should behave as expected on hardware that still uses this DMCU block.

## Chunk Notes for Merge Lane

- The range covers 2,508 source lines and 2,101 `#define` lines.
- Address-block starts in this chunk are at lines 29, 281, 290, 299, 308, 321, 428, 517, 526, 535, 544, 606, 668, 730, 792, 854, 916, 978, 1040, 1064, 2043, 2181, and 2319.
- The largest definition families in this chunk are DCCG clock/control fields, DMCU fields, `AZCONTROLLER0`, the eight `AZSTREAM*_1` descriptors, the two `DC_PERFMON*` blocks, and OTG pixel-rate controls.
- This chunk has no local includes, typedefs, structs, enums, functions, or writable software state.
