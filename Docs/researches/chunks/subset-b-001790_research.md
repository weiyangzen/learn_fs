# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 22117-24606

## Purpose

This chunk is generated AMD DCN 3.0.3 register field metadata. It contains no executable C logic; it publishes preprocessor constants for bit shifts and bit masks used to read, write, and update fields inside memory-mapped display-controller registers.

The requested range starts at the tail of `DC_GPIO_RXEN`, then covers `DC_GPIO_PULLUPEN`, AUX/DDC pad controls, DSC instance 0 and 1 field definitions, DSC-local performance monitor blocks, display writeback `DWB0` capture/color/gamma fields, MPCC instance 0 and 1 blending controls, and the beginning of `MPCC_OGAM0` output-gamma RAM field definitions. It is the companion style of header to a DCN offset header: consuming code combines register offsets from an `*_offset.h` file with the `__SHIFT` and `_MASK` constants here to safely pack and extract fields.

Although this source path is under a local `ceph-client` mirror, the content is AMDGPU display-driver hardware metadata. It is unrelated to Ceph filesystem protocol behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locking primitives in this range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position of a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that same field.

Major macro families in this slice:

- `DC_GPIO_*`: GPIO input-enable tail, pull-up enable fields for generic GPIOs, sync pins, HPD pins, backlight/panel signals, plus AUX termination, DP/DN swap, hysteresis tuning, AUX drive/control, AUX voltage-output tuning, DDC pad I2C mode, 1.2 V enable, pad I2C control, and AUX/I2C PHY power-good status.
- `DSC_TOP0` and `DSC_TOP1`: DSC clock enable, clock-gating disables, debug enable, and test-clock mux fields.
- `DSCCIF0` and `DSCCIF1`: DSC client-interface configuration for underflow recovery/interrupt/status, input pixel format, bits per component, double-buffer update pending, picture width, and picture height.
- `DSCC0` and `DSCC1`: DSC compressor configuration, status, interrupt/status bits, picture parameter set fields, memory power control, squared-error and maximum-absolute-error counters, rate-buffer fullness counters, and debug-bus rotate fields.
- `DC_PERFMON12`, `DC_PERFMON13`, and `DC_PERFMON14`: local display perfmon counter control, counter source/type/mode selection, hardware start/stop/counter-off selection, counter state, report count, interrupt status/ack, high/low counter values, and read selectors.
- `DWB_*` and `FC_*`: display writeback enable/clock/memory power, frame capture enable/rate/crop/eye selection/new-content state, source/window geometry, update lock/pending, CRC control/masks/values, output format/denorm/min/max, MMHUBBUB backpressure counters, host-read control, overflow status/counters, and soft reset.
- `DWB_GAMUT_REMAP*` and `DWB_OGAM*`: writeback color-processing fields, including gamut-remap mode/format and two coefficient matrices, output gamma mode/select/current state, LUT index/data/control, and RAM A/B piecewise-linear region start/end/base/slope/offset/segment fields.
- `MPCC0` and `MPCC1`: MPC compositor control fields for top/bottom mux selection, OPP ID, alpha/blend/overlap flags, stereo/field controls, shared-mem controls, update lock selection, top/bottom gains, background color channels, memory power, and status/current mux values.
- `MPCC_OGAM0`: MPCC output-gamma mode/select/current state, LUT access fields, RAM A piecewise-linear region programming for regions 0 through 33, and the beginning of RAM B start/end field definitions through `MPCC_OGAM0_MPCC_OGAM_RAMB_END_CNTL2_R`.

The macros are intentionally untyped `#define` constants. Type safety, volatile MMIO access, field value range checks, and read-modify-write behavior are supplied by the AMD display register helper layers that include this file.

## Control Flow

This header has no runtime control flow. Runtime sequencing is provided by AMDGPU display code:

