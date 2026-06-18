# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6779.c

## Purpose
This file supplies the MT6779 SoC-specific register map and platform-driver glue for the MediaTek Paris pinctrl core. It describes 203 pins, their GPIO/mux registers, electrical configuration registers, EINT hardware, and the regional register base names required for `mediatek,mt6779-pinctrl`.

## Important APIs, Types, And Functions
`PIN_FIELD_BASE()` and `PINS_FIELD_BASE()` adapt `PIN_FIELD_CALC()` for 32-bit register banks. The field arrays cover mode, direction, DI, DO, input enable select (`IES`), Schmitt trigger (`SMT`), pull-up, pull-down, drive strength, PUPD, R0, and R1. GPIO mode/direction/value are grouped mostly under base index 0, while electrical settings are distributed across seven IOCFG regions.

`mt6779_reg_cals` is the main bridge from generic pinctrl register requests to SoC-specific fields. `mt6779_pinctrl_register_base_names` names the required resources: `gpio`, `iocfg_rm`, `iocfg_br`, `iocfg_lm`, `iocfg_lb`, `iocfg_rt`, `iocfg_lt`, and `iocfg_tl`. `mt6779_eint_hw` declares six EINT ports, 195 AP EINT lines, 13 debounce counters, and `debounce_time_mt2701`. `mt6779_data` enables `ies_present`, combo bias helpers, raw drive helpers, and advanced pull helpers.

## Control Flow
`arch_initcall(mt6779_pinctrl_init)` registers a platform driver named `mt6779-pinctrl`. The OF match table associates `mediatek,mt6779-pinctrl` with `mt6779_data`. Probe is delegated entirely to `mtk_paris_pinctrl_probe()`, which consumes the register calculations and pin descriptors from `mtk_pins_mt6779` to register pinctrl, GPIO, and EINT services. Runtime calls from the pinctrl subsystem are resolved by looking up a pin/register class in `mt6779_reg_cals` and then reading or updating the computed MMIO field.

## State And Persistence
All durable driver knowledge is static const table data. Runtime persistence is in the SoC registers that the Paris core writes for pin muxing, GPIO state, bias, drive, Schmitt, and EINT debounce/trigger behavior. The `ies_present` flag affects whether input-enable operations are expected to use explicit IES registers rather than being treated as absent.

## Dependencies And Integration Points
The file depends on `pinctrl-mtk-mt6779.h` for pin descriptors, alternate function definitions, and debounce-time data, and on `pinctrl-paris.h` for registration and pinconf callbacks. It integrates with OF resource naming, platform-driver matching, generic pinctrl state selection, gpiolib operations, and MediaTek EINT handling.

## Risks
The key risk is regional base mismatch. A wrong `_i_base` routes a field to a valid but unrelated IOCFG block, producing subtle electrical failures rather than an obvious probe error. The PU/PD/PUPD/R0/R1 tables are not uniform across all pins, so advanced pull correctness depends on matching pin coverage to `mtk_pinconf_adv_pull_*` expectations. EINT metadata must also match the header's EINT-capable pin list; otherwise interrupt consumers may get missing, duplicate, or incorrectly debounced lines.

## Test Signals
Validation should include successful driver binding with all eight register resources present, debugfs inspection for 203 pins and groups, GPIO direction/value readback across low and high pin numbers, pinmux tests on pins from each IOCFG region, pinconf read/write tests for bias/drive/Schmitt/input-enable settings, and EINT edge/debounce tests across multiple AP EINT lines. Device-tree schema and boot tests should confirm the `mediatek,mt6779-pinctrl` compatible selects this data, not another MediaTek variant.
