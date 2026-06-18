# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7981.c

## Purpose
`pinctrl-mt7981.c` describes MT7981 pin control for the MediaTek Moore framework. It provides multi-base register-field metadata, 57 pin descriptors, mux group/function tables for networking-oriented peripherals, EINT metadata, and combined bias/pull handling.

## Important APIs, Types, And Data
`MT7981_PIN()` wraps `MTK_PIN()` with EINT mux 0, EINT number equal to the pin number, and `DRV_GRP4`. Local `PIN_FIELD_BASE()` and `PINS_FIELD_BASE()` helpers extend `PIN_FIELD_CALC()` with an explicit register base index, because MT7981 pin configuration is spread across `"gpio"`, `"iocfg_rt"`, `"iocfg_rm"`, `"iocfg_rb"`, `"iocfg_lb"`, `"iocfg_bl"`, `"iocfg_tm"`, and `"iocfg_tl"` bases.

Register calculators cover mode, direction, data input/output, SMT, IES, PU, PD, drive, PUPD, R0, and R1. `mt7981_pull_type` selects either PUPD/R1/R0 style pulls for pins 0-39 or separate PU/PD style pulls for pins 40-56. Pins include WPS/reset, watchdog, PCIe reset/wake/clkreq, JTAG and wireless-offload JTAG, USB VBUS, PWM, SPI0/1/2, UART0, MDIO, GBE interrupt/reset, and Wi-Fi front-end pins.

Function groups cover WA/WM debug, DFD, JTAG, PTA, PCM, UDI, USB, antenna select, Ethernet/MDIO/Wi-Fi modes, I2C, LEDs, PWM, SPI, UART, watchdog, flash, and PCIe.

## Control Flow
`arch_initcall(mt7981_pinctrl_init)` registers `mt7981_pinctrl_driver`. Matching uses `mediatek,mt7981-pinctrl`; probe delegates to `mtk_moore_pinctrl_probe(pdev, &mt7981_data)`. All hardware programming after probe is handled by common pinctrl operations using the supplied register tables and callbacks.

## State And Persistence
State is static descriptor data plus live SoC register state managed by the common framework. `mt7981_data` enables IES support, combined pull handling through `pull_type`, `mtk_pinconf_bias_set_combo()`, and `mtk_pinconf_bias_get_combo()`, rev1 drive callbacks, and advanced pull callbacks. The EINT block declares 7 ports, AP EINT count equal to the pin count, and 16 debounce counters.

## Dependencies And Integration Points
The file depends on accurate base-name ordering in `mt7981_pinctrl_register_base_names`, the Moore probe path, generic pinmux/pinconf APIs, MediaTek EINT, and board device trees that use the named groups/functions.

## Risks
Several visible table anomalies are risk signals: `mt7981_wa_aice_groups` references group strings such as `wm_aice1_1` and `wm_aice1_2`, while the declared group names are `wm_aice1` and `wm_aice2`; some group comments do not match group purposes; `mt7981_ant_sel_pins` lists more entries than the visible funcs array. These are likely to surface as missing pinctrl groups or bad group initialization rather than compile-time logic failures. Multi-base register indexing also makes off-by-one base selection a high-impact risk.

## Test Signals
Validation should include compile testing, successful probe for `mediatek,mt7981-pinctrl`, pinctrl lookup tests for every DTS function name, GPIO/value tests, IES/SMT tests, combo bias tests over both pull-type classes, drive-strength tests, and peripheral smoke tests for SPI flash/SNFI/eMMC, MDIO, PCIe, UART, I2C, LEDs, watchdog, USB VBUS, and Wi-Fi front-end modes.