1. DCN 3.0.3 resource, GPIO, DSC, DWB, MPC, and DMUB paths include this shift/mask header with the matching offset header.
2. Register-list macros paste register and field names into helper macros such as `REG_UPDATE`, `REG_SET`, `REG_GET`, `REG_SET_2`, and block-specific `SRI`/`SR` register-table initializers.
3. Consumers use the `__SHIFT` and `_MASK` pairs to encode values into 32-bit MMIO writes or decode status/counter fields from 32-bit MMIO reads.
4. Driver control flow around those accesses handles clocks, power gating, double-buffer update locks, status polling, interrupt acknowledgement, modeset ordering, and suspend/resume restoration.

The macros themselves do not encode ordering. For example, DSC PPS fields must be programmed in the compressor's expected sequence, DWB gamma/LUT and gamut-remap fields must follow writeback pipeline update rules, and MPCC blending fields must be coordinated with MPC update locks and pipe topology.

## State And Persistence Behavior

The chunk stores no software state and persists nothing to disk. It describes hardware state held in DCN 3.0.3 display registers.

State represented by this chunk includes:

- Pad and GPIO configuration for pull-ups, HPD-related pins, panel/backlight-related pins, AUX termination/swap/tuning/control, DDC I2C behavior, voltage enables, and AUX/I2C PHY power-good reporting.
- DSC top/client/compressor state for clocking, input format, picture size, slice configuration, PPS payload programming, buffer thresholds, quantization parameter ranges, BPG offsets, memory low-power policy, interrupt/status bits, rate-buffer fullness, and compression error metrics.
- Perfmon state for DSC and writeback blocks, including event source selection, counter mode, active status, run start/stop selection, counter-off conditions, interrupt status/ack, and high/low counter values.
- DWB state for capture enable/rate/window/source geometry, CRC generation, output format, host readback, overflow tracking, MMHUBBUB backpressure accounting, memory power, soft reset, gamut remap, and output gamma RAM/LUT contents.
- MPCC and MPCC OGAM state for compositor routing, blend/alpha behavior, background color, update lock, memory power, active mux/status reporting, and output gamma piecewise-linear RAM contents.

