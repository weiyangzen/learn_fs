# sources/distributed-fs/ceph-client/drivers/leds/flash/Kconfig

## Purpose
This Kconfig file defines flash and torch LED driver options that are only visible when `LEDS_CLASS_FLASH` is enabled. It covers GPIO/protocol flash parts, I2C flash controllers, PMIC/MFD flash blocks, and optional V4L2 flash LED class integration.

## Important APIs, Types, and Functions
The main symbols in this subset are `LEDS_AAT1290`, `LEDS_AS3645A`, `LEDS_KTD2692`, `LEDS_LM3601X`, `LEDS_MAX77693`, `LEDS_MT6360`, `LEDS_MT6370_FLASH`, `LEDS_QCOM_FLASH`, `LEDS_RT4505`, `LEDS_RT8515`, and `LEDS_SGM3140`. The file also defines nearby flash drivers such as `LEDS_SY7802` and `LEDS_TPS6131X`. Several entries use `depends on V4L2_FLASH_LED_CLASS || !V4L2_FLASH_LED_CLASS` so the LED driver can build whether V4L2 flash support is enabled or not.

## Control Flow
The whole file is wrapped in `if LEDS_CLASS_FLASH`. Each selected symbol maps to an object in `drivers/leds/flash/Makefile`. `select REGMAP_I2C` and `select LEDS_EXPRESSWIRE` pull helper code needed by particular drivers.

## State and Persistence
Selections persist in kernel configuration and determine build inclusion. Runtime flash timeout, torch current, strobe state, and V4L2 subdevice state are handled by the C drivers, not this file.

## Dependencies and Integration Points
Dependencies connect drivers to I2C, GPIO, OF, pinctrl, MFD parents, multicolor LED class, and V4L2 flash class. PMIC drivers depend on their MFD parent symbols (`MFD_MAX77693`, `MFD_MT6360`, `MFD_MT6370`, `MFD_SPMI_PMIC`). KTD2692 selects the LED ExpressWire helper.

## Risks and Edge Cases
Flash LED drivers often expose camera-facing V4L2 subdevices when available. Incorrect V4L2 dependency expressions can break either media-disabled or media-enabled builds. PMIC dependencies must match actual parent regmap providers. Since the file is inside `LEDS_CLASS_FLASH`, adding a driver that only uses plain LED class here would unnecessarily hide it.

## Test Signals
Run `allmodconfig`, `allyesconfig`, media-disabled, and PMIC-specific builds. Confirm each selected symbol produces its module and that V4L2-enabled builds register flash subdevice hooks without requiring V4L2 in media-disabled configurations.
