# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 1-2510

## Scope

This chunk covers lines 1-2510 of a much larger AMD DCE 12.0 ASIC register mask header. The file is generated-style C preprocessor metadata: it defines bit shifts and masks for fields inside memory-mapped display-controller registers. It contains no functions, no structs, and no executable control flow. Consumers include AMDGPU display code that combines these `__SHIFT` and `_MASK` constants with register address headers and read/modify/write helpers.

## Purpose

The header provides field-level definitions for several DCE display blocks:

- VGA page-address aliases at the start of the display decode space.
- DC performance monitor instances `DC_PERFMON0`, `DC_PERFMON13`, `DC_PERFMON1`, and `DC_PERFMON9`.
- Display PLL and PLL macro register fields, including frequency-control, calibration, observation, update, and reserved PLL macro slots.
- MCIF writeback engines `MCIF_WB0`, `MCIF_WB1`, and `MCIF_WB2`.
- Capture writeback engines `CWB0` and `CWB1`.
- Main display decode VGA, legacy indexed VGA registers, D1-D6 VGA routing controls, PHY PLL pixel-clock resync controls, DCCG clock controls, pin straps, display-stream DTO, audio DTO, and the beginning of `DCE_VERSION`.

Each register field is represented by a pair such as `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`. Driver code can write a field by clearing `FIELD_MASK`, shifting a value by `FIELD__SHIFT`, and ORing it back into the register value.

## Important Macro Families

The first address blocks define `dispdec_VGA_MEM_WRITE_PAGE_ADDR` and `dispdec_VGA_MEM_READ_PAGE_ADDR`, each with page 0 and page 1 fields at shifts `0x0` and `0x10` and 10-bit masks. Later, equivalent unprefixed `VGA_MEM_WRITE_PAGE_ADDR` and `VGA_MEM_READ_PAGE_ADDR` macros appear in the main `dce_dc_dispdec` block.

The repeated `DC_PERFMON*` blocks expose the same performance-monitor register layout for several monitor instances. The key fields are:

- `PERFCOUNTER_CNTL`: event selection, counted-value selector, increment mode, hardware/run-enable controls, count-off selection, restart, interrupt enable/status behavior, active bit, interrupt type, and counter selector.
- `PERFCOUNTER_CNTL2`: counted-value type and hardware stop selectors.
- `PERFCOUNTER_STATE`: eight packed counter state fields and selector bits.
- `PERFMON_CNTL` and `PERFMON_CNTL2`: monitor state, report count, count-off interrupt enable/status/ack, clock enable, and start/stop run-enable selectors.
- `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW`: interrupt status/ack bits and counter-value readout fields.

The `PPLL_*` display PLL block defines analog and timing controls. Notable groups include `PPLL_FREQ_CTRL0/1/2/3` for fractional and integer frequency control words, denominator, slew, refclk divider, VCO pre-divider, fractional-N enable, spread-spectrum enable, frequency jump enable, TDC resolution, and DPLL config bits. `PPLL_CAL_CTRL`, `PPLL_LOOP_CTRL`, `PPLL_REFCLK_CNTL`, `PPLL_CLKOUT_CNTL`, `PPLL_OBSERVE0/1`, and `PPLL_UPDATE_CNTL` cover calibration, loop behavior, reference selection, output clocks, observability, lock/update state, and ready/pending bits. `PLL_MACRO_CNTL_RESERVED0` through `PLL_MACRO_CNTL_RESERVED41` are full-width reserved register masks.

The `MCIF_WB0`, `MCIF_WB1`, and `MCIF_WB2` sections define identical writeback buffer-manager layouts per engine. They include software control, current-line/status registers, pitch, four buffer status pairs, arbitration, SCLK/NB P-state watermark controls, luma/chroma buffer address and offset fields, VCE lock/interrupt/slice-size control, QoS, clock gating, warm-up, self-refresh, and luma/chroma sizes. Buffer status fields track active/locked/overflow/disable/mode/tag/next-buffer/field/current-line and long-line, short-line, and frame-length errors.

The `CWB0` and `CWB1` sections define capture writeback formatting and validation fields: enable, output color depth, zero padding, chroma swap, 4:2:2 luma/chroma swap, 4:4:4 rounding, pack format, output/error dimensions, CRC enable/continuous/source controls, CRC masks, and CRC result counters.

The main `dce_dc_dispdec` block includes VGA render, sequencer reset, mode, surface, memory base, HDP, cache, per-display `D1VGA_CONTROL` through `D6VGA_CONTROL`, VGA status/interrupt/clear registers, test/QoS controls, legacy VGA indexed register windows, DAC registers, source selection, PHY PLL pixel-clock resync controls for PHY PLL A-E, DCFEV pixel-rate controls, symbol-clock enables, DPREF/REF/DSI clock-gating controls, DCCG performance clock enables, CBUS write-command delay, display/audio straps, display-stream DTO and control registers, symbol-clock G enable, DPREF source control, AOM clock enables, and audio DTO2 phase/modulo.

## APIs, Types, and Functions

There are no callable APIs, C types, or function definitions in this chunk. The exported surface is entirely preprocessor constants. The naming convention is the effective API:

- `REGISTER__FIELD__SHIFT` gives the bit offset.
- `REGISTER__FIELD_MASK` gives the already-positioned bit mask.
- Register names are grouped by address-block comments, which connect the masks to companion register-address headers.

