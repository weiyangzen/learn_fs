# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 49205-51607

## Scope

This chunk covers lines 49,205 through 51,607 of the generated DCN 3.0.0 register shift/mask header. It contains 2,165 `#define` entries and address-block comments for display-core hardware registers. There are no C functions, structs, enums, or executable statements in this slice; the exported interface is a macro namespace consumed by AMD display register helper code.

The range starts inside the LVTMA power-sequencer/backlight area with `LVTMA_PWRSEQ_REF_DIV` field macros, continues through DCIO GPIO/DDC/AUX pad controls, and then covers DSC compressor instances 0, 1, and the beginning of instance 2. The range is chunk-local and stops in the middle of `DSCC2_DSCC_PPS_CONFIG15`; line 51608, just outside this work item, contains the missing `DSCC2_DSCC_PPS_CONFIG15__RANGE_BPG_OFFSET0_MASK` pair for the included `RANGE_BPG_OFFSET0__SHIFT`.

## Purpose

The purpose of this header slice is to encode bit positions and masks for DCN 3.0 display hardware registers so driver code can compose and extract MMIO fields without hard-coded numeric literals. The matching offset header supplies register addresses, while this file supplies `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` constants used by helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_SHIFT`, `FD_MASK`, `DCE_PANEL_CNTL_SF`, `SF_DDC`, and `DSC_SF`.

This chunk covers these main hardware areas:

- LVTMA panel power sequencing and backlight PWM timing: reference dividers, power-up/power-down delays, PWM duty, PWM period, frame-start update delay, and the PWM group lock/update-pending register.
- Genlock and swaplock GPIO pad routing plus DCIO soft reset for UNIPHY/DSYNC lanes, DCRXPHY, and ZCAL.
- DCIO GPIO block for generic GPIOs, DDC pins 1-6, DDC VGA, genlock/swaplock pins, HPD pins, panel power sequence pins, pad drive strength, AUX controls, RX enable, pull-up enable, and AUX/I2C pad power-good status.
- DSC top, DSCCIF, DSCC, and DSC-local perfmon register fields for DSC instances 0 and 1, plus the start of DSC instance 2.
- DSC picture parameter set programming fields covering DSC version, picture size, slice geometry, bits per pixel/component, native 4:2:2/4:2:0 flags, rate-control model parameters, thresholds, and the first QP range entry.

## Important APIs, Types, And Functions

This chunk defines macros only. The important exported patterns are:

- `REGISTER__FIELD__SHIFT`: the low bit index for a field.
- `REGISTER__FIELD_MASK`: the bit mask for the field in the 32-bit register word.
- Register comments such as `//BL_PWM_CNTL`, `//DC_GPIO_DDC1_MASK`, and `//DSCC0_DSCC_PPS_CONFIG0`, which group shift/mask pairs by hardware register.
- Address-block comments such as `dce_dc_dcio_dcio_chip_dispdec`, `dce_dc_dsc0_dispdec_dscc_dispdec`, and `dce_dc_dsc1_dispdec_dsc_dcperfmon_dc_perfmon_dispdec`, which identify the IP block whose generated fields follow.

Important macro groups in the chunk:

- LVTMA/backlight: `LVTMA_PWRSEQ_REF_DIV`, `LVTMA_PWRSEQ_DELAY1`, `LVTMA_PWRSEQ_DELAY2`, `BL_PWM_CNTL`, `BL_PWM_CNTL2`, `BL_PWM_PERIOD_CNTL`, and `BL_PWM_GRP1_REG_LOCK`.
- DCIO synchronization/reset: `DCIO_GSL_GENLK_PAD_CNTL`, `DCIO_GSL_SWAPLOCK_PAD_CNTL`, and `DCIO_SOFT_RESET`.
- Generic GPIO: `DC_GPIO_GENERIC_MASK`, `DC_GPIO_GENERIC_A`, `DC_GPIO_GENERIC_EN`, and `DC_GPIO_GENERIC_Y` for generic pins A-G.
- DDC/AUX pin groups: `DC_GPIO_DDC[1-6]_MASK`, `DC_GPIO_DDC[1-6]_A`, `DC_GPIO_DDC[1-6]_EN`, `DC_GPIO_DDC[1-6]_Y`, equivalent `DDCVGA` registers, `PHY_AUX_CNTL`, `DC_GPIO_TX12_EN`, `DC_GPIO_AUX_CTRL_0` through `DC_GPIO_AUX_CTRL_5`, and `AUXI2C_PAD_ALL_PWR_OK`.
- Hotplug/power-sequence GPIO: `DC_GPIO_HPD_MASK`, `DC_GPIO_HPD_A`, `DC_GPIO_HPD_EN`, `DC_GPIO_HPD_Y`, `DC_GPIO_PWRSEQ_MASK`, `DC_GPIO_PWRSEQ_A`, `DC_GPIO_PWRSEQ_EN`, and `DC_GPIO_PWRSEQ_Y`.
- DSC top/control path: `DSC_TOP[0-2]_DSC_TOP_CONTROL`, `DSC_TOP[0-2]_DSC_DEBUG_CONTROL`, `DSCCIF[0-2]_DSCCIF_CONFIG0`, `DSCCIF[0-2]_DSCCIF_CONFIG1`, `DSCC[0-2]_DSCC_CONFIG0`, `DSCC[0-2]_DSCC_CONFIG1`, and `DSCC[0-2]_DSCC_STATUS`.
- DSC interrupts and PPS fields: `DSCC[0-2]_DSCC_INTERRUPT_CONTROL_STATUS` and `DSCC[0-2]_DSCC_PPS_CONFIG0` through at least `PPS_CONFIG15` for the instances present in this range.
- DSC diagnostics/perfmon: `DSCC0` and `DSCC1` memory power, squared-error counters, max-absolute-error counters, rate-buffer fullness counters, debug bus rotation, and `DC_PERFMON21_*` / `DC_PERFMON22_*` perf counter fields.

