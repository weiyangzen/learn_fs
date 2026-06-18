# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 4918-7308

## Scope

This chunk covers 2,391 lines from the generated DCN 1.0 register shift/mask header. It starts in the middle of `DC_GPU_TIMER_START_POSITION_VSTARTUP`, covers GPU timer read control, the display interrupt-status continuation chain, writeback converter/scaler/perfmon register fields for WB0 and WB1, and begins the MCIF writeback buffer-manager definitions for WB0/WB1. The slice ends on the `MCIF_WB1_MCIF_WB_BUF_1_ADDR_C_OFFSET` comment, so the matching shift/mask definitions for that final register are in the next chunk.

The source has no C functions, structs, or executable statements. Its exported interface is a dense set of preprocessor constants in the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` form. In this slice there are 2,160 `#define` entries, roughly split between shift constants and already-positioned masks.

## Purpose

The chunk describes bit layouts for several DCN 1.0 display hardware blocks:

- GPU timer readback and start-position selection fields for per-display timing events, including VSTARTUP, VSYNC_NOM, VREADY, FLIP, V_UPDATE_NO_LOCK, and FLIP_AWAY timing positions.
- The `DISP_INTERRUPT_STATUS` fan-out chain and `DISP_INTERRUPT_STATUS_CONTINUE*` registers, which map interrupt bits for OPTC/OTG timing events, DIG link events, HPD/AUX/DDC/I2C, DMCU/ABM, writeback scaler and MCIF writeback conditions, audio, power-gating, DCFE/DCFCLK, hub/read-client stalls, and DC perfmon conditions.
- Writeback converter (`CNV0`/`CNV1`) controls for capture enable, frame rate, cropping/window size, stereo/interlace selection, update lock/taken/pending state, source size, color-space conversion matrices, rounding offsets, clamps, CRC test readback, input pipe/source selection, soft reset, and warm-up configuration.
- Writeback scaler (`WBSCL0`/`WBSCL1`) fields for coefficient RAM access, tap programming, mode, destination size, horizontal/vertical scale ratios and filter initials, rounding/clamp, overflow and coefficient-conflict status, outside-pixel strategy, CRC testing, backpressure counters, and RAM shutdown.
- Writeback perfmon blocks (`DC_PERFMON3` and `DC_PERFMON4`) for performance counter selection, trigger/reference/clear behavior, state snapshots, counter valid/overflow/testbus mux fields, and high/low counter values.
- MCIF writeback buffer-manager fields for WB0 and the start of WB1, including buffer-manager enable/locks/interrupts, VMID and address fencing, current-line readback, current/next buffer status, luma/chroma pitch, four buffer status/status2 registers, arbitration, SCLK/watermark acknowledgment, buffer addresses and offsets, VCE control, p-state watermark/control, clock gating, warm-up, self-refresh, QoS, and luma/chroma buffer sizes.

## Important Macro Families

The GPU timer tail at lines 4918-4943 provides timer read and read-control fields. `DC_GPU_TIMER_READ` exposes a full 32-bit timer value, while `DC_GPU_TIMER_READ_CNTL` selects a read source and includes per-pipe VSYNC_NOM start-position fields. The first eight lines are a chunk-boundary continuation of `DC_GPU_TIMER_START_POSITION_VSTARTUP`; the shifts for D1-D4 appear before this slice.

The interrupt chain begins at line 4944 with `DISP_INTERRUPT_STATUS` and continues through `DISP_INTERRUPT_STATUS_CONTINUE22` at line 5748. It is structured as one root status register plus continuation registers linked by `DISP_INTERRUPT_STATUS_CONTINUE*` bits. The field groups cover:

- Pipe/timing-generator events such as `OPTCn_DATA_UNDERFLOW_INTERRUPT`, OTG immediate hardware cursor/event triggers, VSYNC_NOM, vertical interrupts, external timing sync and sync-loss.
- Link and connector events such as `DIGA`-`DIGF` fast training completion, video stream disable, HPD1-HPD6, HPD RX, AUX SW/LS done, and DDC/I2C completion.
- Display microcontroller/backlight events such as DMCU internal interrupt and ABM ready/update interrupts.
- Writeback and scaler events such as WBSCL host conflict/data overflow and MCIF writeback VCE/software/slice/overrun interrupts.
- System/display fabric events such as p-state response, power-gating response, DCFCLK watermark, DCFE and hub/read-client underflow/overflow/stall conditions, and perfmon events.

The writeback converter blocks begin at line 5861 for `CNV0` and line 6324 for `CNV1`. The two instances are parallel: each has `WB_ENABLE`, extensive `WB_EC_CONFIG` clock/memory power fields, `CNV_MODE`, window start/size, update state, source size, CSC control and matrix coefficients, clamp/rounding fields, CRC test controls/readback, input selection, soft reset, and warm-up controls.

