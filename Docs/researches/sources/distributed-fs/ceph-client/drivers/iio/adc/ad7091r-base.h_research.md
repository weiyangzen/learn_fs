# sources/distributed-fs/ceph-client/drivers/iio/adc/ad7091r-base.h

## Purpose
`ad7091r-base.h` defines the shared register map, IIO channel macro, modes, state structure, chip descriptors, initialization contract, and exported symbols used by the AD7091R base driver and its I2C/SPI variants.

## Important APIs, types, and definitions
Register definitions cover result, channel, configuration, alert, per-channel low/high limits, and hysteresis. Result helpers extract conversion result bits and chip-family-specific channel IDs (`AD7091R5_REG_RESULT_CH_ID()` and `AD7091R8_REG_RESULT_CH_ID()`). Configuration bits include internal reference enable, alert enable, autocycle mode, and command mode. `AD7091R_CHANNEL()` builds a voltage channel with raw and shared scale info, optional event specs, indexed channel number, and 16-bit storage.

`enum ad7091r_mode` names sample, command, and autocycle modes. `struct ad7091r_state` is the private runtime state shared by the base and bus front ends: device, regmap, optional conversion/reset GPIOs, optional vref regulator, chip info, mode, mutex, and aligned 16-bit SPI buffers. `struct ad7091r_chip_info` supplies chip name, channel table, reference voltage, result-channel parser, and mode setter. `struct ad7091r_init_info` is the bus-driver handoff contract, containing IRQ/no-IRQ chip info, regmap config, regmap initializer, and optional setup callback.

## Control flow and integration
The header's contract is that bus-specific probe functions gather match data, initialize a bus-specific `ad7091r_init_info`, and call `ad7091r_probe()`. The base probe then calls `init_adc_regmap()` and optional `setup()` before using the chip info and callbacks to finish common IIO registration. Bus drivers also use `ad7091r_events` for IRQ-capable channel arrays and `ad7091r_writeable_reg()` / `ad7091r_volatile_reg()` in their regmap configs.

## State and persistence behavior
The header defines only in-memory state and hardware register constants. `ad7091r_state` stores runtime mode and bus resources. Hardware persistence is through ADC registers written by the base or bus driver; no filesystem state exists.

## Dependencies and integration points
It includes `linux/regmap.h` and forward-declares `struct device` and `struct gpio_desc`; it relies on IIO channel/event types being visible in including C files. It declares exported APIs in the `IIO_AD7091R` namespace and is included by both the base implementation and bus-specific drivers.

## Risks and edge cases
The shared state contains SPI-oriented TX/RX buffers even though the I2C variant does not need them; bus code must avoid assuming all fields are valid. The init contract has separate IRQ and no-IRQ chip info pointers; missing IRQ info on an IRQ-capable match will break common probe. `AD7091R_CHANNEL()` hardcodes voltage-channel info masks and 16-bit storage, so variants with different ABI needs would require a new macro or custom channel tables.

## Test signals
Header-level validation is mostly compile-time: ensure both bus drivers build against the exported prototypes and struct fields, regmap configs can call the access helpers, channel arrays compile with and without event specs, namespace imports are present in modules, and result-channel-ID macros match the data-sheet bit widths for AD7091R5 and AD7091R2/4/8 variants.
