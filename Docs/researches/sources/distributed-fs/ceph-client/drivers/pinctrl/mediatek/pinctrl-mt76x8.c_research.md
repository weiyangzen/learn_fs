# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt76x8.c

## Purpose
`pinctrl-mt76x8.c` is an older Ralink/MTMIPS-style pinmux driver for MT76x8, MT7620-compatible, and RT2880-compatible pin controllers. Unlike the Moore drivers in this group, it does not describe per-pin register field calculators; it describes mux groups controlled by shared GPIO mode bitfields.

## Important APIs, Types, And Data
The file includes Linux module/platform/of headers and `pinctrl-mtmips.h`. It uses `struct mtmips_pmx_func` and `struct mtmips_pmx_group` through helper macros `FUNC()`, `GRP()`, and `GRP_G()`. The `MT76X8_GPIO_MODE_*` constants define bit shifts in the SoC GPIO mode register, while `MT76X8_GPIO_MODE_MASK` defines two-bit mux selectors for most groups.

Function arrays enumerate alternatives for PWM, UART, I2C, REFCLK, PERST, watchdog, SPI, SD, I2S, SPI chip-select, SPI slave, GPIO/PCIe, and Ethernet LED pins. The `mt76x8_pinmux_data` array registers each mux group with its mode mask, GPIO fallback value, shift, and available functions, ending with a zero sentinel.

## Control Flow
Runtime flow is minimal. `core_initcall_sync(mt76x8_pinctrl_init)` registers `mt76x8_pinctrl_driver`. The platform driver matches `ralink,mt76x8-pinctrl`, `ralink,mt7620-pinctrl`, and `ralink,rt2880-pinmux`. Probe calls `mtmips_pinctrl_init(pdev, mt76x8_pinmux_data)`, which is responsible for registering the pinmux provider and applying group selections.

## State And Persistence
The file owns static mux metadata only. Runtime mux state lives in the MTMIPS GPIO mode register and is manipulated by the shared MTMIPS pinctrl implementation. The `enabled` fields in the MTMIPS structs are part of the common framework state, not directly mutated by this file.

## Dependencies And Integration Points
This file integrates with the MTMIPS pinctrl subsystem rather than the MediaTek Moore v2 subsystem. It depends on platform driver matching from device tree and on the shared MTMIPS implementation to interpret group masks, shifts, and GPIO fallback values. It exports module device-table metadata for OF autoloading.

## Risks
The table packs many unrelated muxes into one global mode register, so incorrect mask/shift values can corrupt adjacent mux settings. Some groups share pins or offer debug/JTAG/UTIF alternatives, making board DTS selection important. The compatible list includes older SoCs, so behavior must remain compatible with legacy bindings and any subtle register-layout differences covered by the common MTMIPS layer.

## Test Signals
Useful tests are successful probe for all listed compatible strings, boot-time pinctrl lookup success on MT76x8 board DTS files, mux checks for UART0/1/2, SPI, I2C, SDXC, PWM, I2S/PCM, WDT, REFCLK, PCIe/PERST, and Ethernet LED groups, plus GPIO fallback tests for groups where `GRP_G()` defines an explicit GPIO value.
