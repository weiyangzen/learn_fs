# sources/distributed-fs/ceph-client/drivers/input/joystick/psxpad-spi.c

Purpose: SPI driver for PlayStation 1/2 joypads, with optional rumble force feedback under `CONFIG_JOYSTICK_PSXPAD_SPI_FF`.

Important APIs/types/functions: `struct psxpad` stores SPI device, input device, phys path, motor enable/levels, send buffer, and response buffer. `psxpad_command()` performs one synchronous SPI transfer. Optional FF helpers configure motors and implement `psxpad_spi_play_effect()`. `psxpad_spi_poll()` sends the poll command, decodes analog (`0xCE`) and digital (`0x82`) responses, and reports axes/buttons. `psxpad_spi_probe()` configures SPI mode/speed, input capabilities, polling, FF, runtime PM, and registration.

Control flow: Probe allocates state/input, sets ABS/key capabilities, initializes optional memless FF, forces SPI mode 3 at 125 kHz, sets polling at about 60 Hz, registers input, and enables runtime PM. Input open gets runtime PM; close puts it. Each poll optionally configures motors, fills command bytes with current motor levels, transfers, decodes response by controller mode, and syncs input.

State and persistence: Motor levels and enable flags persist in `struct psxpad` between polls. Runtime PM state is tied to input open/close. No persistent storage.

Dependencies and integration points: SPI core, input polling, runtime PM, optional input FF memless, and PSX protocol bit reversal.

Risks: Probe sets `spi->controller->min_speed_hz` and `max_speed_hz`, which mutates controller-wide constraints rather than only this device. `spi_set_drvdata()` is not visible before suspend uses `spi_get_drvdata()`, so suspend path should be verified. Motor configuration is called every poll when FF is enabled, adding traffic.

Test signals: Digital and analog controllers; rumble enabled/disabled builds; runtime PM open/close; suspend clearing motors; SPI setup failure; response modes other than `0xCE`/`0x82`.
