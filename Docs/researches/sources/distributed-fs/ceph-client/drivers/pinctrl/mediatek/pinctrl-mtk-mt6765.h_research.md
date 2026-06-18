# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6765.h

## Purpose

`pinctrl-mtk-mt6765.h` defines the pin descriptor table for the MediaTek MT6765 Paris-generation pinctrl driver. It contributes `mtk_pins_mt6765[]`, a 180-entry `struct mtk_pin_desc` array covering GPIO0 through GPIO179. Each descriptor gives the Paris common driver the pin number, name, EINT mapping, drive group class, and mux-function list for that pin.

The file is descriptor-only and is included by `pinctrl-mt6765.c`, which supplies the register field calculators and platform-driver registration for `mediatek,mt6765-pinctrl`.

## Important APIs, Types, And Data

This header uses `pinctrl-paris.h` and the v2 common data model:

- `MTK_PIN(number, name, eint, drv_n, functions...)` expands into `struct mtk_pin_desc`.
- `MTK_EINT_FUNCTION(eint_m, eint_n)` fills `struct mtk_eint_desc`.
- `DRV_GRP0` and `DRV_GRP4` classify drive-strength handling. The table uses 175 pins in `DRV_GRP4` and 5 pins in `DRV_GRP0`.
- `MTK_FUNCTION(muxval, name)` lists mux options. MT6765 uses mux values 0 through 7, and mux value 0 is GPIO mode.

The table has 180 `MTK_PIN` descriptors and 836 function descriptors. It exposes peripheral families including UART, clock monitor outputs, modem interrupt and UART pins, I2S/audio, SPI and SCP SPI, keypad rows/columns, MSDC, MIPI, antenna selection, connectivity, BPI, JTAG, PWM, and debug monitor functions. EINT data has 180 entries, with 114 real EINT mappings and 66 `NO_EINT_SUPPORT` entries.

## Control Flow And Runtime Use

`pinctrl-mt6765.c` includes this header and sets `.pins = mtk_pins_mt6765`, `.npins = ARRAY_SIZE(mtk_pins_mt6765)`, and `.ngrps = ARRAY_SIZE(mtk_pins_mt6765)` in `mt6765_data`. The platform driver matches `mediatek,mt6765-pinctrl` and probes through `mtk_paris_pinctrl_probe`.

The Paris common driver builds pin groups from the descriptors, resolves mux selectors from the per-pin function arrays, and uses the `.reg_cal` tables in the `.c` file for MODE, DIR, DI, DO, SMT, PD, PU, TDSEL, RDSEL, DRV, PUPD, R0, R1, and IES fields. The header supplies the semantic pin/function choices; the `.c` file supplies how those choices map to register addresses and bits.

## State And Persistence Behavior

The header stores compile-time static descriptor data and no mutable state. The function arrays are compound literals embedded in each `MTK_PIN` initializer and are consumed as read-only capability descriptions. Runtime state is maintained by the Paris pinctrl instance, GPIO chip, EINT subsystem, and hardware registers across the named IO configuration bases.

## Dependencies And Integration Points

The direct dependency is `pinctrl-paris.h`, which brings in `pinctrl-mtk-common-v2.h`, Linux pinctrl/pinmux/pinconf headers, and EINT support. The key companion integration is `pinctrl-mt6765.c`, whose `mt6765_pinctrl_register_base_names` are `iocfg0` through `iocfg7` and whose `mt6765_eint_hw` advertises 160 AP EINTs, 6 ports, and 13 debounce counters.

The SoC data uses generic Paris helpers such as `mtk_pinconf_bias_set_combo`, `mtk_pinconf_drive_set_raw`, and advanced pull helpers. Device trees must provide compatible pinctrl nodes with the expected base resources and function names that match this table.

## Risks And Edge Cases

The biggest risk is mismatch between this semantic table and the register calculators in `pinctrl-mt6765.c`. Pin numbers, drive groups, and EINT numbers must stay aligned with field ranges. Pins 176-178 are named GPIO-only and have `NO_EINT_SUPPORT`; pin 179 has EINT 151, so tail-end EINT coverage is not simply contiguous. Some mux lists omit certain numeric mux values, which is valid but easy to misread during edits.

Function names are binding-facing strings used by DTS pinctrl states and debug output. A typo in a bus name such as `SCP_SPI`, `MSDC`, `CONN`, `ANT_SEL`, `BPI_BUS`, or `DBG_MON` can make an otherwise correct numeric mux inaccessible by name. Incorrect drive group assignment can produce wrong electrical drive-strength behavior even when muxing works.

## Test Signals

Test signals include a clean build, successful `mt6765-pinctrl` probe, debugfs showing 180 pins/groups, and valid pinmux application for UART, SPI, I2S, keypad, MSDC, connectivity, and debug monitor states used by board DTS files. EINT tests should cover both real mappings and `NO_EINT_SUPPORT` rejection. Pinconf tests should cover bias combo, raw drive strength, advanced pull fields, and register-base selection across `iocfg0` through `iocfg7`.
