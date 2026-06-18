# Research: subset-b-002282

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_0_0_offset.h -->
# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_0_0_offset.h

## Purpose

`dpcs_4_0_0_offset.h` is a generated AMDGPU display register offset header for the DCIO/DPCS 4.0.0 register set used by DCN 4.2 display code. It gives C preprocessor names for MMIO offsets in two address blocks: `dpcssys_dcio_dcio_dispdec` and `dpcssys_dcio_dcio_chip_dispdec`. The file does not implement display logic; it is the address half of a generated register contract used by AMD display core code to build register tables for GPIO, DDC, AUX, HPD-adjacent, clock, genlock/swaplock, debug, and soft-reset controls.

The header is guarded by `_dpcs_4_0_0_OFFSET_HEADER`. Every register has a paired `reg..._BASE_IDX` macro, and every base index in this file is `2`, so consumers combine these offsets with DCN segment-2 base addresses such as `ctx->dcn_reg_offsets[2]` or `DCN_BASE__INST0_SEG2`.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or linked symbols. The exported API is a list of `#define` constants named with AMD's `reg` prefix convention:

- Global DCIO/display-decoder controls: `regDC_GENERICA`, `regDC_GENERICB`, `regDCIO_CLOCK_CNTL`, `regDC_REF_CLK_CNTL`, `regDCIO_WRCMD_DELAY`, `regDC_PINSTRAPS`, `regDCIO_SPARE`, `regINTERCEPT_STATE`, `regDCIO_PATTERN_GEN_PAT`, `regDCIO_PATTERN_GEN_EN`, `regDPCS_DCIO_TEST_CLK_SRC`, `regDCIO_DEBUG`, `regDCIO_TEST_DEBUG_INDEX`, `regDCIO_TEST_DEBUG_DATA`, `regDBG_OUT_CNTL`, `regDCIO_DEBUG_CONFIG`, and `regDCIO_SOFT_RESET`.
- Five UNIPHY link-control and lane-crossbar register pairs: `regUNIPHYA_LINK_CNTL`/`regUNIPHYA_CHANNEL_XBAR_CNTL` through `regUNIPHYE_LINK_CNTL`/`regUNIPHYE_CHANNEL_XBAR_CNTL`.
- DDC GPIO groups for DDC1 through DDC5 and DDCVGA. Each DDC line has the four standard GPIO registers `MASK`, `A`, `EN`, and `Y`, e.g. `regDC_GPIO_DDC1_MASK`, `regDC_GPIO_DDC1_A`, `regDC_GPIO_DDC1_EN`, and `regDC_GPIO_DDC1_Y`.
- Power-sequencer and pad controls: `regDC_GPIO_PWRSEQ0_EN`, `regDC_GPIO_PWRSEQ1_EN`, `regDC_GPIO_PAD_STRENGTH_1`, `regPHY_AUX_CNTL`, `regDC_GPIO_AUX_CTRL_0`, `regDC_GPIO_AUX_CTRL_1`, `regDC_GPIO_AUX_CTRL_3`, `regDC_GPIO_AUX_CTRL_4`, `regDC_GPIO_AUX_CTRL_5`, and `regAUXI2C_PAD_ALL_PWR_OK`.

Consumer macros such as `REG(reg_name)` expand these definitions by concatenation: `BASE(reg ## reg_name ## _BASE_IDX) + reg ## reg_name`. That makes names like `REG(DC_GPIO_DDC1_A)` resolve to the correct DCN 4.2 absolute register address.

## Control Flow

The file has no runtime control flow. Its only direct flow is the compile-time include guard followed by linear register definitions grouped by generated address-block comments. Runtime behavior is entirely in consumers. DCN 4.2 GPIO and resource code includes this header with `dpcs_4_0_0_sh_mask.h`, defines a `BASE()` macro over segment 2, and expands register-list macros into static tables or switch cases.

A typical DDC path is: `hw_factory_dcn42.c` expands `ddc_data_regs_dcn2(id)` or `ddc_clk_regs_dcn2(id)`, which uses `REG(DC_GPIO_DDCx_A)`, `REG(DC_GPIO_DDCx_EN)`, `REG(DC_GPIO_DDCx_Y)`, `REG(DC_GPIO_DDCx_MASK)`, `REG(PHY_AUX_CNTL)`, and `REG(DC_GPIO_AUX_CTRL_5)` to populate `struct ddc_registers`. A translation path in `hw_translate_dcn42.c` maps BIOS or GPIO offsets back to `GPIO_DDC_LINE_DDC1` through `GPIO_DDC_LINE_DDC5` and `GPIO_DDC_LINE_DDC_VGA`, then derives related `Y`, `EN`, and `MASK` offsets by adding `+2`, `+1`, and `-1` to the `A` register offset.

