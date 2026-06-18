# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5592r-base.c

## Purpose
`ad5592r-base.c` is the shared IIO and GPIO implementation for the AD5592R SPI and AD5593R I2C configurable eight-channel mixed ADC/DAC/GPIO devices. Bus-specific files provide register and data-path callbacks through `struct ad5592r_rw_ops`, while this base file handles firmware channel modes, IIO channel construction, raw ADC/DAC access, scale/range control, reset, reference handling, and optional GPIO chip registration.

## Important APIs, Types, And Functions
- `ad5592r_probe()` and `ad5592r_remove()` are exported in namespace `IIO_AD5592R` for the SPI and I2C wrappers.
- `ad5592r_set_channel_modes()` converts firmware `adi,mode` and `adi,off-state` values into DAC enable, ADC enable, pulldown, tristate, GPIO input/output, and GPIO value registers.
- `ad5592r_alloc_channels()` reads child fwnodes, builds the dynamic IIO channel list, and always appends the internal temperature channel.
- `ad5592r_read_raw()` reads ADC channels, returns cached DAC writes for output channels, reports scale, and calculates temperature offset.
- `ad5592r_write_raw()` writes DAC values and switches ADC or DAC gain bits in `AD5592R_REG_CTRL`.
- GPIO callbacks `ad5592r_gpio_get()`, `ad5592r_gpio_set()`, `ad5592r_gpio_direction_input()`, `ad5592r_gpio_direction_output()`, and `ad5592r_gpio_request()` expose channels configured as GPIOs.
- `ad5592r_reset()` uses an optional reset GPIO or writes the reset magic value to the reset register.

## Control Flow
Probe allocates the IIO device, initializes the bus callback table and mutex, enables optional `vref`, computes available scales, resets the chip, configures internal/external reference powerdown, allocates channels from firmware, applies channel modes, registers the IIO device, then registers a GPIO chip if any channels are marked GPIO. Runtime raw writes go through the bus `write_dac` callback and update `cached_dac`; raw ADC reads call `read_adc`, verify that the returned channel tag matches, and strip the 12-bit sample. Scale writes read-modify-write the control register cache to set ADC or DAC range bits.

## State And Persistence
`struct ad5592r_state` persists firmware-derived `channel_modes` and `channel_offstate`, GPIO maps and values, `cached_gp_ctrl`, cached DAC values, available scale pairs, regulator pointer, and the bus transfer buffers. The driver treats DAC readback as a software cache for output channels. GPIO state is protected by `gpio_lock`; SPI/I2C register/data sequences are protected by `lock`. Removal unregisters IIO, resets all channel modes to unused/off-state, removes GPIO, and disables the regulator.

## Dependencies And Integration Points
The base depends on IIO, gpiolib, firmware property APIs, regulators, mutex cleanup helpers, and `dt-bindings/iio/adi,ad5592r.h` channel mode constants. It integrates with transport wrappers through `ad5592r_rw_ops` and with gpiolib only for channels explicitly configured as GPIO.

## Risks And Edge Cases
- GPIO chip registration happens after IIO device registration; if GPIO registration fails, IIO is unregistered and channels are reset, but consumers briefly observing the IIO device during probe failure are theoretically possible.
- `ad5592r_write_raw_get_fmt()` returns `IIO_VAL_INT_PLUS_MICRO` for non-scale masks even though raw writes are integer; this ABI detail should be checked against IIO expectations.
- Firmware parsing silently ignores invalid/missing child `reg`; invalid `adi,mode` values are treated as unused when applying channel modes.
- `ad5592r_reset()` does not propagate failure from reset-register write in the non-GPIO path because the scoped guard body return is not captured; the delay still occurs and probe continues. This is worth targeted review.
- Temperature scale and offset formulas depend on fixed-point arithmetic and reference voltage; regression tests should pin expected values.

## Test Signals
Test fwnode configurations for DAC, ADC, DAC_AND_ADC, GPIO, and unused off-states; register write ordering in channel setup; ADC readback channel-tag validation; DAC cache readback; gain scale switching; optional regulator and internal reference behavior; GPIO direction/value paths; reset GPIO and register-reset paths; and cleanup on mid-probe errors.
