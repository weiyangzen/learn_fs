# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 35423-37642

## Scope And Purpose

This chunk is part of AMD's generated DCN 3.5.1 register shift/mask header. It contains preprocessor constants for hardware register bitfields, not executable driver logic. Callers use these `__SHIFT` and `_MASK` definitions with the matching `dcn_3_5_1_offset.h` address header and AMD display register helpers to pack, update, and extract fields in memory-mapped DCN display registers.

The requested range contains 2,217 `#define` lines: 1,107 shift macros and 1,110 mask macros. The imbalance is caused by chunk boundaries. The range starts inside the mask tail of `DC_GPIO_AUX_CTRL_1`, after that register's shift lines and earlier masks, and ends inside `DC_PERFMON19_PERFCOUNTER_CNTL`, before its remaining masks and following perfmon registers. There are no source comments in this span.

The substantive hardware covered here is the DCN 3.5.1 display I/O, panel power sequencing, Display Stream Compression, and adjacent performance-monitor programming surface:

- GPIO/AUX/DDC/HPD electrical controls for AUX and hot-plug related pins.
- DC GPIO receive-enable and pull-up-enable fields for generic, sync, genlock, swaplock, and HPD pins.
- AUX/I2C pad power-good status.
- DCIO UNIPHY reserved macro-control words for UNIPHY instances 1 through 4.
- Two panel power sequencer instances, including panel GPIO ownership, panel timing, backlight PWM, reference dividers, and register locking.
- DSC top control, DSCC input interface, DSCC core configuration, PPS programming, memory power, error statistics, buffer fullness telemetry, and debug fields for DSC instances 0 through 2.
- DC performance monitor instances 17 and 18, plus the beginning of instance 19.

## Important Constants And Register Areas

The GPIO/AUX section finishes `DC_GPIO_AUX_CTRL_1` masks for I2C resistor bias, AUX comparator select, DDC/VGA spare and slew/rx select, per-AUX comparator select, and DDC/VGA comparator selection. `DC_GPIO_AUX_CTRL_2` defines HPD fall slew selection, spike filter enables/selectors, 0.9 V and 1.1 V HPD capacitor/resistor selections, HPD bias current enable, slew, resistor bias, and comparator select fields. `DC_GPIO_AUX_CTRL_3` covers AUX termination disable, DP/DN swap, and hysteresis tuning for AUX1 through AUX6. `DC_GPIO_AUX_CTRL_4` and `DC_GPIO_AUX_CTRL_5` expose per-AUX analog control nibbles and bias/impedance calibration controls.

`DC_GPIO_RXEN` and `DC_GPIO_PULLUPEN` expose one-bit receive-enable and pull-up-enable controls for generic GPIO A through G, HSYNC/VSYNC A, genlock clock/vsync, swaplock A/B, and HPD1 through HPD6. `AUXI2C_PAD_ALL_PWR_OK` provides per-AUX and DDC/VGA pad power-good status, which is useful as a precondition/readback signal for AUX/I2C access.

The `DCIO_UNIPHY{1,2,3,4}_UNIPHY_MACRO_CNTL_RESERVED{0..57}` definitions map each reserved macro-control register as a full 32-bit field. These are intentionally opaque in the generated header: they preserve addressable fields from the hardware register database without assigning semantic subfields in this chunk.

`PWRSEQ0_*` and `PWRSEQ1_*` repeat the same panel power sequencing register layout for two instances. They include GPIO enables for variable backlight, DIGON, and BLON; receive and pull-up enables; GPIO masks, pull-down disables, receiver selections, and A/Y state bits; panel target-state, sync, digital-on, and backlight-on controls with override and polarity bits; state readbacks; power-up and power-down delay registers; panel and PWM reference dividers; PWM active count, fractional enable, frame-start update recognition, enable state; post-frame-start update delays; PWM period and bit count; group-one register lock/update-pending/update-at-frame-start/readback controls; and spare full-width fields.

