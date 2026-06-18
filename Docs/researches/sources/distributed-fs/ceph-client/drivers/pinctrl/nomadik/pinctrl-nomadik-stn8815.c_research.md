# sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-nomadik-stn8815.c

## Purpose
This file is the STN8815 SoC data provider for the common Nomadik pinctrl driver. It lists 124 routed GPIO-capable pins, maps each one to a `GPIO<number>_<ball>` pinctrl descriptor, defines the STN8815 alternate-function groups, and declares the function-to-group relationships for UART, MMC/SD, I2C, CLCD, and USB pinmuxing.

## Important APIs, types, and functions
The only exported entry point is `nmk_pinctrl_stn8815_init()`, which assigns `nmk_stn8815_soc` to the common driver's SoC pointer. `nmk_stn8815_soc` references `nmk_stn8815_pins`, `nmk_stn8815_groups`, and `nmk_stn8815_functions`. The group table uses `NMK_PIN_GROUP()` with `NMK_GPIO_ALT_A`, `NMK_GPIO_ALT_B`, and `NMK_GPIO_ALT_C`; the function table is built with local `STN8815_FUNC_GROUPS()` and `FUNCTION()` macros.

## Control flow
The file is passive table data. The common Nomadik probe path selects it when device-tree match data identifies `PINCTRL_NMK_STN8815`. Pinctrl group callbacks expose the pin arrays, function callbacks expose the `u0`, `mmcsd`, `u1`, `i2c1`, `i2c0`, `i2cusb`, `clcd`, and `usb` functions, and the common mux callback writes the selected alternate function into the corresponding GPIO bank registers.

## State and persistence behavior
The tables are immutable and do not allocate or mutate state. Hardware persistence occurs later through `pinctrl-nomadik.c` when muxing or pin configuration is applied. Unlike DB8500, this SoC data has no ALT-Cx PRCM GPIOCR extension table, so the common driver treats absent PRCM data as acceptable for STN8815 and falls back to ordinary ALT-C handling.

## Dependencies and integration points
The file depends on pinctrl core descriptors and Nomadik structures from `linux/gpio/gpio-nomadik.h`. It integrates with the common Nomadik pinctrl driver and with device trees that reference the exact function and group names, such as `u0txrx_a_1`, `mmcsd_a_1`, `usbfs_b_1`, and `usbhs_c_1`.

## Risks
The file's main risks are table accuracy and string consistency. Function group strings are not compiler-validated against group definitions. The STN8815 pin list notes that GPIOs 124-127 are not routed; tests and board descriptions must not assume a full 128-pin contiguous external pad set. Since the common driver may operate without PRCM on STN8815, accidental addition of ALT-Cx-style requirements would need corresponding core-driver and SoC-data updates.

## Test signals
Compile coverage for the Nomadik driver, STN8815 probe without a PRCM base, pinctrl debugfs enumeration, and board-level mux tests for UART0 modem pins, MMC/SD split groups, I2C, CLCD high data pins, USB FS, and USB HS are the strongest validation signals.