Because these macros are global C preprocessor symbols, correctness depends on exact names matching the rest of AMDGPU's generated register database and display driver helper macros.

## Control Flow

This chunk has no runtime branches or loops. The operational control flow is in callers that use these constants for register programming. Typical caller flow is:

1. Read a MMIO register by its address macro.
2. Clear one or more `*_MASK` fields.
3. Shift new field values with matching `*__SHIFT` constants.
4. Write the updated value back to hardware.
5. For status/interrupt registers, read fields such as `*_STATUS`, write ack/clear bits, or poll ready/pending fields.

The order-sensitive behavior is therefore external to this header, but several fields imply hardware sequences: PLL update locking/pending/ready, perfmon interrupt ack, MCIF buffer-manager lock/interrupt ack, VGA status clear, pixel-clock enable/resync, and DCCG DTO enable/status.

## State and Persistence

The header itself stores no software state. Its constants describe persistent hardware state held in display-controller registers until changed by MMIO writes, reset, power management, or firmware/hardware side effects. Important state domains visible in this chunk are:

- Performance-monitor configuration, counters, interrupt status, and readback values.
- PLL frequency, calibration, reference-clock, post-divider, lock, observation, and update-pending state.
- MCIF writeback buffer ownership, current buffer, line counters, overrun/error state, address fences, QoS/watermarks, and clock/self-refresh policy.
- CWB output format, frame fence dimensions, and CRC accumulation/results.
- VGA mode/routing/status/interrupt state across up to six display pipes.
- DCCG clock enable, source selection, DTO phase/modulo, hardware calibration, and clock-gating delay state.

Some macros represent write-one-to-ack or write-one-to-clear style bits by name, such as `*_INT_ACK`, `VGA_STATUS_CLEAR__*`, and `PPLL_OBSERVE0__pw_pc_clear_sticky_lock`. Caller code must follow register semantics from the hardware spec; this header only provides bit positions.

## Dependencies and Integration Points

This header depends only on the C preprocessor and include guards. It is integrated through the AMDGPU/DRM display stack under `drivers/gpu/drm/amd/include/asic_reg/dce`, typically alongside companion headers that define register offsets and base addresses for the same DCE 12.0 blocks. It is intended for low-level display code, including:

- Register accessor helpers that accept register address, mask, and shift definitions.
- Display clock and PLL programming paths.
- VGA compatibility setup and teardown paths.
- Writeback/capture setup, interrupt handling, and diagnostics.
- Performance-monitor setup and counter collection.
- ASIC-specific display initialization and power-management code.

The repeated instance prefixes (`DC_PERFMON0`, `DC_PERFMON1`, `DC_PERFMON9`, `DC_PERFMON13`, `MCIF_WB0`, `MCIF_WB1`, `MCIF_WB2`, `CWB0`, `CWB1`) are integration signals: callers select an engine instance by choosing the corresponding macro family.

## Risks

The main risk is silent hardware misprogramming. A wrong mask or shift compiles cleanly but can modify reserved bits, target the wrong subfield, leave stale state uncleared, or break timing-sensitive display hardware.

Generated-name consistency is also critical. Many blocks are repeated with near-identical layouts; copy or generation errors between instances could cause one engine to use another engine's field names or masks. Macros such as `*_MASK_MASK` are syntactically awkward but intentional for fields whose names end in `_MASK`; reviewers should not "clean them up" without checking all users.

Full-width masks such as `0xFFFFFFFFL` for address, DTO, reserved, and counter fields make width and type assumptions visible. Callers using narrower or signed intermediates can truncate values. Conversely, small legacy VGA masks such as `0xFFL`, `0x3FL`, and `0x08L` describe byte-sized indexed register windows and should not be treated as normal 32-bit display registers without the matching access path.

Several fields interact with interrupts, clock gating, and power state. Misuse of `*_INT_ACK`, clock-enable, self-refresh, NB P-state, PLL update, or reset fields can hang polling paths, lose writeback frames, or produce display underflow rather than an immediate software error.

## Test Signals

Useful validation signals are mostly integration and hardware-facing:

- Build coverage for translation units that include `dce_12_0_sh_mask.h`, especially with generated register helper macros.
- Static checks that every `REGISTER__FIELD__SHIFT` has a matching `REGISTER__FIELD_MASK`, and that masks align with shifts and expected field widths.
- Diff checks against the authoritative ASIC register-generation source for DCE 12.0.
- Display smoke tests across modesets, VGA disable/compatibility paths, link bring-up, and pixel-clock changes.
- Perfmon tests that configure counters, read low/high values, and exercise interrupt ack/status fields.
- Writeback tests for MCIF/CWB engines, including buffer rotation, pitch/address setup, overflow detection, CRC result generation, and NB P-state/clock-gating transitions.
- Runtime register readback around PLL update, DCCG DTO enable/status, and MCIF buffer-manager status to verify that programmed fields land in the intended bits.

## Cross-Chunk Notes

This is only the first 2510 lines of a 64798-line header. The final per-file research should reconcile this chunk with later chunks to identify all DCE 12.0 register families, later continuation of `DCE_VERSION`, any additional perfmon/clock/writeback instances, and the terminating include guard.
