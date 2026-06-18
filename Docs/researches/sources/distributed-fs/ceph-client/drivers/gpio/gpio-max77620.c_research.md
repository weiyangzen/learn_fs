<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max77620.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-max77620.c

## Purpose
`gpio-max77620.c` provides GPIO and nested IRQ support for MAX77620 and MAX20024 PMIC GPIO blocks.

## Important APIs, types, and functions
`struct max77620_gpio` stores the gpiochip, regmap, device, IRQ bus mutex, per-line IRQ type, and enabled flags. GPIO callbacks manage direction, get, set, drive config, and debounce. IRQ callbacks include parent threaded handler, mask/unmask, set_type, bus lock/sync, and hardware initialization that disables bootloader-left interrupts.

## Control flow
Probe obtains the parent PMIC data and platform IRQ, allocates state, initializes the gpiochip, configures a threaded simple child irqchip, registers the gpiochip, then requests the parent threaded IRQ. The parent handler reads `IRQ_LVL2_GPIO`, iterates pending bits, and handles nested IRQs. Bus sync writes either the cached trigger type or zero into each GPIO config interrupt mask.

## State and persistence behavior
GPIO direction/value/drive/debounce live in per-GPIO PMIC config registers. IRQ enable and type are cached in arrays until bus sync writes them. Hardware IRQ masks are reset to disabled during gpiochip IRQ init.

## Dependencies and integration points
It is a platform child of the MAX77620 MFD, supports platform IDs `max77620-gpio` and `max20024-gpio`, uses regmap, gpiolib nested threaded IRQs, and pinconf drive/debounce.

## Risks and edge cases
Only edge triggers are supported; level requests fail. Parent IRQ is requested after gpiochip registration, so error cleanup relies on devm. Debounce values are bucketed to hardware-supported 0/8/16/32 ms choices, not exact requested values.

## Test signals
Test get/set/direction, open-drain/push-pull, debounce bucket boundaries, IRQ mask initialization, rising/falling/both edge types, nested parent IRQ handling, and regmap error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max77620.c -->
