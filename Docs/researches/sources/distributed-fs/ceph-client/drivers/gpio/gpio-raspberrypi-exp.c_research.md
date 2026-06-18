<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-raspberrypi-exp.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-raspberrypi-exp.c

## Purpose
Raspberry Pi firmware-managed expander GPIO driver. It exposes eight sleeping GPIOs and uses firmware mailbox property calls for config and state.

## Important APIs, types, and functions
`struct rpi_exp_gpio` stores chip and firmware handle. Mailbox payloads are set-config, get-config, and get/set-state structs. GPIO callbacks implement direction input/output, get_direction, get, and set. `rpi_exp_gpio_get_polarity()` preserves polarity across direction changes.

## Control flow
Probe gets the parent firmware node and firmware handle, fills an 8-line chip, and registers. Operations translate local offset to firmware GPIO `128 + offset`, call the relevant firmware property, and require returned `gpio == 0`.

## State and persistence behavior
No local cache exists. Firmware owns direction, polarity, termination, and state.

## Dependencies and integration points
Depends on Raspberry Pi firmware, OF compatible `raspberrypi,firmware-gpio`, and gpiolib sleeping operations.

## Risks and edge cases
Firmware communication can fail on every operation. Direction changes disable termination and only preserve polarity. There is no IRQ support. Nonzero firmware status maps to `-EIO`.

## Test signals
Probe deferral, local-to-firmware numbering, direction changes preserving polarity, get/set state calls, and firmware error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-raspberrypi-exp.c -->
