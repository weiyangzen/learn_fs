# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7988.c

## Purpose
`pinctrl-mt7988.c` describes MT7988 pin control for the MediaTek Moore pinctrl framework. It maps 84 pins across several IO configuration register pages and provides extensive mux metadata for Ethernet, PCIe, flash, UART, JTAG, I2C, LEDs, USB, audio, and debug functions.

## Important APIs, Types, And Data
The file defines `enum mt7988_pinctrl_reg_page` for `"gpio"`, `"iocfg_tr"`, `"iocfg_br"`, `"iocfg_rb"`, `"iocfg_lb"`, and `"iocfg_tl"` register pages. `MT7988_PIN()` wraps `MTK_PIN()` with EINT mux 0, EINT number equal to the pin number, and drive group `DRV_GRP4`. `PIN_FIELD_BASE()` and `PINS_FIELD_BASE()` provide explicit register-base selection for field calculators.

Register calculators cover mode, direction, data input/output, IES, SMT, PU, PD, drive, PUPD, R0, and R1. `mt7988_pull_type` mixes PUPD/R1/R0, separate PU/PD, and PD-only pull models depending on pin. Pin descriptors name UARTs, SMI/MDIO, PCIe wake/clkreq/perst, watchdog, PMIC/I2C, SPI0/1/2, eMMC, PCM/I2S, JTAG, USB VBUS, Ethernet LEDs, GPIO, and UART1/2 pads.

The group table is broad: TOPS/WO JTAG, DFD, many I2C and PHY-I2C aliases, MDIO, PCIe sideband and PHY I2C pins, PMIC, watchdog, SPI, SNFI/eMMC/SD, UART/TOPS UART/WO UART, UDI, I2S/PCM, Ethernet LEDs, PWM, and USB VBUS. `mt7988_functions` exports audio, jtag, int_usxgmii, pwm, dfd, i2c, eth, pcie, pmic, watchdog, spi, flash, uart, udi, usb, and led functions.

## Control Flow
`arch_initcall(mt7988_pinctrl_init)` registers the `mt7988-pinctrl` platform driver. It matches `mediatek,mt7988-pinctrl`, then `mt7988_pinctrl_probe()` delegates to `mtk_moore_pinctrl_probe(pdev, &mt7988_data)`.

## State And Persistence
The file owns static tables only. Live pin state persists in hardware registers through common pinctrl operations. `mt7988_data` enables IES, combo bias callbacks, rev1 drive callbacks, advanced pull callbacks, and EINT metadata with 7 ports and 16 debounce counters.

## Dependencies And Integration Points
The driver depends on exact register-base resource ordering, shared Moore pinctrl logic, MediaTek EINT, generic pinconf/pinmux APIs, and DTS references to the published function/group strings. Its multi-base register mapping is central to pinconf correctness.

## Risks
Several string-table hazards are visible: duplicate group names appear in `mt7988_groups` such as repeated `tops_uart0_0` and repeated `net_wo*_uart_txd_0` names for later pin alternatives; `mt7988_uart_groups` references `ops_uart0_1` and `ops_uart1_1`, while the declared names are `tops_uart0_1` and `tops_uart1_1`; `mt7988_led_groups` references `wf5g_led0` and `wf5g_led1`, which are not present in the visible group table. These can cause runtime pinctrl lookups to fail even if the file compiles. Multi-base field offsets and mixed pull models are additional high-risk areas.

## Test Signals
Testing should include build coverage, boot-time probe success, DTS pinctrl lookup tests for all exported function names, GPIO direction/value tests, EINT debounce tests, combo-bias tests for PUPD, PU/PD, and PD-only pins, drive-strength tests, and hardware smoke tests for PCIe sideband signals, MDIO, Ethernet LEDs, SPI/SNFI/eMMC/SD, UART/TOPS UART, I2C/PHY I2C, watchdog, PMIC, USB VBUS, PCM/I2S, and debug/JTAG groups.