## Control Flow

There is no runtime control flow in this chunk. Its behavior is compile-time macro expansion:

1. A DCN 3.0 display translation unit includes this header, usually with the matching offset header.
2. Hardware-specific register tables expand field names through helper macros, for example `DSC_SF(DSCC0_DSCC_PPS_CONFIG1, BITS_PER_PIXEL, mask_sh)` or `SF_DDC(DC_GPIO_DDC1_MASK, AUX_PAD1_MODE, mask_sh)`.
3. Runtime driver code reads or writes MMIO registers through generated tables and helpers. The helpers combine register offsets with the shift/mask constants from this file.

The ordering is meaningful for generated-header review and reconciliation. Registers are grouped by address block and each register normally lists all shift macros first, followed by corresponding masks. The final included register is split by the chunk boundary, so whole-file analysis must not treat `DSCC2_DSCC_PPS_CONFIG15` as complete from this chunk alone.

## State And Persistence Behavior

The header itself stores no software state and persists no data. It describes hardware state in DCN display registers:

- LVTMA and backlight PWM fields affect panel sequencing state, backlight duty/period, update timing, and lock behavior. Values written there persist in hardware until the driver changes them or the display block resets.
- DCIO soft-reset bits can reset specific UNIPHY, DSYNC, DCRXPHY, and ZCAL blocks. Misprogramming these fields can disrupt live display links.
- GPIO `MASK`, `A`, `EN`, and `Y` groups describe the common pin model: mask/control, output data, output enable, and readback for DDC, HPD, genlock/swaplock, and panel power pins.
- DDC/AUX control fields choose AUX-vs-DDC pad modes, polarity, pull-down/pull-up behavior, drive strength, termination, hysteresis, voltage swing, I2C mode, and pad power controls.
- DSC top and DSCC fields persist compression-engine setup across a programmed stream: clock enable/gating behavior, input format, picture size, slice layout, PPS values, rate control model, and interrupt enable/status fields.
- DSC status, error, fullness, and perfmon fields expose hardware-observed state. Some are readback counters or latched statuses rather than ordinary writable configuration fields.

The macro names do not encode all access semantics. A mask may target a read-only status field, a write-one-to-clear status bit, a writeable configuration field, or a counter readback field. Callers must rely on the register programming model and local helper usage, not just the macro suffix.

## Dependencies And Integration Points

