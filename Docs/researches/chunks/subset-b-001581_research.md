# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 1-2533

## Scope And Purpose

This chunk is the opening portion of AMDGPU's generated-style DCN 1.0 register shift/mask header. It starts with the license and include guard, then defines C preprocessor constants for hardware bitfields in three major display-related areas: HD Audio controller/endpoint/stream registers, VGA compatibility registers, and the beginning of DCCG display clock generator registers.

There are no functions, structs, enums, or executable control paths in this chunk. The public interface is a large set of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros. Driver code combines these constants with sibling register-address headers and MMIO helpers so it can read, update, and compose individual fields without embedding raw bit positions in C code.

## Important APIs, Types, And Macro Families

The macro namespace is the API surface. Important groups in this chunk are:

- HDA controller global state: `AZCONTROLLER0_GLOBAL_CAPABILITIES`, version, payload capability, `AZCONTROLLER0_GLOBAL_CONTROL`, wake/status, stream synchronization, interrupt control/status, wall-clock counter, and alias fields describe controller reset, flush, unsolicited responses, stream interrupt enables, and stream-level synchronization.
- HDA command and response rings: `AZCONTROLLER0_CORB_*` and `AZCONTROLLER0_RIRB_*` define lower/upper DMA base address fields, read/write pointers, reset bits, DMA enable bits, memory-error and response-overrun interrupt fields, ring size, and response interrupt counts.
- HDA immediate command paths: `AZCONTROLLER0_IMMEDIATE_COMMAND_*`, endpoint/root/input endpoint immediate command data/index fields, and matching unprefixed aliases define codec verb/payload writes, codec address selection, command busy/result valid status, and immediate response reads.
- HDA DMA position reporting: `AZCONTROLLER0_DMA_POSITION_*` and unprefixed `DMA_POSITION_*` fields define the DMA position buffer enable bit and 64-bit base address split, with low address alignment/unimplemented bits masked separately.
- HDA stream descriptors: `AZSTREAM0_0` through `AZSTREAM7_0`, then `AZSTREAM0_1` through `AZSTREAM7_1`, repeat the same output stream descriptor layout for multiple stream instances. The fields cover stream reset/run, completion/FIFO/descriptor-error interrupt enables and statuses, FIFO readiness, stream number, link position, cyclic buffer length, last valid index, FIFO size, audio format, BDL lower/upper base address, and link-position aliases.
- VGA indexed and legacy registers: `CRTC8_*`, `GENFC_*`, `GENS*`, `ATTR*`, `GENMO_*`, `SEQ8_*`, `DAC_*`, `GRPH8_*`, and `VGA_MEM_*_PAGE_ADDR` preserve masks for VGA CRTC, sequencer, graphics, attribute, DAC, memory-page, and miscellaneous control/status fields.
- VGA display integration: `VGA_RENDER_CONTROL`, `VGA_SEQUENCER_RESET_CONTROL`, `VGA_MODE_CONTROL`, surface address/pitch registers, `VGA_HDP_CONTROL`, `VGA_CACHE_CONTROL`, per-pipe `D1VGA_CONTROL` through `D6VGA_CONTROL`, status/interrupt/clear registers, `VGA_MAIN_CONTROL`, `VGA_TEST_CONTROL`, `VGA_QOS_CTRL`, and `VGA_SOURCE_SELECT` describe VGA scanout routing, memory aperture handling, cache behavior, sequencer reset effects, and interrupt/status reporting.
- DCCG clocks and resynchronization: `PHYPLL[A-G]_PIXCLK_RESYNC_CNTL`, `PIXCLK[0-2]_RESYNC_CNTL`, `REFCLK_CNTL`, `DPREFCLK_CNTL`, `MIPI_CLK_CNTL`, `DAC_CLK_ENABLE`, `DVO_CLK_ENABLE`, `SYMCLK[A-G]_CLOCK_ENABLE`, and `AOMCLK[0-2]_CNTL` expose clock enables, source selections, deep-color controls, front-end force controls, and pixel-clock resync enables.
- DCCG DTOs and counters: `DP_DTO_DBUF_EN`, `DP_DTO[0-5]_PHASE`, `DP_DTO[0-5]_MODULO`, `DCCG_DS_DTO_*`, `MIPI_DTO_*`, `DCCG_GTC_*`, `AVSYNC_COUNTER_*`, millisecond/microsecond time-base dividers, audio DTO phase/module/modulo registers, and vsync latch/counter fields describe fractional clock generation and time/counter capture.
- DCCG power, reset, and diagnostics: `DCCG_GATE_DISABLE_CNTL`, `DCCG_GATE_DISABLE_CNTL2`, clock-gating turn-on/off delay registers, `DCCG_SOFT_RESET`, `DISPCLK_FREQ_CHANGE_CNTL`, `DC_MEM_GLOBAL_PWR_REQ_CNTL`, `DCCG_PERFMON_CNTL`, `DCCG_PERFMON_CNTL2`, `DCCG_CAC_STATUS`, `DCCG_CBUS_WRCMD_DELAY`, `DCCG_DISP_CNTL_REG`, DVO skew controls, and `DCE_VERSION` expose display clock ramping, soft reset domains, performance monitor inputs, power request gating, and version/status fields.
- OTG pixel-rate control: `OTG0_PIXEL_RATE_CNTL` through `OTG5_PIXEL_RATE_CNTL`, paired `DP_DTOx_PHASE/MODULO`, and `OTGx_PHYPLL_PIXEL_RATE_CNTL` define the source, DTO enable, downspread disable, add/drop pixel, FIFO error, error count, and PLL source fields for each timing generator.