## State And Persistence Behavior

This header stores no software state and performs no persistence. It names hardware registers whose values represent display hardware state: GPIO output enables and readbacks, AUX/DDC pad routing, UNIPHY lane mapping and reset controls, pinstrap status, pattern generator settings, genlock/swaplock pad controls, debug windows, and power-sequencer enable bits. Those hardware values can persist across ordinary driver reads and writes, but may be reset or rewritten by firmware, display initialization, suspend/resume, GPU reset, or power-gating transitions.

Because offsets are compile-time constants, there is no locking or caching in this file. Synchronization, read-modify-write discipline, reserved-bit preservation, and reset ordering belong to the display core and hardware-sequencing code that consumes the macros.

## Dependencies

The file has no `#include` dependencies. Operationally it depends on:

- The matching generated field header `dpcs_4_0_0_sh_mask.h`, which must describe the same registers and ASIC revision.
- AMD display register helpers and table-generation macros such as `REG`, `SR`, `SRI`, `SF_DDC`, `DDC_GPIO_REG_LIST`, and `DDC_MASK_SH_LIST_DCN2`.
- Correct DCN 4.2 base selection. Local consumers define `DCN_BASE__INST0_SEG2` or use `ctx->dcn_reg_offsets[2]`; every `_BASE_IDX` here points at that segment.
- ASIC dispatch that includes this header only for hardware whose DCIO/DPCS register layout matches DPCS 4.0.0.

## Integration Points

Direct local include points are `display/dc/gpio/dcn42/hw_factory_dcn42.c`, `display/dc/gpio/dcn42/hw_translate_dcn42.c`, and `display/dc/resource/dcn42/dcn42_resource.c`. The GPIO factory uses DDC offsets to build DDC clock/data register arrays and DDC shift/mask arrays. The GPIO translator uses the same offsets to convert between register offsets and DAL GPIO identities. The resource file includes this header as part of the wider DCN 4.2 register universe used to initialize display hardware blocks.

The header also preserves compatibility with generic display-core register list patterns. DDC code expects the standard four-register GPIO layout (`MASK`, `A`, `EN`, `Y`) to be contiguous in the generated offsets, and DCN 4.2 relies on that arithmetic in `id_to_offset()`. DIO/link-encoder families use similar DCIO names such as `DCIO_SOFT_RESET` and UNIPHY crossbar controls in earlier generations, so generation skew in this file would affect common register-table assumptions even if the direct DCN 4.2 consumer is small.

## Risks And Edge Cases

The highest risk is silent MMIO misaddressing. A wrong offset or wrong base index can compile cleanly while reading or writing the wrong display register, causing failed EDID/DDC transactions, broken AUX/DDC pad selection, bad GPIO direction/readback, incorrect UNIPHY lane routing, failed soft reset sequencing, or display bring-up failures. The register values are bare integers, so the compiler cannot validate hardware correctness.

The DDC GPIO offsets are structurally important: `hw_translate_dcn42.c` assumes `A`, `EN`, `Y`, and `MASK` are adjacent with fixed relative offsets. Changing the order or adding gaps would break derived `offset_y`, `offset_en`, and `offset_mask` calculations. DCN 4.2 factory code allocates DDC1 through DDC5, a dummy sixth entry, and VGA; this header provides DDC1 through DDC5 and DDCVGA but no `DC_GPIO_DDC6_*` offsets, so any consumer trying to instantiate a real DDC6 GPIO register set from this header would fail to compile or need a different mapping.

Another risk is offset/mask skew. If this offset file is regenerated without the paired shift/mask file, table macros can combine a correct address with stale bitfields, which is especially hazardous for DDC pad mode, AUX polarity, RX select, power-good, and soft-reset bits.

## Test Signals

Static validation should build the DCN 4.2 GPIO factory, GPIO translator, resource code, DDC/AUX helpers, and any link-encoder paths that include the DPCS 4.0.0 headers. Undefined macro failures are useful for missing names, but numeric offset regressions require comparison against the authoritative ASIC register database or a generated-header diff.

Runtime signals include successful DCN 4.2 display initialization, working HPD-to-DDC translation from BIOS GPIO offsets, reliable EDID reads on DDC1 through DDC5 and VGA, correct AUX/DDC pad mode selection, suspend/resume with no stale GPIO direction or power-good failures, and absence of MMIO timeout or display-core assertion logs around `DC_GPIO_DDC*_A`, `PHY_AUX_CNTL`, `DC_GPIO_AUX_CTRL_5`, and `DCIO_SOFT_RESET` accesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_0_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_0_0_sh_mask.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_0_0_sh_mask.h -->