This generated header depends on name and numeric consistency with adjacent AMD register headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h` supplies the corresponding register offsets.
- Other DCN 3.x `*_sh_mask.h` headers define similar namespaces for related ASIC versions; reusing fields across versions requires care because field layouts drift.
- Enumeration headers such as `navi10_enum.h` document some field value meanings for DCIO/LVTMA/backlight controls, while this file supplies only raw bit geometry.

Important in-tree integration points found from nearby consumers include:

- `drivers/gpu/drm/amd/display/dc/dce/dce_panel_cntl.[ch]` and `dc/dcn301/dcn301_panel_cntl.[ch]` use `BL_PWM_GRP1_REG_LOCK` fields to lock/unlock PWM register updates and wait for update completion.
- `drivers/gpu/drm/amd/display/dc/gpio/ddc_regs.h` uses `DC_GPIO_DDC1_MASK` fields such as `DC_GPIO_DDC1DATA_PD_EN`, `DC_GPIO_DDC1CLK_PD_EN`, and `AUX_PAD1_MODE` through the DDC register table macros.
- `drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.h` and newer DSC headers use `DSC_SF` field-table macros for DSCC PPS, DSCCIF, status, memory-power, diagnostic, and perfmon fields. DCN 3.0 carries the same style of generated DSC field namespace.
- IRQ, modeset, AUX/DDC, hotplug, panel power, DSC programming, and perfmon/debug paths consume these constants indirectly through generated register field structures and MMIO helper macros.

The chunk is also part of a generated register contract for hardware bring-up. Direct hand edits are risky unless matched to the source register database and the paired offset definitions.

## Risks And Edge Cases

- A wrong shift or mask silently writes the wrong bits in an MMIO register. This can blank displays, break AUX/DDC transactions, mis-detect hotplug, corrupt DSC PPS programming, or wedge a display link.
- The assigned range begins and ends mid-register context. `LVTMA_PWRSEQ_REF_DIV` starts with its comment outside the range, and `DSCC2_DSCC_PPS_CONFIG15` lacks one mask line inside this chunk. Merge/reconciliation must account for neighboring chunks before judging field completeness.
- Backlight PWM group lock fields are synchronization-sensitive. Incorrect `BL_PWM_GRP1_REG_LOCK`, update-pending, or frame-start selection masks can cause brightness updates to race scanout or fail to latch.
- DDC/AUX pad mode, polarity, termination, and I2C-mode fields are board- and connector-sensitive. Bad definitions can cause EDID read failures, AUX training failures, or inconsistent hotplug behavior.
- GPIO mask fields mix enable, pull-down, receiver, drive-strength, and mode bits in compact layouts. Treating a multi-bit field as a boolean or using the wrong numbered DDC/HPD instance can affect an unrelated connector.
- `DCIO_SOFT_RESET` controls multiple PHY and DSYNC blocks. Using a stale mask from a related ASIC could reset the wrong lane or leave the intended block running.
- DSC PPS fields must match the DSC standard and the sink's negotiated capabilities. Wrong masks for `BITS_PER_PIXEL`, `CHUNK_SIZE`, slice dimensions, rate-control thresholds, or QP ranges can produce visible corruption or link underflow.
- `DSCC*_DSCC_INTERRUPT_CONTROL_STATUS` combines occurred-status and interrupt-enable fields in one generated register group. Confusing status bits with enable bits can leave overflow/underflow events unreported or stuck.
- Perfmon fields include event-selection, counter-state, interrupt, and readback fields. Incorrect masks can make diagnostic counters misleading even if display output appears functional.

## Test Signals

Useful validation signals for this chunk are build-time, macro-expansion, and hardware-integration oriented:

- Compile DCN 3.0/3.x AMD display code that includes `dcn_3_0_0_sh_mask.h`, especially panel control, GPIO/DDC, AUX, DSC, IRQ, and perfmon paths.
- Preprocessor or unit-style checks that representative `FD_MASK`, `FD_SHIFT`, `DCE_PANEL_CNTL_SF`, `SF_DDC`, and `DSC_SF` expansions resolve for fields in this range.
- Panel/backlight tests covering PWM enable, fractional duty programming, period programming, frame-start update latching, brightness changes, and suspend/resume backlight restore.
- GPIO/DDC/AUX tests covering EDID reads over all DDC instances, DisplayPort AUX transactions, HPD plug/unplug events, DDC VGA behavior where applicable, and pad power-good reporting.
- Link bring-up tests that exercise genlock/swaplock pads if the platform uses them, plus PHY reset paths around modeset and hotplug.
- DSC validation on DCN 3.0 hardware with compressed streams: mode validation, PPS programming, slice geometry, 4:2:0/4:2:2/native modes, high bits-per-pixel modes, and visual corruption checks.
- DSC error-path testing that observes DSCC rate-buffer overflow/underflow, rate-control buffer model overflow, and DSCCIF input-interface underflow status/interrupt behavior.
- Perfmon/debug tests that select events in `DC_PERFMON21_*` and `DC_PERFMON22_*`, start/stop counters, read low/high values, and acknowledge counter interrupts.

## Open Cross-Chunk Questions

- The previous chunk should be consulted for the beginning of the LVTMA power-sequencer register group and the `LVTMA_PWRSEQ_REF_DIV` comment context.
- The next chunk must complete `DSCC2_DSCC_PPS_CONFIG15` and continue the rest of DSC instance 2. Whole-file reconciliation should avoid flagging the missing `RANGE_BPG_OFFSET0_MASK` as a source defect when it is only outside this chunk boundary.
- The final per-file report should compare this mask header with `dcn_3_0_0_offset.h` and the active DCN 3.0 display register tables to identify any offset/mask coverage gaps.
