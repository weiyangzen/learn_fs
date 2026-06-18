
# sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-mux-gpio.h

## Purpose
This header defines platform data for an I2C mux controlled by GPIO lines.

## Important APIs And Types
`I2C_MUX_GPIO_NO_IDLE` means no specific idle mux state. `struct i2c_mux_gpio_platform_data` contains parent adapter number, base adapter number for child buses, array of GPIO bitmask values, number of mux positions, idle bitmask, and settle time after selection.

## Control Flow, State, And Persistence
The mux driver selects a child bus by writing the corresponding GPIO bitmask, waits `settle_time`, performs transfers through the parent adapter, and optionally writes the idle state when done. State is the current GPIO mux selection.

## Dependencies And Integration Points
It integrates platform data with the I2C mux core, parent I2C adapters, and GPIO-controlled board multiplexers.

## Risks And Test Signals
Risks include wrong parent adapter number, duplicate child bus numbers, mismatched values array length, missing settle delay, and unsafe idle state. Test signals include child adapter creation, transfers on every mux position, idle-state verification, GPIO waveform checks, and concurrent child bus access serialization.
