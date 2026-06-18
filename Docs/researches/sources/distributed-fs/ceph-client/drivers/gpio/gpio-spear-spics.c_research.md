# sources/distributed-fs/ceph-client/drivers/gpio/gpio-spear-spics.c

## Purpose
This driver presents SPEAr SoC PL022 SPI chip-select control bits as a four-line GPIO controller. It lets SPI chip selects be controlled through system registers outside the SPI controller's own MMIO space.

## Important APIs, Types, and Functions
`struct spear_spics` holds the system-register base, DT-provided register/bit fields, use count, cached last selected chip-select offset, and gpio chip. `spics_set_value()` selects a chip-select index and writes its value bit. `spics_request()` enables software control on the first user; `spics_free()` disables software control after the last user.

## Control Flow
Probe maps the system register resource, reads required DT properties for the peripheral config register and bit fields, fills a four-line output-only gpio chip, and registers it. Consumers request a line, which enables software control and defaults the chip-select value high. Direction output and set both call `spics_set_value()`.

## State and Persistence
Hardware state lives in the peripheral configuration register. Software state is limited to `use_count` and `last_off`, used to avoid rewriting selection fields when the same chip select is toggled repeatedly. There is no locking and no PM handling.

## Dependencies and Integration Points
The driver depends on platform DT properties with `st-spics,*` names, MMIO system registers, gpiolib, and early `subsys_initcall()` registration so chip-select GPIOs are available to SPI controllers.

## Risks
`use_count` and register updates are not locked, so concurrent users can race. Only output semantics are implemented; there is no get or direction_input. Shared hardware appears to select one chip-select at a time, so simultaneous use of multiple lines depends on SPI core serialization. Missing DT properties fail probe.

## Test Signals
Test DT property validation, first request enabling software control, last free disabling it, selection field updates when switching offsets, value bit high/low toggling, repeated set on same offset, and concurrent SPI chip-select consumers if applicable.
