# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8516.c

## Purpose
`pinctrl-mt8516.c` is the legacy MediaTek SoC description and platform-driver binding for MT8516. It contributes the MT8516 pin drive-strength map, special pull-register map, input-enable and Schmitt-trigger maps, register offsets, pinmux packing parameters, and EINT hardware description used by `pinctrl-mtk-common.c`.

## Important APIs, Types, And Data
- `mt8516_drv_grp[]` defines the same three drive classes used by several legacy MediaTek drivers: 4-16 mA, 2-8 mA, and 2-16 mA encodings.
- `mt8516_pin_drv[]` maps selected pins to drive register offsets from `0xd00` through `0xd70`. The table is sparse: not every pin has an entry.
- `mt8516_spec_pupd[]` maps special pull pins to PUPD/R1/R0 bit triplets at offsets `0xe00` through `0xe90`.
- `mt8516_ies_set[]` and `mt8516_smt_set[]` describe discontinuous IES and SMT bit ranges.
- `mt8516_pinctrl_data` binds `mtk_pins_mt8516`, all table pointers, register offsets, mode packing, and EINT parameters.

## Control Flow
At `arch_initcall`, `mtk_pinctrl_init()` registers the MT8516 platform driver. Device tree matching on `mediatek,mt8516-pinctrl` selects `mt8516_pinctrl_data`, then `mtk_pctrl_common_probe()` performs the common registration path. Pinctrl maps generated from DTS `pinmux` values resolve functions by the MT8516 pin descriptor header. Pin configuration calls use `spec_pull_set` for special PUPD/R1/R0 pins, fall back to generic pull enable/select registers for other pins, and use MT8516 IES/SMT tables for input-enable and Schmitt configuration.

## State And Persistence
This file holds only static SoC metadata. Hardware state lives in register writes performed by the common driver through regmap. The platform driver persists for the life of the device; PM operations for EINT suspend/resume are delegated to `mtk_eint_pm_ops`. The common group cache stores only the last configuration value per pin group.

## Dependencies And Integration Points
It depends on `pinctrl-mtk-common.h`, `pinctrl-mtk-mt8516.h`, Linux OF/platform/regmap/pinctrl APIs, and `mtk-eint`. The data table expects one regmap backing the pin controller and optional interrupt-controller properties for EINT. It exports a module device table for OF autoloading.

## Risks
The sparse drive table means board states that request drive strength on unsupported pins fail with `-EINVAL`. Special pull pins use shared set/reset registers; incorrect bit positions can invert bias or select the wrong resistor combination. `type1_start` and `type1_end` are both 125, disabling `regmap2` under half-open interval semantics. Pinmux packing values must match hardware or neighboring pins are corrupted.

## Test Signals
Build the MT8516 driver with its pin header and legacy common driver. Probe a DT node with `mediatek,mt8516-pinctrl`, verify pinctrl/GPIO registration, and verify EINT setup when `interrupt-controller` is present. Test UART, I2S, MSDC, PWM, GPIO, bias, input-enable, Schmitt, output-level, and drive-strength states.
