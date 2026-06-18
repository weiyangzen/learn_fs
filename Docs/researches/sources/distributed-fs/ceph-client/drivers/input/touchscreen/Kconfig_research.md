# sources/distributed-fs/ceph-client/drivers/input/touchscreen/Kconfig

## Purpose
This Kconfig file defines the touchscreen driver menu and configuration symbols for a broad set of serial, I2C, SPI, USB, MFD, IIO, AC97, platform, and SoC touchscreen controllers.

## Important APIs, types, and functions
The top-level `INPUT_TOUCHSCREEN` bool gates all child options. Child symbols include concrete drivers such as `TOUCHSCREEN_88PM860X`, `TOUCHSCREEN_ADS7846`, `TOUCHSCREEN_ATMEL_MXT`, `TOUCHSCREEN_GOODIX`, `TOUCHSCREEN_USB_COMPOSITE`, `TOUCHSCREEN_WM97XX`, and many others, plus helper/core symbols such as `TOUCHSCREEN_GOODIX_BERLIN_CORE`, `TOUCHSCREEN_TSC200X_CORE`, and feature booleans such as `TOUCHSCREEN_TSC2007_IIO`.

## Control flow
When the touchscreen menu is enabled, each config entry applies dependencies, selects helper libraries such as `REGMAP_I2C`, `REGMAP_SPI`, `FW_LOADER`, `CRC_*`, `VIDEOBUF2_*`, `SERIO`, or `USB`, and describes module names. Some entries are hidden core symbols selected by bus-specific options, and several USB composite protocol options default to `y` under `TOUCHSCREEN_USB_COMPOSITE`.

## State and persistence
All state is build configuration stored in `.config`. The symbols determine which source files are compiled and which helper subsystems are pulled in. There is no runtime state in this file.

## Dependencies and integration points
This file integrates touchscreen drivers with the broader kernel configuration graph: bus subsystems, MFD parents, architecture guards, GPIO, OF/ACPI, IIO, HWMON, media/V4L, thermal, AC97, and COMPILE_TEST. It must stay synchronized with `drivers/input/touchscreen/Makefile`.

## Risks
With many options, dependency drift is the main risk: missing selects can break builds, excessive selects can force unwanted subsystems, and architecture-only dependencies can reduce compile coverage. Core/helper split symbols must remain hidden or selected consistently. Module-name help text can become stale when Makefile objects change.

## Test signals
Use allmodconfig, allyesconfig, randconfig, and COMPILE_TEST builds to catch dependency issues. Specifically test bus split families such as AD7879, Goodix Berlin, Cypress TTSP, TSC200x, WM97xx, and USB composite protocol booleans, plus serial options that must select `SERIO`.
