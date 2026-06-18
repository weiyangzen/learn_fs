# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6765.c

## Purpose
This file is the MediaTek MT6765 pinctrl SoC description for the Paris pinctrl framework. It does not implement pinctrl algorithms itself; instead it gives the shared MediaTek pinctrl core enough static data to expose 203 pins as GPIOs, mux groups, pin configuration targets, and external interrupt lines for the `mediatek,mt6765-pinctrl` device-tree compatible.

## Important APIs, Types, And Functions
The file builds `struct mtk_pin_field_calc` arrays for every register class used by the SoC: mode, direction, data input/output, Schmitt trigger, pull-down, pull-up, transmit/receive select timing, drive strength, PUPD, R0, R1, and input-enable select. `PIN_FIELD_BASE()` and `PINS_FIELD_BASE()` wrap `PIN_FIELD_CALC()` for register bases selected by `_i_base`, with the plural form marking shared bit fields across a pin range.

`mt6765_reg_cals` maps the generic `PINCTRL_PIN_REG_*` enum slots to the MT6765 field arrays through `MTK_RANGE()`. `mt6765_eint_hw` declares the EINT controller layout: six ports, port mask `7`, 160 application-visible EINTs, 13 debounce counters, and `debounce_time_mt6765`. `mt6765_data` is the integration object consumed by `mtk_paris_pinctrl_probe()`: it points to `mtk_pins_mt6765`, the register calculations, EINT hardware, eight IOCFG base names, and the combo bias, raw drive, and advanced pull callbacks.

## Control Flow
Boot registration is simple. `arch_initcall(mt6765_pinctrl_init)` registers `mt6765_pinctrl_driver`. The platform bus matches `mediatek,mt6765-pinctrl`, attaches `mt6765_data` as match data, and calls `mtk_paris_pinctrl_probe()`. From that point, the shared Paris code maps the named register resources, registers pinctrl/gpio/eint providers, and uses the static range tables whenever consumers request mux, GPIO direction/value, bias, drive strength, Schmitt, timing, or EINT configuration.

## State And Persistence
There is no mutable software state in this file after registration. Runtime state is the hardware register contents written by the common pinctrl core. The source of persistence is the static register map: if a pin's base index, offset, bit start, bit width, or shared-field flag is wrong, all future pin configuration requests for that field persist to the wrong hardware location until reboot or reconfiguration.

## Dependencies And Integration Points
The driver depends on `pinctrl-mtk-mt6765.h` for the pin descriptors and debounce table, `pinctrl-paris.h` for the common probe and pinconf helpers, Linux platform-driver and OF matching infrastructure, and the device tree providing resources named `iocfg0` through `iocfg7`. It integrates with pinctrl consumers via generic pinctrl states, GPIO via the MediaTek common GPIO implementation, and interrupt consumers through the MediaTek EINT wiring.

## Risks
The major risk is table accuracy. MT6765 spreads configuration across eight IOCFG bases and many non-contiguous bit positions, so copy/paste mistakes can misroute a pin's bias, drive, input-enable, or timing control. The `npins` and `ngrps` values both derive from `ARRAY_SIZE(mtk_pins_mt6765)`, so header/table consistency is mandatory. Pull behavior depends on the combination of PU/PD plus PUPD/R0/R1 and advanced pull helpers; missing one of those register ranges can make some pins appear configurable while returning ineffective electrical settings.

## Test Signals
Useful signals include a boot log showing the platform driver binds without resource-name failures, pinctrl debugfs listing all MT6765 pins/groups, GPIO loopback tests for direction/data registers, device-tree pin state tests for alternate functions, bias and drive-strength readback through pinconf, EINT trigger/debounce tests across representative pins, and suspend/resume smoke tests for devices whose pins are configured before and after system sleep.
