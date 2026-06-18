<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-lp87565.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-lp87565.c

## Purpose
`gpio-lp87565.c` exposes three GPIO pins on TI LP87565-Q1 PMIC variants using the parent regmap.

## Important APIs, types, and functions
`struct lp87565_gpio` holds a gpiochip and regmap. Request configures each pin's function mux to GPIO mode. Direction, get, set, and drive-mode configuration operate on `LP87565_REG_GPIO_IN`, `OUT`, `CONFIG`, and `PIN_FUNCTION`.

## Control flow
Probe copies a gpiochip template, obtains the parent MFD regmap, and registers three can-sleep lines. Request for offsets 0-2 sets the corresponding `GPIO*_SEL` bit. Direction output writes the value first, then sets the direction bit.

## State and persistence behavior
All state is in PMIC registers; no software cache is kept. Direction is read from `GPIO_CONFIG`, input values from `GPIO_IN`, and output values from `GPIO_OUT`.

## Dependencies and integration points
It is a platform child `lp87565-gpio`, depends on `linux/mfd/lp87565.h` register definitions and regmap, and exposes pinconf open-drain/push-pull.

## Risks and edge cases
Requesting a line changes pin function away from EN pin mode. The open-drain bit offset is derived from `LP87565_GPIO1_OD`, so header definition changes directly affect all offsets. Invalid offsets fail only in request, while gpiolib normally bounds operation offsets.

## Test signals
Test mux request for each pin, input/output direction and value, drive config, regmap error paths, and interaction with PMIC enable-pin functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-lp87565.c -->
