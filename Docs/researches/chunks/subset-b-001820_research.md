# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 44530-47039

## Scope

This chunk covers a generated DCN 3.1.2 shift/mask header slice for AMD display hardware registers. It contains only C preprocessor constants and generated grouping comments; there are no local functions, structs, enums, storage objects, or executable statements.

The slice starts in the tail of `UNIPHYB_CHANNEL_XBAR_CNTL`, covers DCIO link/GPIO controls, UNIPHY reserved macro-control fields, panel power sequencer instances 0 and 1, DSC compressor instance 0, DSC interface/top controls, and ends partway through `DC_PERFMON19_PERFCOUNTER_CNTL2`. Because both ends are partial register families, the final per-file reconciliation should merge this chunk with neighboring chunks before making whole-file claims.

## Purpose

This header is part of the generated hardware ABI used by AMDGPU Display Core for DCN 3.1.2 ASICs. Each macro gives either a field bit offset (`__SHIFT`) or bit mask (`_MASK`) for a named MMIO register field. Driver code normally reaches these constants through register table builders and helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `SF`, `SRI`, `SRIR`, GPIO field lists, panel-control field lists, DSC field lists, and perfmon tables.

At a hardware level, this chunk describes:

- UNIPHY link lane inversion, power-sequencer selection, and channel crossbar routing for UNIPHY B through E.
- DCIO-level write-command delay, pin strap, intercept, genlock/swaplock pad, frame-start selection, and soft-reset fields.
- Display GPIO pin programming for generic pins, DDC/I2C/AUX pads, HPD pins, genlock pins, power-sequence pins, TX/RX enables, pullups, pad strength, AUX control, and AUX/I2C pad power-good status.
- Reserved UNIPHY macro-control register fields for UNIPHY instances 1 through 4.
- PWRSEQ0 and PWRSEQ1 panel GPIO, panel digital/backlight power sequencing, delay/reference divider, PWM, grouped register lock, and spare fields.
- DSCC0 Display Stream Compression compressor configuration, picture parameter set programming, interrupt/status bits, memory power control, quality/error metrics, buffer fullness readbacks, and debug bus selection.
- DSCCIF0 input-interface format/underflow/update-pending fields and DSC_TOP0 clock/debug controls.
- The beginning of DC perfmon instance 19 counter control fields.

The main value is symbolic correctness. Consumers can request fields such as `DC_GPIO_DDC1_MASK__AUX_PAD1_MODE_MASK`, `PWRSEQ0_BL_PWM_CNTL__BL_PWM_EN_MASK`, or `DSCC0_DSCC_PPS_CONFIG16__RANGE_BPG_OFFSET2_MASK` without embedding fragile numeric bit layouts in runtime code.

## Important APIs, Types, And Constants

There are no callable APIs or local types. The exported interface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: numeric bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: mask for the same field.
- Register comments such as `//DSCC0_DSCC_PPS_CONFIG1` and address-block comments such as `// addressBlock: dce_dc_pwrseq0_dispdec_pwrseq_dispdec` preserve generated register grouping.

Important macro families in this chunk are:

