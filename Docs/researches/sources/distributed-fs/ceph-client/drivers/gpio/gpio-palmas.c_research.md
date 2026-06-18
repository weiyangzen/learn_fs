<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-palmas.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-palmas.c

## Purpose
GPIO child driver for TI Palmas-family PMICs, supporting 8-line Palmas/TPS65913/TPS65914 parts and 16-line TPS80036 parts with sleeping GPIO access and PMIC IRQ mapping.

## Important APIs, types, and functions
`struct palmas_gpio` stores the chip and parent `struct palmas`; `struct palmas_device_data` provides `ngpio`. GPIO callbacks are get, set, direction input/output, and `to_irq()`.

## Control flow
Register bank is selected by `offset / 8`, with bit offset modulo 8. `get()` reads direction and then DATA_OUT or DATA_IN. `set()` uses dedicated set/clear registers. `direction_output()` sets the initial output before marking the line as output; input clears the direction bit. Probe fills chip data and honors legacy GPIO base.

## State and persistence behavior
No shadow state exists. Direction/output/input state is in PMIC registers, with no child PM restore.

## Dependencies and integration points
Uses Palmas MFD read/write/update and IRQ translation APIs, platform child devices, OF match data, and gpiolib. The chip can sleep.

## Risks and edge cases
For 16-line devices, `palmas_gpio_output()` reduces offset before calling `palmas_gpio_set()`, risking wrong bank selection for GPIOs 8-15. IRQ mapping assumes contiguous parent PMIC IRQs.

## Test signals
Exercise both banks on TPS80036, set/clear register selection, direction/get behavior, `to_irq()` mappings, legacy base, and parent PMIC error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-palmas.c -->
