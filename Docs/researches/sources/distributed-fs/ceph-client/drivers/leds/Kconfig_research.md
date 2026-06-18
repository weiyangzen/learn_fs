# sources/distributed-fs/ceph-client/drivers/leds/Kconfig

## Purpose
This Kconfig file is the main LED subsystem configuration menu. It defines the framework-level symbols for LED core support, LED class devices, flash LEDs, multicolor LEDs, brightness hardware-change reporting, KUnit coverage, and a long list of concrete platform/I2C/SPI/MFD LED drivers. It also includes the subordinate blink, flash, RGB, trigger, and Simatic LED Kconfig files.

## Important APIs, Types, and Functions
The file is declarative Kconfig rather than C code. Its important "APIs" are symbols consumed by Makefiles and C preprocessor conditionals: `NEW_LEDS`, `LEDS_CLASS`, `LEDS_CLASS_FLASH`, `LEDS_CLASS_MULTICOLOR`, `LEDS_TRIGGERS`, `LEDS_EXPRESSWIRE`, and many `LEDS_*` driver symbols. It uses Kconfig primitives such as `menuconfig`, `config`, `depends on`, `select`, `default`, `source`, and `comment`.

## Control Flow
Configuration flow starts with helper symbols that can exist outside `NEW_LEDS`, then opens the `NEW_LEDS` menu. Enabling `NEW_LEDS` exposes framework classes and the driver menu. Driver symbols gate platform objects in `drivers/leds/Makefile`; subordinate files are sourced near the end so specialized blink, flash/torch, RGB, trigger, and Simatic drivers are only visible inside LED support.

## State and Persistence
Selected symbols persist in the kernel `.config` and determine whether LED framework code and drivers are built in, modular, or omitted. Runtime LED state is not handled here, but misconfiguration changes which runtime sysfs classes and device drivers can exist.

## Dependencies and Integration Points
The file integrates with architecture, bus, and subsystem symbols such as `GPIOLIB`, `I2C`, `SPI`, `OF`, `MFD_*`, `V4L2_FLASH_LED_CLASS`, `LEDS_CLASS_MULTICOLOR`, and `COMPILE_TEST`. `LEDS_EXPRESSWIRE` is intentionally outside `NEW_LEDS` because other subsystems can select it. The `source` lines are key integration points with `drivers/leds/blink/Kconfig` and `drivers/leds/flash/Kconfig`.

## Risks and Edge Cases
Incorrect `depends on` clauses can expose drivers without required bus/regmap/GPIO support or hide valid compile-test coverage. `select` use must remain conservative because it bypasses dependency checking for selected symbols. Moving subordinate `source` lines outside `if NEW_LEDS` would change menu visibility and build behavior. Framework symbols are shared by many drivers, so changing their type or defaults has broad build fallout.

## Test Signals
Useful signals are `olddefconfig`, `allyesconfig`, `allmodconfig`, and targeted `COMPILE_TEST` builds. Kconfig warnings about unmet direct dependencies, recursive dependencies, or unknown symbols are high-value signals. Runtime confirmation comes from the expected `/sys/class/leds`, flash class attributes, multicolor class attributes, and trigger availability matching the selected symbols.
