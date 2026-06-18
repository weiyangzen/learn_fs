# sources/distributed-fs/ceph-client/drivers/gpio/gpio-bd72720.c

## Purpose
This platform driver exposes GPIO-capable pins on ROHM BD72720 and BD73900 PMICs. Because many pin functions are OTP-selected and unreadable at runtime, device-tree properties declare which pins are valid GPIO inputs or outputs.

## Important APIs, types, and functions
`struct bd72720_gpio` stores the gpiochip, device, regmap, and `gpio_is_input` bitmap. GPIO operations are `bd72720gpio_get()`, `bd72720gpo_set()`, `bd72720_gpio_set_config()`, and `bd72720gpo_direction_get()`. `bd72720_valid_mask()` parses `rohm,pin-dvs0`, `rohm,pin-dvs1`, `rohm,pin-exten0`, `rohm,pin-exten1`, and `rohm,pin-fault_b`.

## Control flow
Probe copies the 6-line chip template, gets the parent regmap, and registers. During valid-mask initialization, EPDEN is always exposed, optional properties add DVS/EXTEN/FAULT_B pins as GPI or GPO where supported, and GPI pins are recorded in `gpio_is_input`. Get reads either interrupt source bits for inputs or per-pin control registers for outputs.

## State and persistence behavior
Output value and drive state live in per-pin PMIC control registers. Input state is read from `BD72720_REG_INT_ETC1_SRC`. The driver's `gpio_is_input` bitmap and valid mask are runtime interpretations of firmware-declared OTP configuration.

## Dependencies and integration points
The driver depends on the BD72720 MFD regmap, firmware node string properties, gpiolib, and pinconf drive configs. It is registered as `bd72720-gpio` with asynchronous preferred probing.

## Risks and edge cases
Device-tree must match OTP programming; the driver cannot verify it. Only DVS0/DVS1 support GPI mode; other properties set to `gpi` are warned and ignored. Setting or configuring input pins fails. The module description mentions BD73900 while IDs expose `bd72720-gpio`.

## Test signals
Test valid-mask parsing for missing, `gpi`, `gpo`, and invalid properties, input/output direction reporting, EPDEN availability, output set/get registers, input source reads, and drive open-drain/CMOS config.
