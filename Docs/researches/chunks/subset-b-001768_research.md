# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 41908-44291

## Scope And Purpose

This chunk is a generated register shift/mask section for AMD Display Core Next 3.0.2 (`dcn_3_0_2`). It does not implement executable control flow; instead it defines C preprocessor constants that describe bit positions and bit masks for memory-mapped display hardware registers. The constants are consumed by AMDGPU display code through register descriptor tables and helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, and per-block field-list macros that bind `__SHIFT` and `_MASK` values into typed register access structures.

The requested slice starts in the middle of the DP4 register block, with the last visible mask for `DP4_DP_MSE_SAT0`, and continues through complete blocks for DP4 secondary data packets, DCIO, GPIO/pad controls, DSC0 encoder and perfmon registers, then reaches the beginning of the DSC1 encoder block and ends mid-register in `DSCC1_DSCC_INTERRUPT_CONTROL_STATUS`. The surrounding header-level purpose is to provide the hardware contract for DCN 3.0.2 register programming: callers use these definitions to pack field values into 32-bit register writes and unpack status fields from 32-bit register reads without hard-coding shifts or masks at each call site.

## Register Families Covered

The DP4 section covers DisplayPort stream/link encoder fields for a fourth DP instance. It includes MST stream allocation table registers (`DP4_DP_MSE_SAT1`, `SAT2`, update/status registers, link timing, and misc control), Main Stream Attribute timing parameters (`DP_MSA_TIMING_PARAM1` through `PARAM4`), Multi-Stream Operation controls (`DP_MSO_CNTL`, `CNTL1`), DSC-over-DP controls (`DP_DSC_CNTL`, `DP_DSC_BYTES_PER_PIXEL`), secondary packet controls (`DP_SEC_CNTL2` through `CNTL7`), double-buffer control (`DP_DB_CNTL`), VBID override fields (`DP_MSA_VBID_MISC`), metadata transmission, ALPM link power management, and GSP8 through GSP11 packet controls. These fields support DisplayPort MST/MSO scheduling, secondary data packet timing, audio/video metadata delivery, DSC payload signalling, double-buffered update handshakes, and low-power link transitions.

The DCIO display-decoder block starts at `dce_dc_dcio_dcio_dispdec`. It defines generic clock/test output selectors (`DC_GENERICA`, `DC_GENERICB`), clock gating (`DCIO_CLOCK_CNTL`), reference clock output selection (`DC_REF_CLK_CNTL`), UNIPHY link controls for PHY A through E, per-lane channel crossbar selection, write-command delays, pin strap readouts, LVTMA panel power sequencing, backlight PWM control, GSL/genlock and swaplock pad controls, and soft-reset bits for UNIPHY/DSYNC/DCRXPHY/ZCAL paths. These masks are used when the display resource layer creates and programs link encoders, panel controls, clock sources, and output PHY state.

The DCIO chip-level GPIO block starts at `dce_dc_dcio_dcio_chip_dispdec`. It describes generic GPIO pads, DDC/AUX pads, VGA DDC, genlock, hot-plug detect, panel power-sequence pads, pad-strength registers, AUX PHY tuning/control, TX/RX enables, pullups, and power-good status. Register naming follows a repeated pattern: `_MASK` registers select pad ownership and pull-down or receive behavior, `_A` registers expose input/sample values, `_EN` registers control output enable, and `_Y` registers drive output values. DDC1 through DDC5 and DDCVGA are represented as clock/data pairs; HPD exposes six hot-plug detect pins; AUX controls expose termination, polarity, hysteresis, voltage/output drive tuning, I2C mode, and per-pad power state.

The DSC0 section spans three address blocks: `dce_dc_dsc0_dispdec_dsc_top_dispdec`, `dce_dc_dsc0_dispdec_dsccif_dispdec`, and `dce_dc_dsc0_dispdec_dscc_dispdec`. It defines top-level DSC clock/debug controls, DSCC input interface configuration, core DSC encoder configuration, interrupt/status bits for rate-buffer and rate-control-buffer events, PPS configuration registers `DSCC0_DSCC_PPS_CONFIG0` through `CONFIG22`, memory power controls, error counters, buffer fullness monitors, and debug bus rotation. These fields map closely to Display Stream Compression PPS and rate-control concepts: version, bits per component/pixel, picture and slice dimensions, initial delays, scale intervals, BPG offsets, model size, quantization limits, buffer thresholds, and range parameters.

The `DC_PERFMON19` block is associated with the DSC0 display-decoder perfmon address block. It exposes eight performance counter controls, counter-state controls, top-level perfmon enable/state/report-count fields, count-off interrupt configuration, counter interrupt status/ack bits, and low/high readback fields. These masks support driver or debug tooling that selects internal DSC/display events, starts/stops counters by hardware signals, reads accumulated values, and acknowledges threshold interrupts.

