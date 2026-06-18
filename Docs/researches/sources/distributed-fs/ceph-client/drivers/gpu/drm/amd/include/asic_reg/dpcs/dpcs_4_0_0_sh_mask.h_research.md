# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_0_0_sh_mask.h

## Purpose

`dpcs_4_0_0_sh_mask.h` is the generated bitfield companion for `dpcs_4_0_0_offset.h`. It defines `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros for DCIO/DPCS 4.0.0 registers used by DCN 4.2 display code. The file contains no executable logic; it provides the field positions needed by AMDGPU display register helpers to compose, update, and decode 32-bit MMIO register values.

The field coverage mirrors the offset header: generic DCIO controls, UNIPHY link and lane-crossbar controls, DDC GPIO/AUX pad controls, power-sequencer controls, debug/test registers, and power-good bits. It is guarded by `_dpcs_4_0_0_SH_MASK_HEADER`.

## Important APIs, Types, And Macros

There are no functions, structs, or enums. The public interface is the macro namespace:

- Generic and clock fields: `DC_GENERICA__GENERICA_SEL`, `DC_GENERICB__GENERICB_SEL`, `DCIO_CLOCK_CNTL__DCIO_TEST_CLK_SEL`, `DCIO_CLOCK_CNTL__DISPCLK_R_DCIO_GATE_DIS`, and `DC_REF_CLK_CNTL__GENLK_CLK_OUTPUT_SEL`.
- UNIPHY fields: each of `UNIPHYA` through `UNIPHYE` exposes per-channel invert bits in `*_LINK_CNTL` and four lane-source fields plus four DOUT enable bits in `*_CHANNEL_XBAR_CNTL`.
- Global DCIO control/status fields: `DCIO_WRCMD_DELAY__UNIPHY_DELAY`, `DC_PINSTRAPS__DC_PINSTRAPS_*`, full-width spare/pattern/debug fields, `INTERCEPT_STATE__*`, `DCIO_PATTERN_GEN_EN`, `DPCS_DCIO_TEST_CLK_SRC__DPCS_TEST_CLK_SRC_SEL`, `DBG_OUT_CNTL__*`, `DCIO_DEBUG_CONFIG__DCIO_DBG_EN`, and `DCIO_SOFT_RESET__*`.
- DDC GPIO fields for DDC1 through DDC5 and DDCVGA: clock/data mask, pull-down enable, receive, address/output (`A`), enable (`EN`), and readback (`Y`) fields. DDC1 through DDC5 also define AUX pad mode, AUX polarity, hardware pull-down allowance, and AUX hot-plug pull-down fields.
- AUX/pad analog and routing fields: `PHY_AUX_CNTL__AUX_PAD_WAKE` and `AUX1_PAD_RXSEL` through `AUX6_PAD_RXSEL`; `DC_GPIO_AUX_CTRL_0`, `_1`, `_3`, `_4`, and `_5` fields for slew, spike rejection, comparator select, termination, DP/DN swap, hysteresis, AUX control, voltage output drive tuning, I2C mode, 1.2V enable, and DDC pad I2C control.
- Power sequencing and power-good fields: `DC_GPIO_PWRSEQ0_EN`/`DC_GPIO_PWRSEQ1_EN` backlight and VSync/generic enable fields, `DC_GPIO_PAD_STRENGTH_1` genlock/sync drive strength fields, and `AUXI2C_PAD_ALL_PWR_OK__AUXI2C_PHY1_ALL_PWR_OK` through `PHY6`.

These macros are consumed through AMD field-helper patterns. In DCN 4.2 GPIO code, `DDC_MASK_SH_LIST_DCN2(__SHIFT, id)` and `DDC_MASK_SH_LIST_DCN2(_MASK, id)` concatenate field names such as `PHY_AUX_CNTL__AUX1_PAD_RXSEL__SHIFT` and `DC_GPIO_AUX_CTRL_5__DDC_PAD1_I2CMODE_MASK` into `struct ddc_sh_mask` arrays.

## Control Flow

The header's only direct flow is the include guard and a linear list of register comments plus field definitions. It does not branch, loop, call functions, or access registers. Runtime control flow happens in consumers that read a register using the offset header, then apply a shift/mask pair to extract or update one field.

In the DCN 4.2 DDC path, initialization builds one shift table and one mask table per DDC line. Later GPIO/DDC helper code can use those tables to set DDC/AUX pad mode, select AUX pad receive routing, control pull-downs, and interpret GPIO clock/data values. The translator path uses two mask macros directly, `DC_GPIO_DDC1_A__DC_GPIO_DDC1DATA_A_MASK` and `DC_GPIO_DDC1_A__DC_GPIO_DDC1CLK_A_MASK`, as canonical masks for all DDC line `A` registers because the same bit positions are repeated across DDC1 through DDC5 and DDCVGA.

## State And Persistence Behavior

This file stores no mutable software state. It describes hardware state in DCIO/DPCS registers. Some fields are configuration state, such as DDC pad I2C mode, AUX pad RX select, UNIPHY lane crossbar source, soft-reset bits, and pattern-generator enable. Other fields are status or readback state, such as GPIO `Y`, `*_RECV`, `INTERCEPT_STATE`, debug data, and AUX/I2C pad power-good bits.

Persistence is therefore hardware-defined. Written configuration can remain effective until the driver, firmware, power management, reset, or power gating changes it. Status fields may change asynchronously as display connectors, pads, interrupts, or power rails change. The header does not provide synchronization, reserved-bit handling, or ordering; consumers must use read-modify-write helpers and hardware sequencing where required.

## Dependencies

The field macros depend on the matching register-address file `dpcs_4_0_0_offset.h` and the AMDGPU register-field naming convention. The generated names are intentionally shaped for helper macros that concatenate `REGISTER`, `FIELD`, and `_MASK` or `__SHIFT` suffixes. Local dependencies include `display/dc/gpio/ddc_regs.h`, which expects fields like `DC_GPIO_DDC1_MASK__AUX_PAD1_MODE`, `PHY_AUX_CNTL__AUXn_PAD_RXSEL`, and `DC_GPIO_AUX_CTRL_5__DDC_PADn_I2CMODE` to exist.

The file is ASIC-specific. Its shifts and masks are valid only when the driver has selected the DPCS/DCIO 4.0.0 register layout. It also depends on fixed-width unsigned register operations; many mask literals use an `L` suffix and include high bits such as `0x80000000L`, so consumers should avoid signed arithmetic surprises by storing register values in `uint32_t`.

## Integration Points

Direct DCN 4.2 integration occurs in `hw_factory_dcn42.c`, `hw_translate_dcn42.c`, and `dcn42_resource.c`. The factory builds DDC register and field tables for five DDC ports, one dummy sixth entry, and VGA. The translator uses DDC `A` register masks to represent clock/data pins in `struct gpio_pin_info`. Resource initialization includes the header alongside broad DCN 4.2 register metadata so block constructors can use consistent offsets and fields.

The file also aligns with common display-core register patterns from earlier DCN generations. Link-encoder headers in older generations contain field-list macros for `DCIO_SOFT_RESET` and UNIPHY crossbar fields; DDC code uses the same `DDC_MASK_SH_LIST_DCN2` pattern across DCN 2.x, 3.x, 4.0.1, and 4.2. This header lets the shared GPIO/DDC helper code keep generation-neutral table layouts while substituting the DPCS 4.0.0 bit positions.

## Risks And Edge Cases

Incorrect shifts or masks can silently corrupt adjacent hardware fields. This is especially risky for high-bit fields such as UNIPHY DOUT enables, GPIO pad strength, DDCVGA data strength, soft-reset controls, and AUX control fields. A stale mask paired with the correct offset can make a display issue look like a sequencing or board problem rather than a generated-header mismatch.

The DDC field set is repetitive but not perfectly identical. DDC1 through DDC5 define AUX pad mode, polarity, hardware pull-down allowance, and hot-plug pull-down fields, while DDCVGA has a different polarity/strength set and no AUX pad mode. DCN 4.2 factory code uses `DDC_MASK_SH_LIST_DCN2_VGA()` with zeros for the AUX-specific table slots, so treating VGA as a normal numbered DDC pad would be wrong.

There is also a DDC6 asymmetry. `PHY_AUX_CNTL` and several AUX control registers expose AUX6/DDC6-style fields, and `DDC_MASK_SH_LIST_DCN2(__SHIFT, 6)` can compile for shift/mask fields such as `AUX6_PAD_RXSEL` and `DDC_PAD6_I2CMODE`. However the offset header does not provide `DC_GPIO_DDC6_*` registers, and `hw_factory_dcn42.c` installs a dummy sixth DDC register entry. Consumers must not infer that a complete DDC6 GPIO port exists from the presence of AUX6 field macros alone.

## Test Signals

Compile-time signals include successful builds of DCN 4.2 GPIO factory and translator objects with no undefined field macros from `DDC_MASK_SH_LIST_DCN2`, `DDC_MASK_SH_LIST_DCN2_VGA`, or direct DDC mask references. Generated-header validation should compare every shift/mask pair against the authoritative ASIC register database and ensure the paired offset header covers the same register set.

Runtime validation should exercise EDID/DDC reads on all available DCN 4.2 connectors, including AUX-to-I2C mode transitions, VGA-style DDC if exposed, suspend/resume, hotplug, and display reset paths. Useful failure signals are DDC/AUX timeouts, incorrect GPIO clock/data pin identification, broken HPD-to-DDC mapping, AUX pad power-good readback failures, display link-training failures after soft reset, and display-core assertions around GPIO mask, AUX RX select, or DDC pad I2C mode programming.