The writeback scaler blocks begin at line 6046 for `WBSCL0` and line 6509 for `WBSCL1`. Important fields include coefficient RAM index/write enables, tap data, scaler mode and tap counts, destination dimensions, fixed-point horizontal/vertical ratios, initial phases for Y/RGB and CbCr, rounding/clamp, overflow status, coefficient RAM conflict status, outside-pixel strategy, CRC test fields, backpressure counter enable/value, and RAM shutdown control.

The perfmon blocks begin at line 6186 for `DC_PERFMON3` and line 6649 for `DC_PERFMON4`. Their counters expose enable/reset/clear/start controls, counter source selection, trigger/reference selection, counter ID, testbus mux, paired state readback, valid and overflow status, C-value interrupt fields, and high/low counter words. These are instance-specific performance monitor macros for writeback-related display paths.

The MCIF writeback section begins at line 6787 for `MCIF_WB0` and line 7092 for `MCIF_WB1`. `MCIF_WB0` is nearly complete in this slice, while `MCIF_WB1` is only partially included. Repeated buffer status registers for buffers 1-4 report active/locked/overflow/disabled/mode/buftag/next-buffer/field/current-line and long-line/short-line/frame-length errors; the companion `STATUS2` registers hold right-eye/current-line, new-content, color-depth, and Y/C overrun fields.

## APIs, Types, and Functions

There are no callable APIs, type definitions, enums, or functions in this region. The macros themselves are the hardware-facing API contract:

- `*_SHIFT` constants define the bit offset for a field within the MMIO register value.
- `*_MASK` constants define the already-shifted mask used by register helper macros to test, clear, or update a field.
- Address-block comments identify which generated register namespace the following definitions belong to, such as `dce_dc_wb0_dispdec_cnv_dispdec`, `dce_dc_wb1_dispdec_wbscl_dispdec`, and `dce_dc_mmhubbub_mcif_wb0_dispdec`.

These constants are normally paired with register offset macros from the companion DCN 1.0 offset header and with AMD display register helpers that perform read/modify/write operations.

## Control Flow

This header has no intrinsic runtime control flow. The operational flow is imposed by the display driver code that consumes the macros:

1. The caller chooses a DCN 1.0 register offset for timer, interrupt, writeback converter/scaler, perfmon, or MCIF writeback hardware.
2. The caller reads a register, prepares a value, or handles an interrupt/status readback.
3. The caller applies the appropriate `*_MASK` and `*_SHIFT` macros to isolate a field, pack a value, acknowledge an event, or preserve unrelated bits during a register update.
4. The hardware block consumes the updated state at its own synchronization point, such as a writeback update lock/taken transition, scaler coefficient load, MCIF buffer-manager lock, perfmon start/clear, or interrupt acknowledgment.

Several macro groups imply important runtime sequencing even though they do not implement it. `CNV*_CNV_UPDATE` has lock/pending/taken fields and should be coordinated with writeback programming. Coefficient RAM programming in `WBSCL*_WBSCL_COEF_RAM_SELECT` and `WBSCL*_WBSCL_COEF_RAM_TAP_DATA` requires ordered access to the selected tap pair. MCIF buffer-manager SW control has lock, interrupt enable/ack, VMID, and address fence fields that must be programmed coherently with buffer addresses and pitch/size.

## State and Persistence

The file stores no software state. It describes persistent hardware register state in DCN 1.0 display/writeback blocks. State represented by this chunk includes:

- Latched timer readback values and selected timer event positions.
- Interrupt status bits that persist until the corresponding hardware event is cleared or acknowledged by the proper status/control path.
- Writeback converter enable/mode/window/source/CSC/clamp/update state.
- Scaler coefficient RAM contents, scaling ratios, tap configuration, clamp/rounding behavior, overflow/conflict status, and CRC status.
- Perfmon counter configuration, active state, overflow/valid flags, and high/low counter values.
- MCIF writeback buffer-manager state: enabled buffers, locks held by software/VCE, current/next buffer selection, current line, buffer tags, line/frame errors, luma/chroma addresses and sizes, watermark/p-state/clock-gating controls, QoS, self-refresh, and warm-up settings.

These values persist in hardware until modified by MMIO writes, reset, mode-set teardown, power-management transitions, or firmware/hardware initialization. Status and interrupt fields may be clear-on-read, write-one-to-clear, or cleared through companion control registers depending on the underlying block; this generated header only gives bit positions and masks, not side-effect semantics.

## Dependencies and Integration Points

This chunk depends only on the C preprocessor and on inclusion in the generated DCN 1.0 ASIC register header set. It integrates with:

- Companion DCN 1.0 register offset definitions, typically `dcn_1_0_offset.h`, that provide the MMIO addresses for these masks.
- AMDGPU Display Core and DCN 1.0 resource, interrupt, timing, writeback, and hardware-sequencer code that programs the same registers through common register helper macros.
- IRQ handling code that uses `DISP_INTERRUPT_STATUS` and continuation bits to discover and service display events across multiple display pipes, link encoders, HPD/AUX/DDC paths, writeback blocks, and perfmon.
- Writeback pipeline code that configures `CNV*`, `WBSCL*`, and `MCIF_WB*` registers for display capture, scaling, color conversion, and memory writeout.
- Power-management and watermark code that consumes MCIF p-state, SCLK-change, self-refresh, and clock-gating fields.
- Diagnostic and validation paths that use CRC test registers, perfmon counters, underflow/overflow status, current-line fields, and buffer error flags.

The repeated `CNV0`/`CNV1`, `WBSCL0`/`WBSCL1`, `DC_PERFMON3`/`DC_PERFMON4`, and `MCIF_WB0`/`MCIF_WB1` naming establishes an instance mapping. Callers must not mix instance-specific offset macros with the wrong instance-specific shift/mask macros.

## Risks

The primary risk is silent hardware misprogramming. A wrong mask or shift compiles cleanly but can corrupt adjacent fields in display timing, interrupt routing, writeback memory programming, scaler coefficients, or perfmon control.

Interrupt fields are especially sensitive because this chunk contains a long chained status register map. Misinterpreting a continuation bit as a normal event, or failing to follow the chain to later `DISP_INTERRUPT_STATUS_CONTINUE*` registers, can lose interrupts. Conversely, acknowledging the wrong bit can clear unrelated display events such as HPD/AUX, OTG vertical interrupts, underflow, MCIF overrun, or perfmon status.

Writeback register programming has synchronization hazards. `CNV*_CNV_UPDATE` lock/taken/pending fields, scaler coefficient RAM selection/write-enable fields, and MCIF buffer-manager locks need ordered updates. Programming addresses, pitch, size, or CSC/scaler fields while capture is active can produce corrupted frames, memory writes to unexpected locations, line-length errors, or stale content.

MCIF fields carry memory-safety consequences. VMID, address fence, buffer address, luma/chroma offset, pitch, size, and current/next-buffer fields define where hardware writes captured frames. Incorrect values can cause writeback to target the wrong GPU virtual address range or overrun an allocated buffer.

Power-management fields can create display-visible or capture-visible failures. SCLK-change acknowledgment, p-state watermark, self-refresh, clock-gating, and RAM power state controls interact with writeback latency. Bad programming may show up as writeback underrun/overrun, corrupted captures, or stalls under clock changes.

This chunk has two merge-boundary risks: it starts mid-register at `DC_GPU_TIMER_START_POSITION_VSTARTUP`, and it ends immediately after the `MCIF_WB1_MCIF_WB_BUF_1_ADDR_C_OFFSET` comment. The reconciliation lane should merge adjacent chunks so those partial register definitions are not treated as complete standalone sections.

## Test Signals

Useful validation signals include:

- Build coverage for translation units that include `dcn_1_0_sh_mask.h`, catching duplicate names, malformed macros, or missing continuation from adjacent chunks.
- Generated-header consistency checks that every field has matching `__SHIFT` and `_MASK` constants, masks align with shifts, and repeated instance blocks (`CNV0`/`CNV1`, `WBSCL0`/`WBSCL1`, `MCIF_WB0`/`MCIF_WB1`) remain structurally consistent.
- Diff checks against AMD's authoritative DCN 1.0 register database and neighboring ASIC-generation headers for stable field layouts.
- IRQ smoke tests that trigger or emulate HPD/AUX/DDC, OTG vertical, underflow, writeback overflow, MCIF overrun, DMCU/ABM, and perfmon interrupts and verify the chained `DISP_INTERRUPT_STATUS_CONTINUE*` walk.
- Writeback functional tests that enable capture, program CNV window/source/CSC, program WBSCL ratios/coefficients, route input pipe/source selection, and verify output frames through CRC/readback or memory comparison.
- MCIF writeback tests that exercise buffer rotation across buffers 1-4, SW/VCE locks, address fencing, luma/chroma offsets, pitch/size, current-line status, overrun and line/frame error reporting.
- Power-management and watermark tests that run writeback while changing clocks/p-states and inspect `MCIF_WB*_SCLK_CHANGE`, watermark/p-state controls, and overflow/stall signals.
- Perfmon tests that start, clear, and read `DC_PERFMON3`/`DC_PERFMON4` counters, verifying valid/overflow flags and high/low counter values.

## Cross-Chunk Notes

This is a middle slice of a generated DCN 1.0 shift/mask header. The final per-file research document should merge it with the preceding GPU timer definitions and the following MCIF_WB1 address/control continuation. Treat the chunk as a register-map segment spanning display interrupts and writeback hardware, not as a standalone source module with local control flow.
