<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pisosr.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-pisosr.c

## Purpose
Input-only GPIO driver for SPI-compatible parallel-in serial-out shift registers. It optionally pulses a load GPIO, reads the register chain over SPI, and exposes sampled bits as GPIO inputs.

## Important APIs, types, and functions
`struct pisosr_gpio` stores chip, SPI device, buffer, buffer size, optional load GPIO, and mutex. `pisosr_gpio_refresh()` performs the load pulse and SPI read. GPIO callbacks report fixed input direction, get one bit, and get_multiple.

## Control flow
Probe copies a template chip, reads optional `ngpios`, allocates the SPI buffer, gets optional `load` GPIO, initializes the mutex, and registers. Each get refreshes the whole buffer; get_multiple refreshes once and copies selected clumps.

## State and persistence behavior
The buffer holds the last SPI sample only. There is no output, direction state, or PM context.

## Dependencies and integration points
Depends on SPI, optional GPIO consumer `load`, DT compatible `pisosr-gpio`, and gpiolib sleeping operations.

## Risks and edge cases
`get()` ignores refresh errors and may return stale data. Bit order is assumed. Fixed microsecond delays are used for nanosecond-class timing. Final partial bytes rely on masks/offsets.

## Test signals
Configurable `ngpios`, buffer sizing, load pulse timing, SPI length, bit order, stale-data-on-error behavior, and input-only direction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pisosr.c -->
