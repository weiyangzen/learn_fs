<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-loongson1.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-loongson1.c

## Purpose
`gpio-loongson1.c` supports the Loongson 1 SoC GPIO controller using gpio-generic for MMIO data, output, and direction registers.

## Important APIs, types, and functions
`struct ls1x_gpio_chip` embeds `gpio_generic_chip` and the MMIO base. `ls1x_gpio_request()` sets the enable/config bit for a line; `ls1x_gpio_free()` clears it. Probe maps registers, initializes gpio-generic, installs request/free hooks, and registers the chip.

## Control flow
Probe maps resource 0, builds a generic chip config with `GPIO_DATA`, `GPIO_OUTPUT`, and `GPIO_DIR`, initializes it, clears `ngpio` so gpiolib reads the firmware `ngpios` property, and registers the chip. Request/free toggle the `GPIO_CFG` bit under the generic chip lock.

## State and persistence behavior
Hardware stores config, direction, data, and output state. The driver keeps no software shadow. Requested lines are enabled in hardware and disabled on free.

## Dependencies and integration points
The driver binds to `loongson,ls1x-gpio`, depends on gpio-generic and platform MMIO resources, and integrates with DT-provided line count.

## Risks and edge cases
Clearing `ngpio` relies on firmware providing `ngpios`; missing properties can produce registration surprises. Request/free side effects mean consumers that hold descriptors control hardware line enable state.

## Test signals
Test DT `ngpios` parsing, request/free config-bit toggling, direction/input/output operations, and registration failure paths with missing MMIO resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-loongson1.c -->
