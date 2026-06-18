# sources/distributed-fs/ceph-client/drivers/gpio/gpio-bd71815.c

## Purpose
This platform driver exposes BD71815/BD71817 PMIC GPO pins as gpiolib lines. The hardware is output-only, with an optional hidden second GPO that is disabled unless explicitly enabled by device property.

## Important APIs, types, and functions
`struct bd71815_gpio` stores the gpiochip, device, and parent regmap. Operations are `bd71815gpo_get()`, `bd71815gpo_set()`, `bd71815_gpio_set_config()`, `bd71815gpo_direction_get()`, and `bd71815_init_valid_mask()`. Probe uses `dev_get_regmap()` from the parent MFD and registers a template gpiochip.

## Control flow
Probe copies the output-only chip template, sets `ngpio` to 1 by default or 2 when `rohm,enable-hidden-gpo` is present, installs the valid-mask callback, assigns the parent regmap, and registers the chip. Set/get operate on `BD71815_REG_GPO`; pin config selects open-drain or CMOS drive.

## State and persistence behavior
The GPO output and drive state live in the PMIC GPO register. The driver keeps no cache. The valid mask/line count is derived from firmware property at probe.

## Dependencies and integration points
The driver depends on the ROHM BD71815 MFD regmap, platform device creation, gpiolib, and pinconf drive-mode configs. The GPIO chip parent is the MFD parent so firmware properties are read from the PMIC node.

## Risks and edge cases
The hidden GPO may be physically tied to ground, so enabling it can be unsafe on boards not designed for it. The driver sets `ngpio` to 1 by default because legacy sysfs may ignore `valid_mask`. There is no input or IRQ support.

## Test signals
Test default one-line exposure, hidden GPO opt-in, output-only direction reporting, set/get register bits, open-drain/push-pull pinconf writes, and missing parent regmap behavior.