The naming convention is regular enough for AMDGPU field helper macros: a caller can extract a field with `(value & REGISTER__FIELD_MASK) >> REGISTER__FIELD__SHIFT`, or update one by clearing the mask and OR-ing `(field_value << SHIFT) & MASK`. Fields whose names end in `MASK` naturally create symbols such as `DCCG_VSYNC_CNT_INT_CTRL__DCCG_VSYNC_CNT_OTG0_LATCH_MASK_MASK`; these are generated names, not duplicate suffix mistakes.

## Control Flow And Data Flow

This header has no runtime control flow. Its data flow is compile-time macro substitution into DC, DCE, DCCG, audio, IRQ, and AMDGPU register access code.

Several hardware protocols are implied by the field layout:

- HDA controller bring-up uses reset/flush bits, capability reads, interrupt enables, CORB/RIRB base programming, pointer resets, ring-size selection, DMA enables, and polling or interrupt-driven status checks.
- HDA stream programming uses a repeated stream-descriptor sequence: stop/reset a stream, program cyclic buffer length and BDL addresses, choose format and stream number, enable interrupts, run the stream, then observe link-position, FIFO-ready, completion, FIFO-error, and descriptor-error fields.
- VGA ownership and compatibility flows read and write legacy indexed registers, switch VGA source selection, program surface addresses/pitches, adjust `VGA_VSTATUS_CNTL`, gate memory access, and clear or mask VGA access/display-switch interrupts.
- DCCG programming selects reference and symbol clock sources, enables or gates clocks, programs DTO phase/modulo values, resynchronizes pixel clocks, ramps display clock changes, handles soft resets, and observes FIFO/error/performance/counter status.
- Vsync counter and latch fields provide a capture protocol: enable the counter, choose reset/reference/trigger behavior, enable per-OTG latch capture, read latch-value registers, and clear or mask latch interrupts.

## State And Persistence Behavior

The header itself stores no state. The durable or mutable state is in hardware registers addressed elsewhere.

Important state classes represented by this chunk include:

- Controller state: HDA reset, flush, unsolicited-response enablement, wake/status bits, interrupt enables/status, stream synchronization, wall-clock counters, immediate-command busy/result state, and CORB/RIRB ring pointers.
- DMA-visible addresses: CORB, RIRB, HDA stream BDL, and DMA position-buffer base addresses are split into lower and upper registers, with low alignment bits marked as unimplemented or enable fields.
- Stream state: per-stream run/reset, format, buffer length, BDL pointer, stream number, FIFO readiness, link position, and error/completion status persist in stream descriptor registers until changed or reset.
- VGA state: legacy indexed register data, memory page selects, render/mode controls, source selection, per-display VGA enables, cache/HDP controls, interrupt mask/status/clear bits, and test/QoS settings.
- Clocking state: DCCG clock source selection, gate-disable bits, resync enablement, DTO phase/modulo values, time-base dividers, soft-reset bits, performance-monitor enables, audio DTO source selection, and OTG pixel-rate controls all affect active display timing and audio clock behavior.
- Latched status: VGA access/display-switch status, DCCG FIFO/error counts, GTC/current counters, avsync reads, vsync latch values, and vsync latch interrupts expose state that can be consumed by diagnostics, IRQ handlers, or timing code.