- `UNIPHYC_LINK_CNTL`, `UNIPHYD_LINK_CNTL`, `UNIPHYE_LINK_CNTL`, and corresponding `*_CHANNEL_XBAR_CNTL` families: per-channel invert bits, link-to-power-sequencer selection, and 2-bit channel source selectors. The first six lines complete the preceding `UNIPHYB_CHANNEL_XBAR_CNTL` family.
- `DCIO_WRCMD_DELAY`, `DC_PINSTRAPS`, `INTERCEPT_STATE`, `DCIO_BL_PWM_FRAME_START_DISP_SEL`, `DCIO_GSL_GENLK_PAD_CNTL`, `DCIO_GSL_SWAPLOCK_PAD_CNTL`, and `DCIO_SOFT_RESET`: top-level DCIO timing, strap, power/intercept state, genlock/swaplock routing, and reset masks for UNIPHY/DSYNC/PWRSEQ blocks.
- `DC_GPIO_GENERIC_*`, `DC_GPIO_DDC1_*` through `DC_GPIO_DDC5_*`, `DC_GPIO_DDCVGA_*`, `DC_GPIO_GENLK_*`, and `DC_GPIO_HPD_*`: GPIO mask, output enable, output value, and input/readback fields. DDC masks also include AUX pad mode, AUX polarity, hardware pull-down enable allowance, and clock/data drive strength. HPD masks include per-pin mask/pull-down/receive fields, RX select fields, and HPD pad strength.
- `DC_GPIO_PWRSEQ0_EN`, `DC_GPIO_PWRSEQ1_EN`, `DC_GPIO_TX12_EN`, `DC_GPIO_RXEN`, `DC_GPIO_PULLUPEN`, `PHY_AUX_CNTL`, `DC_GPIO_AUX_CTRL_0` through `DC_GPIO_AUX_CTRL_5`, and `AUXI2C_PAD_ALL_PWR_OK`: pad enables, RX enable/power-down behavior, pullup controls, AUX pad receiver selection, AUX I/O enable, I2C-mode controls, pad polarity, pull-down selection, detect selection, and power-good status.
- `DCIO_UNIPHY<n>_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED57` for UNIPHY instances 1-4: reserved full-width or subfield masks, mostly one data field per register, used to preserve the generated register map even where public driver code may not name individual semantics.
- `PWRSEQ0_*` and `PWRSEQ1_*`: per-instance panel power sequencer fields for GPIO enable/control/mask/readback, panel `BLON`/`DIGON`/`SYNCEN` control and polarity, target-state request and readback, delay programming, PWM reference dividers, PWM period and active count, PWM fractional/override enable, grouped register lock/update-pending bits, and spare fields.
- `DSCC0_DSCC_CONFIG0`, `DSCC0_DSCC_CONFIG1`, `DSCC0_DSCC_STATUS`, and `DSCC0_DSCC_INTERRUPT_CONTROL_STATUS`: DSC slice/topology controls, rate-control buffer model size, double-buffer update-pending bit, and interrupt enable/status/clear fields for rate-control buffer model, output buffer overflow/underflow, and end-of-frame-not-reached conditions.
- `DSCC0_DSCC_PPS_CONFIG0` through `DSCC0_DSCC_PPS_CONFIG22`: DSC picture parameter set fields including DSC version, PPS identifier, line buffer depth, bits per component/pixel, VBR/simple/native modes, RGB conversion, block prediction, chunk size, picture/slice dimensions, initial delays, scale intervals, BPG offsets, initial/final offsets, flatness QP limits, RC model size, RC edge factor, quant increment limits, target offsets, RC buffer thresholds, and range min/max QP plus BPG offsets 0-14.
- `DSCC0_DSCC_MEM_POWER_CONTROL`, error/readback, fullness, and debug fields: DSC memory low-power control/state, squared-error lower/upper words per component, max absolute error, rate-buffer and rate-control-buffer max fullness levels, and debug bus rotate selectors.
- `DSCCIF0_DSCCIF_CONFIG0/1`: input-interface underflow recovery/interrupt/status, input pixel format, bits per component, double-buffer update pending, and picture size fields.
- `DSC_TOP0_DSC_TOP_CONTROL` and `DSC_TOP0_DSC_DEBUG_CONTROL`: DSC clock enable, display/DSC clock gate disable bits, debug enable, and test clock mux selection. `DSC_TOP0_DSC_DEBUG_CONTROL` appears twice with identical field definitions in this slice.
- `DC_PERFMON19_PERFCOUNTER_CNTL` and the start of `DC_PERFMON19_PERFCOUNTER_CNTL2`: event selection, counted-value source selection, increment mode, hardware control, run-enable mode, counter-off start disable, restart, interrupt enable, active status, counter selector, counted value type, hardware stop selections, and counter-off selector fields.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time macro expansion:

1. DCN 3.1.2-specific resource, IRQ, DMUB, GPIO, panel, DSC, or diagnostic code includes this header with the matching offset header.
2. Register table macros concatenate register and field names into `*_MASK` and `*__SHIFT` constants.
3. Runtime helpers use those generated table entries to compose MMIO writes, read/modify/write selected fields, poll status bits, decode readback fields, and acknowledge hardware events.
4. Actual sequencing lives in other display code. This header supplies the bit layout required by those sequences, including AUX/DDC pin setup, HPD/GPIO translation, panel/backlight sequencing, DSC PPS programming, DSC clock gating, update-pending polling, and perf counter setup.

The order in the file is generated and hardware-block oriented. Most register comments are followed by all `__SHIFT` definitions and then all matching `_MASK` definitions. Repeated instances are ordered numerically, such as DDC1-DDC5, UNIPHY1-UNIPHY4 reserved registers, PWRSEQ0/PWRSEQ1, and DSC PPS registers 0-22.