The DSC/DSCC region is repeated for instances 0, 1, and 2. `DSC_TOP*_DSC_TOP_CONTROL` exposes DSC clock enable and DISPCLK/DSCCLK gate-disable bits. `DSCCIF*_DSCCIF_CONFIG0/1` configures the input interface with underflow recovery/status/interrupt enable, input pixel format, bits per component, double-buffer update-pending readback, and picture width/height. `DSCC*_DSCC_CONFIG0/1` covers slice layout, alternate ICH encoding, vertical slice count, and rate-control buffer model size; DCN 3.5.1 resource code supplies local definitions for an `ICH_RESET_AT_END_OF_LINE` field around this register family.

`DSCC*_DSCC_INTERRUPT_CONTROL_STATUS` packs rate-buffer overflow and underflow status bits for buffers 0 through 3, rate-control buffer model overflow status bits, and matching interrupt-enable bits. `DSCC*_DSCC_PPS_CONFIG0` through `DSCC*_DSCC_PPS_CONFIG22` carry the Display Stream Compression PPS fields: DSC version, PPS identifier, line-buffer depth, bits per component/pixel, VBR/simple-422/RGB/native-422/native-420/block-prediction modes, chunk size, picture and slice dimensions, initial transmit/decode delay, scale values and intervals, first/second-line BPG offsets, NFL/NSL/slice BPG offsets, initial/final offsets, flatness and RC model parameters, RC edge and quantization limits, target offsets, RC buffer thresholds 0 through 13, and range min/max QP plus range BPG offsets 0 through 14.

`DSCC*_DSCC_MEM_POWER_CONTROL` fields describe default low-power state, memory power force/disable/status, and native-422 memory power force/disable/status. The telemetry registers hold squared error lower/upper counters for R/Y, G/Cb, and B/Cr channels; max absolute error fields; max fullness levels for rate buffers 0 through 3; and max fullness levels for rate-control buffer models 0 through 3. Instance 0 additionally includes `DSCC0_DSCC_TEST_DEBUG_BUS_ROTATE`.

`DC_PERFMON17_*` and `DC_PERFMON18_*` are complete performance monitor instances in this chunk. They define counter event selection, counted-value selection, increment mode, hardware control selector, run-enable mode, count-off start disable, restart enable, interrupt enable, off mask, active status, counter select, count-off selection, counter state for counters 0 through 7, perfmon state/report count/count-off controls, perfmon count-off interrupt enable/status/ack, clock enable, run-enable start/stop selectors, per-counter interrupt status/ack, counter value high/low readback, and read selector fields. `DC_PERFMON19_PERFCOUNTER_CNTL` starts at the end of the chunk and is incomplete here.

## APIs, Types, And Functions

