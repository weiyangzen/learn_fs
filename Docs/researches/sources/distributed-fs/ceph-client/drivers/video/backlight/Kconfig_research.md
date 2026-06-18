# sources/distributed-fs/ceph-client/drivers/video/backlight/Kconfig

## Purpose
This Kconfig file defines the LCD and backlight support menu, including the generic LCD/backlight class devices and a broad set of panel, PMIC, GPIO, PWM, LED, platform, and I2C backlight drivers.

## Important APIs, types, and functions
Important framework symbols are `LCD_CLASS_DEVICE` and `BACKLIGHT_CLASS_DEVICE`. The listed work item drivers map to symbols such as `LCD_AMS369FG06`, `BACKLIGHT_AW99706`, `BACKLIGHT_APPLE`, `BACKLIGHT_APPLE_DWI`, `BACKLIGHT_ADP5520`, `BACKLIGHT_ADP8860`, `BACKLIGHT_ADP8870`, `BACKLIGHT_88PM860X`, `BACKLIGHT_AAT2870`, `BACKLIGHT_AS3711`, `BACKLIGHT_BD6107`, and `BACKLIGHT_ARCXCNN`. Many entries add `depends on` subsystem constraints and `select` helper libraries such as `REGMAP_I2C`, `NEW_LEDS`, or `LEDS_CLASS`.

## Control flow
LCD panel options are visible only under `LCD_CLASS_DEVICE`; backlight options are visible only under `BACKLIGHT_CLASS_DEVICE`. Per-driver dependencies constrain platform buses, MFD parents, I2C/SPI, ACPI, OF, GPIO, PWM, and architecture support. Kconfig selections then drive the local Makefile.

## State and persistence
The file contributes build-time configuration state in `.config`; no runtime state exists.

## Dependencies and integration points
It integrates low-level display control with the Linux driver model by ensuring core class support and bus/helper dependencies are available before individual drivers compile.

## Risks and test signals
Risks are under-specified dependencies, missing selects for helper APIs, stale help text/module names, and options visible on impossible hardware. Test signals include randconfig builds, `COMPILE_TEST` coverage, module builds for each option, and dependency audits against each driver's includes and API calls.
