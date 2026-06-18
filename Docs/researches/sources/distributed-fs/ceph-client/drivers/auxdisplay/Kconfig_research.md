<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/auxdisplay/Kconfig

## Purpose

This Kconfig file defines auxiliary display driver configuration, including character LCD cores, HD44780-compatible displays, parallel-port panel/keypad options, graphical LCD support, line-display helpers, I2C LED/display controllers, GPIO seven-segment displays, and the ARM Versatile/RealView character LCD driver.

## Important APIs, types, and functions

The central menu symbol is `AUXDISPLAY`. Important child symbols include `CHARLCD`, `HD44780_COMMON`, `HD44780`, `LCD2S`, `PARPORT_PANEL`, many `PANEL_*` tuning options, `PANEL_CHANGE_MESSAGE`, `PANEL_BOOT_MESSAGE`, backlight choice symbols, `KS0108`, `CFAG12864B`, `LINEDISP`, `IMG_ASCII_LCD`, `HT16K33`, `MAX6959`, `SEG_LED_GPIO`, `ARM_CHARLCD`, and deprecated `PANEL`.

## Control flow

Kconfig first gates the submenu on `AUXDISPLAY`. Nested `if PARPORT_PANEL` exposes detailed panel wiring options only for custom profiles. Several symbols select common cores (`CHARLCD`, `HD44780_COMMON`, `LINEDISP`) while concrete drivers add platform dependencies such as `I2C`, `FB`, `PARPORT_PC`, `GPIOLIB`, `PLAT_VERSATILE`, or `COMPILE_TEST`.

## State and persistence behavior

There is no runtime state. The persistent effect is `.config` symbol state, which controls compiled objects and built-in/module selection. Some options also become compile-time defaults for panel dimensions, pin wiring, messages, and refresh rates.

## Dependencies and integration points

This file integrates auxdisplay drivers with Kbuild, framebuffer, input, LED, backlight, regmap, GPIO, I2C, parport, platform, and MFD dependencies. It also preserves a deprecated compatibility symbol `PANEL` that selects the newer menu path.

## Risks

The main risks are dependency/selection drift and user-visible config ABI changes. Incorrect `select` relationships can build concrete drivers without their common cores. Numeric panel options are compile-time hardware ABI for legacy devices; changing defaults can break existing installations. High refresh rates for slow LCDs are explicitly risky.

## Test signals

Run allmodconfig/allyesconfig and targeted configs for each major auxdisplay driver, verify menu visibility with dependencies missing, confirm selected common objects link, and build deprecated `PANEL` configs for compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/Kconfig -->
