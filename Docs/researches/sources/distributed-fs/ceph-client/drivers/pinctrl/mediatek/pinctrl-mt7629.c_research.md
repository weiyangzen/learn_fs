# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7629.c

## Purpose
`pinctrl-mt7629.c` provides the MT7629 SoC pinctrl description for the common MediaTek Moore pinctrl framework. It maps 79 pins to register ranges, pin groups, device-tree functions, EINT metadata, and pin configuration callbacks.

## Important APIs, Types, And Data
`MT7629_PIN()` wraps `MTK_PIN()` with EINT mux value 0, a caller-supplied EINT number, and drive group `DRV_GRP1`. The register calculators cover mode, direction, data input/output, IES, Schmitt trigger, pull enable, pull select, drive strength, TDSEL, and RDSEL. Most non-GPIO pad controls are partitioned by broad pin ranges at offsets `0x1000` through `0x7600`, while GPIO mode/dir/di/do use the standard lower offsets.

`mt7629_pins` names pads for Wi-Fi 2G/5G interfaces, LEDs, watchdog, I2C, GPIO, UART, Ethernet PHY MDI pairs, SMI MDC/MDIO, PCIe, PWM, SPI, and UART0. Pin group arrays model ePHY/GPHY LEDs, I2C alternatives, SPI and optional WP/HOLD pins, UART data/control pairs, MDIO, PCIe reset/wake/clkreq, PWM, Wi-Fi front-end groups, serial NAND, and SPI NOR. `mt7629_functions` exposes `eth`, `i2c`, `led`, `pcie`, `pwm`, `spi`, `uart`, `watchdog`, `wifi`, and `flash`.

## Control Flow
`arch_initcall(mt7629_pinctrl_init)` registers a platform driver named `mt7629-pinctrl`. Device tree matching uses `mediatek,mt7629-pinctrl`. Probe is a single delegation: `mt7629_pinctrl_probe()` calls `mtk_moore_pinctrl_probe(pdev, &mt7629_data)`. No SoC-specific post-probe register writes are performed in this file.

## State And Persistence
The source owns no mutable driver state. The runtime state is hardware register state managed by the common pinctrl framework after the static `mt7629_data` descriptor is registered. `mt7629_data` indicates `gpio_m = 0`, `ies_present = true`, default register base names, rev1 bias callbacks, and rev1 drive callbacks.

## Dependencies And Integration Points
The file integrates with Linux platform driver discovery, device tree pinctrl consumers, MediaTek EINT, and generic pinconf/pinmux interfaces. `mt7629_eint_hw` defines 7 ports, AP EINT count equal to the number of pins, 16 debounce counters, and the MT2701 debounce timing table.

## Risks
Table accuracy is the main risk. The Wi-Fi group `mt7629_wf0_2g_pins` lists 9 pins but the visible `mt7629_wf0_2g_funcs` initializer has 8 entries, which is a metadata mismatch risk for group setup. As with all string-based pinctrl function tables, typos in group names would surface as device tree mux failures rather than obvious logic errors. The register maps use broad pin ranges, so one incorrect range boundary could affect multiple unrelated peripherals.

## Test Signals
Expected signals include successful compilation, successful probe for `mediatek,mt7629-pinctrl`, DTS pinctrl lookup success for Ethernet, Wi-Fi, flash, SPI, UART, I2C, PCIe, and LEDs, GPIO loopback tests for direction/value paths, EINT debounce tests, and pinconf get/set checks for pull, Schmitt, IES, drive, TDSEL, and RDSEL controls.
