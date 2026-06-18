# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/gpio.c

## Purpose
Implements a gpiolib driver for QE parallel I/O banks and a legacy QE pin multiplexing API. It exposes QE PIO pins as GPIOs while preserving firmware-programmed dedicated-function register state so clients can switch pins between GPIO and peripheral modes.

## Important APIs, types, and functions
`struct qe_gpio_chip` wraps `struct gpio_chip`, MMIO registers, a spinlock, shadow `cpdata`, and saved PIO register state. GPIO operations are `qe_gpio_get`, `qe_gpio_set`, `qe_gpio_set_multiple`, `qe_gpio_dir_in`, and `qe_gpio_dir_out`. Legacy pin APIs are exported as `qe_pin_request`, `qe_pin_free`, `qe_pin_set_dedicated`, and `qe_pin_set_gpio`. Probe registers a 32-pin bank for compatible `"fsl,mpc8323-qe-pario-bank"`.

## Control flow and state behavior
Probe allocates the chip, maps the bank registers, snapshots `cpdata`, direction, assignment, and open-drain registers, then registers the gpiochip. GPIO writes update shadow `cpdata` under lock before writing the big-endian data register. Direction changes call `__par_io_config_pin`. `qe_pin_request` obtains a nonexclusive GPIO descriptor only to find the owning chip and local offset, then releases the descriptor and returns a custom `qe_pin`. `qe_pin_set_dedicated` restores per-pin saved direction, assignment, data, and open-drain bits; `qe_pin_set_gpio` reconfigures the pin as GPIO input.

## Dependencies and integration points
Depends on gpiolib descriptors and chips, platform OF matching, QE PIO register definitions, and `__par_io_config_pin` from `qe_io.c`. The custom pin API is a compatibility bridge for drivers that have not moved to pinctrl.

## Risks and test signals
`qe_gpio_set_multiple` mutates the caller-provided mask with `__test_and_clear_bit`, matching some gpiolib patterns but worth checking if reused. `qe_pin_request` uses `gc->base` to compute offsets despite dynamic GPIO bases; descriptor-native offsets would be safer. Test signals include GPIO get/set/direction operations, restoration of firmware dedicated function after GPIO use, and correct rejection of non-QE GPIO descriptors.
