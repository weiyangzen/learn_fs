# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7622.c

## Purpose
`pinctrl-mt7622.c` is the MediaTek MT7622 SoC pinctrl description for the common "Moore" pinctrl core. It is not an algorithm-heavy driver; it supplies the static pin, register-field, pin group, pin function, external interrupt, and pin configuration callback metadata consumed by `mtk_moore_pinctrl_probe()`.

## Important APIs, Types, And Data
The file includes `pinctrl-moore.h` and relies on shared types such as `struct mtk_pin_field_calc`, `struct mtk_pin_reg_calc`, `struct mtk_pin_desc`, `struct group_desc`, `struct pinfunction`, `struct mtk_eint_hw`, and `struct mtk_pin_soc`. `MT7622_PIN()` wraps `MTK_PIN()` with EINT mux value 1, EINT number equal to the GPIO number, and drive group `DRV_GRP0`.

The register calculator arrays map pin numbers 0 through 102 to MT7622 register offsets and bit fields. Covered logical registers include mode, direction, input, output, slew rate, Schmitt trigger, pull-up, pull-down, E4/E8 drive selection, TDSEL, and RDSEL. `mt7622_reg_cals` binds these arrays to `PINCTRL_PIN_REG_*` indices.

`mt7622_pins` names 103 pads, including GPIO, I2S, SPI, I2C, Ethernet, NAND/eMMC, PMIC, PCIe, PWM, UART, watchdog, and LED pads. The many `*_pins` and `*_funcs` arrays define pinmux groups, and `mt7622_groups` exposes them through `PINCTRL_PIN_GROUP()`. `mt7622_functions` then publishes user-facing mux functions such as `antsel`, `emmc`, `eth`, `i2c`, `i2s`, `ir`, `led`, `flash`, `pcie`, `pmic`, `pwm`, `sd`, `spi`, `tdm`, `uart`, and `watchdog`.

## Control Flow
The only runtime flow in this file is platform driver registration and probe. `arch_initcall(mt7622_pinctrl_init)` registers `mt7622_pinctrl_driver`. Device tree matching uses compatible string `mediatek,mt7622-pinctrl`. `mt7622_pinctrl_probe()` passes the static `mt7622_data` descriptor to `mtk_moore_pinctrl_probe()`, which performs the actual pinctrl, GPIO, pinmux, pinconf, and EINT registration.

## State And Persistence
The file owns no dynamic or persistent runtime state. All state is static constant hardware description data. Runtime pin state is maintained in SoC registers through the common pinctrl core. The descriptor selects `gpio_m = 1`, `ies_present = false`, default MediaTek register base names, standard bias callbacks, and standard drive callbacks.

## Dependencies And Integration Points
Integration is through Linux platform-driver probing, device tree compatible matching, the common MediaTek v2 pinctrl register calculator, pinmux group/function descriptors, and the MediaTek EINT subsystem. `mt7622_eint_hw` declares 7 EINT ports, AP EINT count equal to the pin count, 20 debounce counters, and `debounce_time_mt6765`.

## Risks
The file is table-driven, so the main risks are silent metadata mistakes: wrong register offsets, wrong bit widths, mismatched pin/function array lengths, or group names omitted from function lists. Because `ies_present` is false while many newer SoCs expose IES fields, any board-level expectation of per-pin input-enable control must match MT7622 hardware behavior. Pin groups also contain many overlapping alternatives, so device tree consumers must select non-conflicting groups.

## Test Signals
Useful validation signals are compile coverage for array and descriptor declarations, boot-time probe success for `mediatek,mt7622-pinctrl`, GPIO direction/input/output tests across several banks, pinmux smoke tests for Ethernet, SPI, UART, I2C, PCIe reset/wake, and storage groups, EINT debounce tests, and pinconf get/set tests for bias and drive callbacks.