The DSC1 section starts near the end of this chunk. It mirrors the top, DSCCIF, and early DSCC fields from DSC0 for a second DSC instance: top clock/debug controls, input interface config, picture dimensions, core slice/ICH config, rate-control model size, double-buffer pending status, and the beginning of rate-buffer/rate-control-buffer interrupt status and interrupt-enable masks. The chunk ends before the complete DSC1 PPS register set appears, so this document only covers the visible early DSC1 fields.

## Important APIs, Types, And Macro Contract

This file exports only preprocessor symbols. The important API contract is the naming convention:

- `REGISTER__FIELD__SHIFT` gives the bit position used when encoding or decoding a field.
- `REGISTER__FIELD_MASK` gives the field mask in the final 32-bit register value.
- Address-block comments group related registers by hardware block but do not affect compilation.

Higher-level AMD display code generally does not reference every constant directly. It uses macro lists in block-specific headers and resource constructors to initialize register structures. For DSC, headers such as `display/dc/dsc/dcn20/dcn20_dsc.h` declare field lists with `DSC_SF(..., mask_sh)`, then implementation files use `REG_SET_*`/`REG_UPDATE` helpers to program PPS and control fields. For DCN 3.0.2 specifically, `display/dc/resource/dcn302/dcn302_resource.c` includes this `dcn_3_0_2_sh_mask.h` together with the matching offset header, then creates DCN302 resource objects for stream encoders, DSC engines, AUX/I2C engines, link encoders, panel controls, and other display blocks.

The DP4 fields integrate with DIO/link encoder and stream encoder code that pairs these field masks with matching register offsets from `dcn_3_0_2_offset.h`. The GPIO fields integrate with GPIO factory and hardware abstractions for DDC, AUX, HPD, generic GPIO, genlock/swaplock, and panel power sequencing. The perfmon fields integrate with diagnostic counter paths rather than normal modesetting logic.

## Control Flow And Data Flow

There is no runtime control flow inside this chunk. Runtime behavior emerges when other driver code includes the header and calls register helper macros:

1. Resource construction selects the DCN302 offset and mask headers for the ASIC.
2. Block constructors build per-instance register address tables and shift/mask tables.
3. Modeset, link training, hotplug, panel, DSC, or diagnostics code calls typed helper functions.
4. Helper macros read or write memory-mapped registers, using the shift and mask constants to preserve unrelated bits and encode only the requested field.
5. Hardware latches or reports state through the corresponding register fields, including double-buffer pending bits, send-pending bits, interrupt status bits, power-sequence done bits, HPD samples, and counter readbacks.

Several groups represent hardware handshakes rather than simple configuration. DP secondary packet and GSP registers expose send, pending, active, deadline-missed, and send-in-idle bits. DP and DSC double-buffer fields expose pending/taken/update status. LVTMA power sequencing exposes target state, DIGON/SYNCEN/BLON, and done/state readbacks. Interrupt/status registers combine occurrence bits and interrupt-enable bits, and some companion control registers contain ack/clear fields in nearby chunks or related blocks.

## State And Persistence Behavior

The macros themselves carry no mutable state, but the hardware registers they describe are persistent device state until overwritten, reset, power-gated, or reinitialized by modeset sequences. Important state categories in this chunk include:

- Link and stream state: DP4 MST slot allocation, MSA timing, MSO packet enable masks, secondary packet scheduling, DSC payload fields, VBID overrides, metadata packet timing, and ALPM requests persist in the DP encoder until reprogrammed.
- Pad and PHY state: UNIPHY lane inversion/crossbar/link-enable fields, DCIO soft resets, AUX/DDC pad tuning, RX/pullup/TX enables, and GPIO output values persist as hardware pad configuration and directly affect connector behavior.
- Panel state: LVTMA power-sequence and backlight PWM fields persist across display enable/disable transitions until the panel control code changes them or a reset occurs.
- DSC state: PPS, picture/slice dimensions, rate-control parameters, input format, memory power settings, and interrupt enables persist inside each DSC instance. Double-buffer pending fields indicate when hardware has accepted or is still waiting to apply a programmed state.
- Diagnostic state: `DC_PERFMON19` counter selections, counter states, interrupt status/ack, and accumulated high/low values persist until the perfmon is stopped, cleared, acknowledged, or the block is reset.

Because these are low-level MMIO definitions, persistence semantics are hardware-defined. The driver must sequence writes around vblank, double-buffer update windows, power state, and link training state; the header only supplies bit positions.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.0.2 register offset header for actual addresses. A shift/mask constant is not useful unless paired with the corresponding `mm...` register offset and base index. It also depends on AMD display register-access infrastructure, including generated register structs, `REG_*` helper macros, DC context MMIO accessors, and per-block field descriptor arrays.

Major integration points are:

- `display/dc/resource/dcn302/dcn302_resource.c`, which includes this header and wires DCN302 resources to the proper register/mask tables.
- DSC block code under `display/dc/dsc/`, which programs DSC top, DSCCIF, DSCC, PPS, memory power, and status fields using field-list macros and register helpers.
- DIO/link encoder and stream encoder code, which uses DP stream/link fields for MSA programming, secondary data packet scheduling, MST/MSO behavior, DSC-over-DP signalling, and link power management.
- GPIO and AUX/I2C hardware factories, which use GPIO, DDC, AUX, HPD, and generic pad fields for connector detection, EDID/DDC access, AUX transactions, and board-specific pin programming.
- Panel control and power-sequence code, which uses LVTMA and backlight PWM fields to control embedded-panel power rails, sync enable, digital enable, and brightness output.
- Debug/performance tooling paths, which use `DC_PERFMON19` field selections and readback registers to observe display-block activity.

The source path is under `drivers/gpu/drm/amd/include/asic_reg/dcn`, so it is part of the Linux AMDGPU display hardware definition layer. Changes here have broad compile-time reach because many resource constructors and hardware blocks include the ASIC-specific generated headers.

## Risks And Edge Cases

The primary risk is incorrect bit layout. A wrong shift or mask can silently write the wrong hardware field, preserve stale bits, clear adjacent fields, or decode status incorrectly. In this chunk, that risk affects high-impact display behavior: connector detection, AUX/DDC access, DP MST allocation, DSC bitstream validity, link power management, panel/backlight sequencing, and interrupt handling.

Generated-header consistency is critical. The same field name must match between offset headers, mask headers, register-list macros, and implementation code. Renaming or dropping a field can break compilation where `*_SF(..., mask_sh)` expands to missing symbols. Keeping a stale mask while hardware changed the register layout can compile cleanly but fail only on affected ASICs or connector configurations.

The chunk contains repeated per-instance patterns. DP4 fields mirror other DP instances, UNIPHY A-E fields share the same layout, DDC1-DDC5 fields repeat, HPD1-HPD6 fields repeat, and DSC0/DSC1 fields mirror each other. Copy-generation errors are plausible: an instance number may be wrong, a mask may use another instance's field width, or a later instance may have a truncated field set. The visible `DSC_TOP1_DSC_DEBUG_CONTROL` block has `DSC_DBG_EN_MASK` in this chunk while its `DSC_TEST_CLOCK_MUX_SEL_MASK` appears outside the visible range or is absent here, so consumers must rely on the full file rather than this chunk alone for final completeness.

Several fields represent status, pending, ack, or interrupt-enable semantics. Treating a status bit like a writable config bit, writing ack bits without preserving enables, or enabling interrupts before clearing old occurrence bits can cause lost events or interrupt storms. Similarly, double-buffer and vblank-timed fields must be updated in the correct display timing window; the masks do not enforce ordering.

Power and pad controls are especially sensitive. Incorrect LVTMA power sequencing can blank or flicker panels. Incorrect GPIO/AUX/DDC pad tuning can break EDID reads, HPD detection, or AUX link training. Incorrect UNIPHY reset/crossbar/channel inversion fields can prevent link bring-up or produce lane mapping issues that appear as link-training failures rather than obvious register programming bugs.

DSC PPS fields must match the negotiated DSC stream parameters. Incorrect bit packing for picture size, slice size, bits per pixel/component, rate-control model, or range parameters can produce sink decode failures, visual corruption, underflow/overflow status, or fallback to uncompressed modes. The error counters and buffer fullness fields in this chunk are useful for diagnosing those failures, but only if their masks remain correct.

## Test Signals

There are no direct unit tests for this generated header in the chunk. Useful validation signals come from build coverage, hardware bring-up, display conformance behavior, and register readback:

- Compile tests should catch missing or renamed macros when DCN302 resources, DSC, DIO, GPIO, panel, or perfmon code expands register field lists.
- Display smoke tests should verify monitor detection, EDID reads, HPD interrupts, DP link training, MST/MSO topologies, secondary packet delivery, audio/metadata delivery, panel power-up/down, and backlight control on DCN 3.0.2 hardware.
- DSC-specific tests should exercise DSC enable/disable, compressed stream negotiation, multiple slice sizes, 8/10/12 bpc formats where supported, MST with DSC, and readback of underflow/overflow/error counters.
- GPIO/AUX/DDC tests should check all connector instances, including DDC1-DDC5, AUX1-AUX6, HPD1-HPD6, DDCVGA, and boards that use LVTMA/panel power sequencing.
- Perfmon/debug tests should configure `DC_PERFMON19` counters, start/stop them through hardware selectors, read low/high values, trigger count-off interrupts, and verify status/ack behavior.
- Register readback tracing is a strong regression signal: programmed field values should round-trip through the same shift/mask definitions, and unrelated bits in the same register should remain unchanged after `REG_UPDATE` operations.

For generated register headers, a high-value maintenance check is comparing this file against the vendor register database or adjacent ASIC versions. Repeated field families should be mechanically diffed for expected instance-number substitutions and deliberate generation differences, especially around DP4, DSC0/DSC1, GPIO instance groups, and perfmon field widths.