Because the state is hardware-backed, incorrect masks can survive until a later driver write or hardware reset and can affect scanout, audio, memory apertures, interrupts, and clock trees.

## Dependencies And Integration Points

This header is meant to be included with DCN 1.0 register address definitions from the same `include/asic_reg/dcn/` area and consumed by AMDGPU/DC register helpers. The generated constants integrate with helper conventions such as `REG_SET_FIELD`, `REG_UPDATE`, `SR(...)`, and `SF(..., mask_sh)` tables used throughout the AMD display stack.

Concrete integration points visible in the source tree include `display/dc/irq/dcn10/irq_service_dcn10.c`, which includes `dcn/dcn_1_0_sh_mask.h`, and common AMDGPU/DCE code paths that use shared field names such as `VGA_RENDER_CONTROL__VGA_VSTATUS_CNTL_MASK` and `DCCG_AUDIO_DTO_SOURCE__DCCG_AUDIO_DTO0_SOURCE_SEL`. DCE/DC audio code uses `DCCG_AUDIO_DTO_SOURCE` fields to choose audio DTO sources and 512-frame-base-rate behavior. VGA setup and handoff code uses `VGA_RENDER_CONTROL` to control VGA vstatus handling during memory/display initialization. DCCG modules for newer DCN generations follow the same mask/shift table pattern for clock-gating, audio DTO, and pixel-rate fields.

The HDA groups integrate with the GPU display audio path rather than with a normal CPU HD-audio controller driver in this tree: DC/AMDGPU code can use these definitions when programming display audio endpoints, stream DMA descriptors, codec immediate commands, and audio timing derived from DCCG DTOs.

## Risks And Edge Cases

The main risk is register-spec drift. This file is generated from ASIC register data, and consumers assume these constants exactly match DCN 1.0 hardware. A wrong shift or mask can silently write the wrong bit in a hardware register.

Specific high-risk areas in this chunk are:

- HDA DMA base address fields, where incorrect masking of unimplemented low bits or upper/lower halves can point CORB, RIRB, BDL, or position buffers at the wrong memory.
- CORB/RIRB and stream pointer/status bits, where bad reset, run, interrupt, or error masks can hang command submission, lose responses, or hide FIFO/descriptor faults.
- Repeated stream descriptor blocks, where copy/paste or generator errors between `AZSTREAMx_0` and `AZSTREAMx_1` can affect only one stream instance and be hard to detect without multi-stream audio coverage.
- VGA legacy and render controls, where an incorrect source, aperture, cache, or vstatus bit can corrupt VGA handoff, boot console behavior, suspend/resume display restoration, or legacy register access.
- DCCG clock-gating and soft-reset fields, where writing the wrong bit can gate a live clock, reset a PLL/interface, or block display/audio timing.
- DTO phase/modulo and pixel-rate fields, where programming mistakes can cause clock drift, audio/video sync faults, FIFO underflow/overflow, or timing generator errors.
- Interrupt status/clear/mask fields that share bit positions, especially in `DCCG_VSYNC_CNT_INT_CTRL`, where clear and status names intentionally map to the same bit positions.
- Chunk boundary risk: this research covers only lines 1-2533. `DCCG_VSYNC_CNT_INT_CTRL` continues past the mapped end, and the full header contains many later DCN 1.0 register groups that must be researched by later chunk documents before drawing full-file conclusions.

## Test Signals

There are no unit tests for this header alone. Useful validation is indirect:

- Build coverage for AMDGPU/DC code that includes `dcn_1_0_sh_mask.h`; this catches missing or renamed macros but not incorrect numeric values.
- Comparison against the matching AMD DCN 1.0 register database or upstream generated header to verify every `_SHIFT` and `_MASK` value.
- Display boot, modeset, suspend/resume, hotplug, and boot-console handoff tests that exercise VGA render/source/memory controls and DCCG pixel-clock programming.
- HDMI/DP audio tests that exercise HDA stream descriptor programming, CORB/RIRB command/response handling, immediate codec commands, DMA position reporting, and audio DTO source/phase/module fields.
- Interrupt tests for HDA stream completion/error, VGA access/display-switch/status clear, and DCCG vsync latch interrupt mask/clear behavior.
- Clocking diagnostics that read back DCCG gate-disable, resync, DTO, display-clock ramp, perfmon, GTC, avsync, and FIFO error/status fields under active displays.
- Multi-pipe and multi-stream coverage, because many fields are replicated per stream, per OTG, per PHYPLL, or per display pipe and a single-pipe test can miss index-specific register-definition errors.
