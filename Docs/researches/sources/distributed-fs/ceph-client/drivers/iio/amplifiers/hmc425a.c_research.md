# sources/distributed-fs/ceph-client/drivers/iio/amplifiers/hmc425a.c

## Purpose
`hmc425a.c` supports GPIO-controlled gain attenuators/amplifiers in the HMC425A family plus HMC540S, ADRF5740, and LTC6373. It exposes one voltage output channel with writable hardware gain; LTC6373 also exposes a `powerdown` extended attribute.

## Important APIs, Types, And Functions
`struct hmc425a_chip_info` describes per-part channel metadata, GPIO count, gain range, default code, powerdown support, and conversion callbacks. `struct hmc425a_state` stores the chip info, GPIO descriptors, cached gain code, powerdown flag, and mutex. Conversion helpers map dB values to GPIO codes and back for each supported part. `hmc425a_write()` pushes the bit pattern to all GPIOs. `hmc425a_read_raw()` and `hmc425a_write_raw()` implement hardwaregain as `IIO_VAL_INT_PLUS_MICRO_DB`. `ltc6373_read_powerdown()` and `ltc6373_write_powerdown()` control shutdown.

## Control Flow
Probe obtains chip data from OF match data, validates the number of `ctrl` GPIOs, enables `vcc-supply`, initializes the mutex, sets IIO direct mode, then writes either a powerdown value for LTC6373 or the default gain for the other parts. Runtime writes validate dB range and powerdown state, convert to a code, cache it, and write GPIOs.

## State And Persistence
Gain and powerdown state are cached in memory and mirrored to GPIO lines. There is no nonvolatile persistence. The mutex serializes gain and powerdown changes. On probe, hardware is initialized to a fixed default rather than reading any previous pin state.

## Dependencies And Integration Points
The driver integrates with platform/OF matching, GPIO descriptor arrays, regulators, IIO sysfs, and IIO extended channel attributes. Supported compatible strings select static conversion tables.

## Risks
The GPIO bit ordering must match board wiring. Code conversion uses bitwise inversion and integer rounding; boundary and fractional dB behavior is part-specific and easy to regress. `ltc6373_write_powerdown()` sets `powerdown` before writing GPIO and ignores `hmc425a_write()` return, though GPIO helper currently returns void-equivalent success. Reads/writes return `-EPERM` while powered down.

## Test Signals
Validate each compatible's GPIO count, default code, min/max gain boundaries, fractional dB conversion, read-after-write, LTC6373 powerdown gating, and regulator/GPIO probe failures.
