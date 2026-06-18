# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 35436-37655

## Purpose

This chunk is a generated DCN 3.5.0 register field shift/mask table for AMD display hardware. It does not implement runtime logic directly; it supplies preprocessor constants consumed by AMD Display Core register-access macros to pack, unpack, read, update, and validate MMIO fields for GPIO/AUX/DDC/HPD pads, UNIPHY reserved registers, panel power sequencing/backlight PWM, Display Stream Compression (DSC/DSCC/DSCCIF), and DC perfmon counters.

The line range contains 2,220 lines and 2,217 `#define` entries. Every entry follows the generated `REGISTER__FIELD__SHIFT` or `REGISTER__FIELD_MASK` convention, where the shift is the bit position and the mask is the already-shifted field mask for a 32-bit register value.

## Register Areas Covered

- `DC_GPIO_AUX_CTRL_1` through `DC_GPIO_AUX_CTRL_5` define electrical control fields for AUX, I2C/DDC, DDCVGA, and HPD pads: CSEL/RSEL choices for 0.9 V and 1.1 V domains, bias and resistor enables, slew/fall-slew tuning, spike filter controls, comparator selection, AUX DP/DN swap, hysteresis tuning, AUX control nibbles, DDC pad I2C mode, and AUX pad power-good fields.
- `DC_GPIO_RXEN` and `DC_GPIO_PULLUPEN` map receive-enable and pull-up-enable bits for generic GPIOs, sync/genlock/swaplock pins, and HPD1-HPD6 pins.
- `AUXI2C_PAD_ALL_PWR_OK` provides per-pad power state fields for AUX, I2C, I2C mode, DDCVGA, and HPD pad groups.
- `DCIO_UNIPHY{1..4}_UNIPHY_MACRO_CNTL_RESERVED{0..57}` reserve one full-width field per register instance. The defines expose only a full 32-bit `RESERVED` field shift/mask per register, preserving generated register coverage even where the public driver does not name hardware subfields.
- `PWRSEQ0_*` and `PWRSEQ1_*` cover two panel power-sequencer instances. Fields include GPIO power-sequencer enable/control/mask/output bits, panel DIGON/DIGON override, BLON/BLON override, power-up/down sequence delays, refresh dividers, panel state flags, PWM control and period registers, backlight group register locks, and spare bits.
- `DSC_TOP{0..2}_DSC_TOP_CONTROL`, `DSCCIF{0..2}_*`, and `DSCC{0..2}_*` define three Display Stream Compression instances. The DSCC coverage includes DSC mode/configuration, status and interrupt fields, PPS config registers 0-22, memory power controls, error accumulators, max absolute error fields, rate buffer fullness, rate control buffer fullness, and debug-bus rotation for instance 0.
- `DC_PERFMON17_*`, `DC_PERFMON18_*`, and the beginning of `DC_PERFMON19_*` define display perfmon event selection, count value selection, increment mode, hardware control/start-stop behavior, counter run/active/interrupt state, state selectors, high/low counter values, and current-value interrupt/misc fields.

## Important APIs, Types, and Macros

This header exposes constants only. The important "API" is the generated register-field naming contract used by AMD display macros:

- `REG_SET`, `REG_SET_N`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, `REG_GET_N`, `REG_READ`, and `REG_WRITE` in the display code use register offsets plus these shift/mask constants to manipulate MMIO fields.
- Register list helpers such as `SRI_ARR`, `SR`, `SRIR`, `SF`, `SF_DDC`, and DSC-specific `DSC_SF` expand into structures of register offsets, shifts, and masks.
- `dcn35_resource.c` builds `dsc_shift` and `dsc_mask` from `DSC_REG_LIST_SH_MASK_DCN35(__SHIFT)` and `DSC_REG_LIST_SH_MASK_DCN35(_MASK)`, so the DSCC constants in this chunk become per-instance DSC programming metadata.
- `dcn20_dsc_registers`, `dcn20_dsc_shift`, `dcn20_dsc_mask`, `dcn35_dsc_shift`, and `dcn35_dsc_mask` are the typed storage for the generated DSC register metadata.
- `ddc_regs.h` uses `DC_GPIO_AUX_CTRL_5__DDC_PAD*_I2CMODE` in `DDC_MASK_SH_LIST_DCN2`, tying this chunk to DDC/AUX pad mode configuration.
- Panel control code stores and restores `BL_PWM_CNTL`, `BL_PWM_CNTL2`, `BL_PWM_PERIOD_CNTL`, and power-sequencer divider fields through the generated field metadata.

## Control Flow and Runtime Behavior

There is no local control flow in this chunk. Runtime behavior appears when included through DCN 3.5 display resource construction:

1. DCN 3.5 resource initialization includes `dcn_3_5_0_offset.h` and this shift/mask header, then populates register/shift/mask structures for display blocks.
2. GPIO/DDC setup code selects per-connector DDC/AUX register metadata. When a DDC line is configured, the generic GPIO/DDC helpers use the stored mask/shift values for pad pull-down, AUX pad mode, RX selection, and I2C-mode updates.
3. Panel power and backlight code reads PWM state from hardware, caches working values, restores them after BIOS or suspend/resume anomalies, enables PWM output, and unlocks register groups. The power-sequencer constants in this chunk define the bit positions for those operations.
4. DSC creation wires a `dcn20_dsc` object to DCN 3.5 shift/mask tables. DSC enablement resets DSCC memory power control bits before enabling the compressor, then common DSC programming writes PPS config registers 0-22 using the masks/shifts from this chunk.
5. Perfmon consumers can program event selection, run mode, interrupt, state, and counter-value registers for display performance counters 17, 18, and 19.

## State and Persistence

The header itself is stateless and has no persistence. It defines compile-time constants that describe hardware state layout. Persistence concerns are in callers:

- Backlight and panel state are persisted in driver memory via `stored_backlight_registers` and restored to hardware when PWM registers are invalid or reset.
- DSCC memory power fields (`DSCC_MEM_PWR_FORCE`, `DSCC_MEM_PWR_DIS`, and state bits) reflect hardware low-power state. `dsc35_enable()` explicitly clears force/disable bits because DSCC memory can remain unexpectedly shut down after idle exit.
- DSC PPS registers persist the active compression stream parameters in hardware until reprogrammed, reset, or power-gated.
- Perfmon counters and state bits persist in hardware counter registers while the perfmon block is active and are reset or reconfigured by perfmon control writes.

## Dependencies and Integration Points

- Must be paired with `dcn_3_5_0_offset.h`; masks/shifts alone are not usable without matching MMIO register addresses.
- Depends on the AMD Display Core register abstraction in `drivers/gpu/drm/amd/display`, especially the resource construction layer and `REG_*` field-access macros.
- Integrates with `dc/gpio/ddc_regs.h` for DDC/AUX pad mode and RX selection.
- Integrates with `dc/dce` and `dc/dcn301` panel-control paths for PWM/backlight and panel power-sequencer programming.
- Integrates with `dc/dsc/dcn20`, `dc/dsc/dcn35`, and DCN resource headers for DSC PPS programming, interrupt/status reads, memory power handling, and error telemetry.
- Integrates with perfmon infrastructure through generated `DC_PERFMON17`, `DC_PERFMON18`, and `DC_PERFMON19` field layouts.

## Risks and Edge Cases

- Generated constants must match the ASIC register spec exactly. A single wrong shift or mask silently writes the wrong MMIO bits and can break display bring-up, HPD/DDC detection, backlight control, DSC compression, or perfmon reporting.
- Reserved UNIPHY definitions expose full-register masks. Callers must avoid treating these as safe writable public fields unless hardware documentation requires it.
- The DSC PPS fields are tightly packed and often span several fields per register. Incorrect packing can produce invalid DSC PPS payloads, link training/display corruption, or decompression failure on sinks.
- DSCC memory power control is sensitive during idle exit and power transitions. The existing DCN 3.5 DSC code already works around intermittent DSCC memory shutdown by clearing force/disable bits at enable time.
- Panel power and PWM fields affect physical panel sequencing. Bad masks for DIGON/BLON delays, overrides, or PWM duty/period can cause blank panels, flicker, or unsafe sequencing.
- GPIO/AUX/HPD electrical tuning fields affect signal integrity and hotplug/DDC reliability. Wrong masks can look like intermittent cable, EDID, or HPD problems rather than a software failure.
- Perfmon control fields include interrupt and counter restart controls; incorrect bit layout can leave counters inactive, count the wrong event, or generate unexpected interrupts.

## Test Signals

- Build coverage: compile the AMD display driver for DCN 3.5 targets with this header included; type/field mismatches in resource initializers and register macros should fail at compile time.
- Display bring-up: internal/eDP panel powers on, backlight responds, and suspend/resume does not leave PWM period/duty invalid.
- Connector detection: HPD, DDC EDID reads, AUX transactions, and I2C-over-AUX paths work across all exposed connectors and voltage/power states.
- DSC validation: high-bandwidth modes that require DSC light correctly, DSC PPS register dumps match expected stream parameters, and no DSCC interrupt/status errors or rate-buffer anomalies appear.
- Power management: idle exit, S0ix, runtime PM, and display off/on transitions do not leave DSCC memory in shutdown or panel sequencing registers reset.
- Perfmon validation: DC perfmon counters can be configured for known events, become active, increment predictably, and report/clear interrupts as expected.
- Register audit: compare generated masks/shifts against hardware XML/register database for DCN 3.5.0, especially packed PPS fields, panel sequencing fields, and GPIO/AUX electrical controls.