There are no functions, structs, enums, or inline helpers in this source range. The public interface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT` gives the bit position for packing or extracting a register field.
- `REGISTER__FIELD_MASK` gives the already-positioned field mask.
- Register names encode hardware block and instance, such as `PWRSEQ1_BL_PWM_CNTL`, `DSCC2_DSCC_PPS_CONFIG16`, or `DC_PERFMON18_PERFCOUNTER_STATE`.

The macros are consumed through register-list and field-list structures in the AMD display stack. For DCN 3.5.1, `display/dc/resource/dcn351/dcn351_resource.c` includes `dcn_3_5_1_offset.h` and this shift/mask header, then builds resource, AUX, UNIPHY, DSC, and other register tables. `display/dc/irq/dcn351/irq_service_dcn351.c` and `display/dmub/src/dmub_dcn351.c` also include this header for ASIC-specific register access.

The DSC fields integrate with common DCN DSC code through `display/dc/dsc/dcn35/dcn35_dsc.c`, inherited DSC register list macros, and generic DSC calculations in `display/dc/dsc/dc_dsc.c`. Panel power and backlight fields correspond to panel-control code patterns in the DC display stack, especially the `dce_panel_cntl` and DCN panel-control abstractions. AUX and UNIPHY fields feed link encoder, DIO, AUX/I2C, and DMUB-side register setup rather than direct ad hoc bit twiddling.

Semantic enum values are not defined here. Valid values for pixel formats, bits-per-component encodings, DSC PPS fields, HPD/AUX analog tuning, power states, perfmon event selectors, and run-control selectors must come from hardware documentation, generated enum data, or higher-level DCN code.

## Control Flow And Runtime Behavior

This header has no local control flow. Runtime behavior occurs when the display driver programs the hardware registers described by these masks during probe/resource construction, link bring-up, AUX transactions, panel power transitions, backlight updates, DSC enable/disable/programming, interrupt handling, performance diagnostics, or debug readback.

The implied GPIO/AUX flow is: ensure relevant AUX/I2C pads are powered, configure AUX and HPD analog characteristics, enable receivers and pull-ups as required, and let the link/AUX layer drive transactions or HPD detection through the established register helper layer. Incorrect GPIO receive or pull-up programming can affect hotplug detection, DDC/AUX communication, genlock/swaplock signals, or panel control pins.

Panel sequencing flow is stateful and timing-sensitive. The driver programs reference dividers and delay registers, configures GPIO ownership and polarity, optionally locks or double-buffers PWM group registers, and drives `PANEL_PWRSEQ_TARGET_STATE` or override fields to transition the panel, DIGON, BLON, and sync outputs. Status and update-pending bits provide synchronization points; power and backlight code must respect them rather than treating the fields as ordinary memory.

The DSC programming flow uses the top clock-control fields, interface config, DSCC core config, PPS registers, interrupt controls, memory-power controls, and status fields together. Higher-level DSC code computes DSC PPS values from link timing and compression parameters, then writes `DSCC_PPS_CONFIG0..22`, configures slice layout and input format, enables clocks and memory, and monitors update-pending or error/overflow status. DSCCLK setup in the wider DCN sequencing is also relevant because DSCC register access can depend on clock availability.

Performance monitor flow is diagnostic: callers select events and counted values, choose increment and run-enable behavior, configure count-off and interrupt behavior, start or stop counters, then read high/low counter values through read selectors. Status and ACK fields in `PERFMON_CVALUE_INT_MISC` and `PERFMON_CNTL` are side-effect-prone and should be handled by the established perf/debug path.

Repeated instance layout is important control-flow context. The DSC/DSCC blocks are structurally parallel across instances 0, 1, and 2; `PWRSEQ0` and `PWRSEQ1` are structurally parallel; `DC_PERFMON17` and `DC_PERFMON18` are structurally parallel. The driver relies on instance-indexed register tables so common code can operate on the selected hardware instance by changing register addresses and using the same field names.

## State And Persistence

The file itself stores no mutable state. It defines how software reaches persistent hardware state in DCN registers and internal DSC/panel/link state machines.

Persistent hardware state represented here includes AUX/HPD electrical tuning, GPIO receiver and pull-up configuration, AUX/I2C pad power-good readback, UNIPHY reserved macro-control words, panel timing/divider/PWM/polarity/override state, DSC clocks and gate controls, DSCC input and PPS configuration, DSCC memory power state, DSCC error and buffer fullness telemetry, and perfmon configuration/counter state.

Several fields expose double-buffered or current-state behavior. `DOUBLE_BUFFER_REG_UPDATE_PENDING`, `BL_PWM_GRP1_REG_UPDATE_PENDING`, readback DB register enable fields, panel state readbacks, perfmon active/state fields, and DSCC error/fullness counters are synchronization or observation points. They should not be interpreted as independent software-owned state.

Memory power fields are persistent and sequencing-sensitive. `DSCC*_DSCC_MEM_POWER_CONTROL` can force or disable memories used by the DSC block and report their state. Powering these memories down at the wrong time can affect DSC programming retention, active compressed scanout, or safe register access.

## Dependencies And Integration Points

This generated header depends on the matching DCN 3.5.1 address header. The masks are meaningful only with the same register database and ASIC generation; similar DCN 3.5.0, DCN 3.6.0, or DCN 4.x headers must not be substituted without validation.

Primary integration points are:

- `display/dc/resource/dcn351/dcn351_resource.c`, which includes this generated header and builds DCN 3.5.1 resource, AUX, UNIPHY, DSC, and related register/mask tables.
- `display/dc/irq/dcn351/irq_service_dcn351.c`, which includes the same generated offset and shift/mask headers for DCN 3.5.1 interrupt source setup.
- `display/dmub/src/dmub_dcn351.c`, which initializes DMUB-facing DCN 3.5.1 register offsets and fields.
- `display/dc/dsc/dcn35/dcn35_dsc.c` and common DSC code, which consume DSC/DSCC field tables to enable clocks, configure memory power, program DSC PPS values, and read status.
- Panel-control code under `display/dc/dce` and `display/dc/dcn301`, which shows the higher-level patterns for PWRSEQ, PWM, target-state, and state-readback fields that these DCN 3.5.1 masks support.
- Link, DIO, AUX/I2C, and HPD handling paths, which rely on GPIO/AUX/UNIPHY field tables rather than direct register literals.

The register helper layer is the main API boundary. Direct open-coded bit manipulation against these constants would bypass instance tables, base-index selection, locking, double-buffering, and existing sequencing assumptions.

## Risks And Edge Cases

Generated-header drift is the central risk. A wrong mask or shift generally compiles successfully but writes the wrong hardware bits, which can cause failures in hotplug detection, AUX/DDC access, panel power sequencing, backlight PWM, DSC compression output, DSC interrupt status handling, or performance counter readback.

Chunk boundaries are incomplete. Whole-register validation for the first register requires the previous chunk's `DC_GPIO_AUX_CTRL_1` shift and early mask definitions. Whole-register validation for the last register requires the next chunk's remaining `DC_PERFMON19_PERFCOUNTER_CNTL` masks and related perfmon fields.

Reserved UNIPHY fields are opaque by design. Their full-width masks make it easy for generated tables to expose them, but they should not be written casually without hardware guidance. Treating reserved macro-control words as normal feature fields can destabilize PHY behavior.

Panel and backlight fields are sequencing-sensitive. Delay fields, target-state controls, override bits, polarity bits, register locks, frame-start update controls, and update-pending readbacks must be ordered with the panel power state machine. Mistakes can leave a panel dark, power a panel out of spec, or produce visible backlight jumps.

DSC PPS programming is highly coupled. PPS field mismatches between software calculation, DSCC registers, and sink expectations can produce link training success with corrupt compressed video. The `L` suffix on high-bit masks such as `0x80000000L`, `0xF0000000L`, and `0xFFFFFFFFL` also means consumers should keep using the driver's unsigned register helper types rather than signed arithmetic on raw constants.

Repeated instance consistency is a strong maintenance signal. `DSCC0`, `DSCC1`, and `DSCC2` should remain structurally parallel, as should `PWRSEQ0`/`PWRSEQ1` and `DC_PERFMON17`/`DC_PERFMON18`. A generator or merge error may only affect one DSC engine, one panel sequencer, or one perfmon instance.

## Test And Validation Signals

Compile coverage should include DCN 3.5.1 resource construction, IRQ service, DMUB register initialization, DSC code, AUX/DIO code, and panel-control users that include or indirectly consume `dcn_3_5_1_sh_mask.h`. Missing or renamed macros usually fail at compile time; incorrect numeric values require generated-data comparison or hardware validation.

Useful static checks include comparing this range against the authoritative DCN 3.5.1 register database, verifying complete registers have non-overlapping masks whose low set bit matches the shift value, diffing repeated `DSCC0/1/2`, `PWRSEQ0/1`, and `DC_PERFMON17/18` layouts, and checking neighboring chunks for the incomplete `DC_GPIO_AUX_CTRL_1` and `DC_PERFMON19_PERFCOUNTER_CNTL` boundaries.

Runtime signals include reliable HPD detection, stable AUX/DDC transactions, correct internal/eDP panel power-up and power-down timing, smooth and correctly synchronized backlight PWM updates, successful DSC modes on all exposed DSC engines, correct DSC PPS readback and compressed display output, absence of DSCC rate-buffer overflow/underflow interrupts during valid modes, stable suspend/resume and runtime power transitions, and working perfmon counter start/stop/readback/interrupt behavior.

## Research Notes

This is source-tree-aligned chunk research only. It intentionally writes only `Docs/researches/chunks/subset-b-002103_research.md`. Whole-file research for `dcn_3_5_1_sh_mask.h` must merge adjacent chunks to complete the leading `DC_GPIO_AUX_CTRL_1` register and trailing `DC_PERFMON19_PERFCOUNTER_CNTL` register context.
