# sources/distributed-fs/ceph-client/drivers/media/rc/ir-spi.c

Purpose: SPI-backed IR LED transmitter driver. It registers a raw transmit-only rc-core device and converts pulse/space duration arrays into a binary SPI waveform that drives an IR LED through a regulator.

Important APIs, types, and functions: `struct ir_spi_data` stores carrier frequency, active-low flag, pulse/space 16-bit patterns, rc device, SPI device, and regulator. `ir_spi_tx()` converts microsecond durations to carrier cycles, allocates a `u16` transmit buffer, fills it with pulse or space words, enables the regulator, sends one SPI transfer at `freq * 16`, disables the regulator, and returns count or error. `ir_spi_set_tx_carrier()` validates carrier against SPI maximum speed. `ir_spi_set_duty_cycle()` computes pulse bitmask and handles active-low LED wiring. `ir_spi_probe()` reads regulator and device properties, allocates `RC_DRIVER_IR_RAW_TX`, wires callbacks, sets default carrier and duty cycle, and registers rc-core.

Control flow: userspace transmit through rc-core calls `tx_ir`, optionally after setting carrier or duty cycle. The SPI signal consists of `IR_SPI_BITS_PER_PULSE` bits per carrier period; duty cycle controls how many bits are high/low in the pulse word. The regulator is powered only around the SPI transfer.

State and persistence behavior: device state persists in devm-managed `ir_spi_data` for the SPI device lifetime. Carrier, duty cycle words, and active-low configuration remain until changed or device removal.

Dependencies and integration points: depends on SPI core, regulator framework, firmware properties (`led-active-low`, `duty-cycle`), rc-core raw TX API, and OF/SPI device IDs for `ir-spi-led`.

Risks and edge cases: `ir_spi_tx()` mutates the supplied duration buffer from microseconds to cycles, which is acceptable only if rc-core treats it as temporary. Large durations can allocate large buffers. Duty cycle calculation uses `GENMASK(bits, 0)` and `bits = duty_cycle * 15 / 100`; extreme duty-cycle values should be validated by callers or tested. Carrier must fit under `spi->max_speed_hz / 16`.

Test signals: transmit NEC/RC5 raw buffers, verify carrier frequency on a logic analyzer, test active-low and normal LED wiring, regulator enable/disable failure paths, large transmit buffers, invalid carrier zero/too-high, and property-provided duty cycles.