Persistence is hardware-defined. Configuration fields usually survive until the block is reprogrammed, gated, reset, or the GPU enters a suspend/reset path. Status, interrupt, counter, update-pending, current-state, and power-state fields may be read-only, sticky, write-one-to-clear, self-clearing, or transient. This generated header does not indicate access type; consumers must rely on hardware programming guides and existing AMD display block code.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.0.3 register database and must match the companion register-offset namespace for the same ASIC generation:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_offset.h`
- sibling DCN shift/mask headers used for comparison or related ASIC variants, such as `dcn_3_0_0_sh_mask.h` and nearby DCN 3.x headers
- AMD display register helper macros that expect `__SHIFT` and `_MASK` names generated from register and field tokens

Likely integration points in the AMD display tree include:

- GPIO and link/pad code that programs `DC_GPIO_*`, AUX, DDC, HPD, panel-power, and backlight-related fields.
- DSC resource and encoder code that writes `DSC_TOP*`, `DSCCIF*`, and `DSCC*` fields when enabling DSC for high-bandwidth DisplayPort/eDP modes.
- IRQ/status code that reads and acknowledges DSCC underflow, overflow, and rate-control-buffer status bits.
- DWB/writeback code that configures frame capture, crop/source geometry, output format, CRC, overflow handling, host readback, color transforms, and writeback output gamma.
- MPC/MPCC code that sets MPCC source selection, OPP routing, alpha/blending controls, gains, background color, update locks, memory power, and MPCC OGAM LUT/RAM fields.
- Debug/perf paths that configure `DC_PERFMON12`, `DC_PERFMON13`, and `DC_PERFMON14` counters for DSC and writeback diagnostics.

The primary integration contract is name stability. A register helper can only build field operations if the generated register and field tokens match the offset header, register lists, and block-specific C code.

## Risks And Edge Cases

- Shift or mask drift is the main risk. These constants compile as ordinary numeric macros, so a wrong mask or shift can silently program the wrong bits in a real hardware register.
- Copy-family errors are easy in repeated generated blocks. `DSCC0` and `DSCC1`, `DC_PERFMON12` through `14`, `MPCC0` and `MPCC1`, and RAM A/B gamma region families are structurally similar but instance-specific.
- Some fields span nearly the whole register, such as 32-bit error counters or LUT data, while others are narrow single-bit controls. Incorrect field width can truncate values, leak neighboring fields, or break read-modify-write preservation.
- Status and interrupt fields require correct access semantics. Treating sticky or write-one-to-clear bits like ordinary writable configuration can lose diagnostics or leave interrupts asserted.
- DSC PPS fields are bandwidth and format critical. Bad masks for `BITS_PER_PIXEL`, slice geometry, RC model sizes, buffer thresholds, QP ranges, or BPG offsets can produce visual corruption, link failures, or failures only on DSC-enabled panels.
- DWB and OGAM LUT/RAM fields are stateful programming surfaces. Incorrect index/data/control or region start/end/slope/base masks can corrupt captured frames, CRC validation, color conversion, or gamma output.
- MPCC blend/routing fields affect pipe composition. A bad source selection, OPP ID, alpha mode, gain, or update lock field can cause blank planes, wrong z-order, stale updates, or pipe-specific artifacts.
- GPIO/AUX/DDC pad fields interact with external electrical behavior. Wrong pull-up, termination, voltage, swap, or I2C mode masks can cause hotplug, EDID, AUX, panel, or backlight issues that are board-specific.
- The chunk boundary is artificial. It starts after earlier `DC_GPIO_RXEN` shift definitions and stops inside `MPCC_OGAM0` RAM B definitions; the final file report must merge adjacent chunks before making whole-header claims.

## Test Signals

Useful validation combines generated-header consistency checks and hardware behavior:

- Build AMDGPU/DC with the DCN 3.0.3 paths enabled; missing or renamed field macros should fail where register tables and helper macros reference them.
- Mechanically verify that each visible `__SHIFT` macro in lines 22117-24606 has the expected matching `_MASK` macro for the same register/field, and that repeated instance blocks preserve intended symmetry between `DSCC0`/`DSCC1`, `MPCC0`/`MPCC1`, perfmon instances, and RAM A/B region families.
- Compare this chunk against AMD's authoritative generated DCN 3.0.3 register headers and adjacent DCN 3.x variants to detect accidental drift in bit positions or masks.
- Exercise hotplug, EDID/DDC reads, AUX DPCD transactions, panel power, backlight, suspend/resume, and low-power wake on boards using the affected GPIO/AUX/DDC pads.
- Enable DSC on capable DisplayPort/eDP panels across multiple formats, slice layouts, and bandwidth pressure points; monitor for visual corruption, link training failures, DSCC underflow/overflow/rate-control-buffer status, and error-counter changes.
- Exercise writeback/frame capture paths with crop windows, different source sizes, output formats, CRC capture, host readback, overflow/backpressure monitoring, gamut remap, and output gamma programming.
- Test compositor paths using MPCC instances 0 and 1 with plane blending, alpha, stereo/field settings, background color, update locks, memory power transitions, and output gamma programming.
- Use perfmon/debug paths to read DSC and DWB counter values and interrupt status/ack behavior, checking for stuck counters, invalid high/low reads, or unexpected active-state behavior.
- Watch kernel logs and display diagnostics for AUX timeouts, hotplug storms, DSC PPS failures, writeback overflow, CRC mismatches, stuck interrupts, color/gamma regressions, blank planes, and resume-only failures.

## Cross-Chunk Notes

Earlier chunks own the start of the GPIO and DCIO shift/mask namespace, including the beginning of `DC_GPIO_RXEN`. Later chunks continue `MPCC_OGAM0` RAM B fields and the rest of the DCN 3.0.3 shift/mask register map. This document is only the worker-produced research for `subset-b-001790`; the final per-file research document should merge it with all other chunks for `dcn_3_0_3_sh_mask.h`.