## State And Persistence Behavior

The header itself stores no software state and persists no data. It describes hardware state held in DCN display registers:

- DCIO and UNIPHY state covers lane inversion, crossbar source selection, soft reset, strap readback, write-command delay, genlock/swaplock pad routing, intercept state, and PWM frame-start display selection.
- GPIO state covers pin masks, pull-down/pullup enables, output enables, output values, receive/readback bits, drive strength, AUX/DDC mode selection, polarity, RX enable, detect selection, and AUX/I2C pad power-good readback.
- PWRSEQ state covers panel target/current state, backlight and digital power outputs, sequencing delays, PWM period/duty/fractional controls, reference dividers, grouped register lock/update-pending status, and spare state.
- DSCC/DSCCIF/DSC_TOP state covers DSC clocking, compressor topology and PPS parameters, underflow recovery/status, double-buffered update pending, interrupt enables/status/clear bits, DSC memory power state, quality metrics, buffer fullness levels, debug selection, and input picture format/dimensions.
- DC perfmon19 state covers event selection, counting mode, interrupt enable/status-related control, counter active status, and hardware stop/counter-off routing for the selected counter.

Persistence is hardware-defined. Programmed fields generally remain until changed by another MMIO write, panel/display block reset, power transition, or full ASIC reset. Status and readback fields can change asynchronously with HPD/AUX activity, I2C/DDC transactions, panel sequencing, backlight updates, DSC frame processing, DSC interrupt events, memory power management, or perf counter activity. This header does not encode read-only, write-one-to-clear, volatile, lock, or delay semantics; callers must follow the block-specific programming model.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.1.2 register model staying synchronized across companion files and consumers:

- `dcn_3_1_2_offset.h` supplies the register offsets paired with these shift/mask definitions.
- DCN 3.1 include sites in this tree include this header from `drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, `drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.c`, and `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c`.
- GPIO register helpers use these names through `dc/gpio/ddc_regs.h`, `dc/gpio/hpd_regs.h`, `dc/gpio/hw_ddc.c`, and generation-specific `hw_translate_*` files to map logical DDC, HPD, generic, and PWRSEQ pins to MMIO offsets, masks, and shifts.
- Panel/backlight control paths use PWRSEQ and BL_PWM fields through DCE/DCN panel control headers and implementations, including stored backlight register save/restore, PWM period/duty programming, PWM group locking, and panel power-state polling.
- DSC code consumes DSCC/DSCCIF/DSC_TOP field names through DSC field-list macros and register helpers. Later-generation DSC headers show the same naming contract for programming PPS registers, enabling DSC clocks, reading update-pending state, configuring interrupts, and collecting error/fullness diagnostics.
- IRQ and hotplug flows depend on HPD and HPDRX mapping code in the display IRQ services; this chunk's GPIO HPD masks are adjacent infrastructure for the physical pin state, while HPD interrupt registers live elsewhere in the full header.
- DMUB and resource initialization can use the same register tables to restore or coordinate DCN 3.1.2 display state across firmware-assisted paths.
- SOC enum headers define values for some fields described here, such as `DCIO_UNIPHY_CHANNEL_XBAR_SOURCE` and PWRSEQ target/override enums, while this chunk supplies the bit placement.

The direct interface is a preprocessor name contract. Missing or renamed macros normally fail at build time when an `SF`/`REG_*` table expands. Incorrect numeric masks are more dangerous because the build can succeed while runtime MMIO writes target the wrong bits.

## Risks And Edge Cases

- The chunk begins inside `UNIPHYB_CHANNEL_XBAR_CNTL` and ends inside `DC_PERFMON19_PERFCOUNTER_CNTL2`; merge/reconciliation must include adjacent chunks for complete register-family coverage.
- GPIO and AUX/DDC masks are tightly tied to board routing and connector discovery. Wrong DDC clock/data, AUX pad mode, RX select, polarity, pull-down, or power-good masks can break EDID reads, AUX transactions, link training, or HPD behavior.
- HPD and generic GPIO fields are repetitive and review-unfriendly. A one-pin mask drift can affect only one connector, making failures appear board-specific.
- PWRSEQ fields have visible user impact. Incorrect panel `DIGON`, `BLON`, target-state, delay, reference-divider, PWM period, or PWM duty masks can cause black panels, flicker, bad brightness levels, or resume failures.
- Grouped PWM register lock/update-pending fields are sequencing-sensitive. Updating duty-cycle fields without the correct lock/unlock and pending polling can leave stale backlight values or create frame-boundary glitches.
- DCIO soft-reset bits are high-impact. A wrong reset mask could reset the wrong UNIPHY/DSYNC/PWRSEQ block or fail to reset a block that needs recovery.
- DSCC PPS fields mirror DSC protocol parameters. Mask drift in bits-per-pixel, chunk size, slice dimensions, BPG offsets, QP ranges, or RC thresholds can produce compressed stream corruption that may only show on DSC-enabled displays and modes.
- DSCC interrupt/status/clear bits mix enable, status, and clear semantics in one generated namespace. The shift/mask header cannot prevent callers from treating clear bits as ordinary state bits.
- DSC clock-gating and DSCC memory-power fields can interact with low-power behavior. Wrong masks can leave DSC inaccessible, waste power, or cause hangs if registers are touched while the required clock/power state is absent.
- Full-width readback masks such as squared-error words and high-bit masks such as perfmon selectors, interrupt acknowledgements, and DSC PPS fields require unsigned 32-bit handling in callers.
- `DSC_TOP0_DSC_DEBUG_CONTROL` is duplicated in this chunk with identical definitions. That is probably generator output, but whole-file validation should confirm it is intentional and not masking a missing adjacent register.
- Reserved UNIPHY macro-control registers are intentionally opaque. They preserve register-map coverage but give no semantic safety; any consumer must rely on hardware documentation or generator provenance.
- Similar field names exist across DCN generations, but this file is specific to DCN 3.1.2. Copying masks from DCN 3.0.x, 3.1.x variants, or later ASICs is unsafe without register-database confirmation.

## Test Signals

Useful validation is mostly build-time, register-table, and hardware-integration oriented:

- Build AMDGPU Display Core with DCN 3.1 support so `dcn31_resource.c`, `irq_service_dcn31.c`, and `dmub_dcn31.c` compile against `dcn_3_1_2_offset.h` plus this shift/mask header.
- Preprocess or compile GPIO, DDC, HPD, panel-control, DSC, and perfmon users that expand `SF_DDC`, `HPD_REG_LIST`, `DCN301_PANEL_CNTL_SF`-style lists, `DSC_SF`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT` against these macro names.
- Compare this header slice against the matching offset header and upstream register-generation source to ensure every listed register field has a matching register offset and expected bit width.
- Exercise DDC/AUX paths on DCN 3.1.2 hardware: EDID read, DP AUX transactions, AUX/I2C mode switching, HPD-low AUX error paths, connector hotplug/unplug, and multi-connector boards that cover DDC1-DDC5 and DDCVGA if present.
- Validate GPIO translation for generic, HPD, DDC, genlock, and PWRSEQ pins by checking logical pin mappings against board schematics or BIOS connector tables.
- Exercise panel power and backlight behavior: boot panel enable, suspend/resume restore, backlight duty updates, PWM period/reference-divider setup, group-lock update-pending polling, and PWRSEQ0/PWRSEQ1 selection.
- Run DSC-enabled display modes that cover RGB, 4:2:2/4:2:0/native modes where supported, multiple slice widths/heights, different bits-per-pixel/component settings, and mode changes that force PPS reprogramming.
- Check DSC error/fullness/status telemetry after stress modes and link-rate changes, including interrupt enable/status/clear behavior for buffer overflow/underflow and end-of-frame-not-reached conditions.
- Verify DSC clock enable/disable and memory power transitions across blanking, modesets, low-power entry/exit, and reset paths.
- Run perfmon smoke tests for DC perfmon19 counter event selection, counter activation, interrupt enable path, hardware stop controls, and counter-off selection once the adjacent chunk supplies the remaining perfmon fields.

## Open Cross-Chunk Questions

- The preceding chunk should provide the beginning of `UNIPHYB_CHANNEL_XBAR_CNTL`; this chunk only includes channel 2/3 shifts and all four masks.
- The next chunk should complete `DC_PERFMON19_PERFCOUNTER_CNTL2` and likely the rest of the DC perfmon19 register family.
- Whole-file reconciliation should decide whether the duplicated `DSC_TOP0_DSC_DEBUG_CONTROL` block is expected generator output or a sign that a neighboring DSC top register is missing from the source register database.
- Final synthesis should identify the generator/register-database provenance if available, because manual edits to this file are high risk and hard to validate by inspection alone.
