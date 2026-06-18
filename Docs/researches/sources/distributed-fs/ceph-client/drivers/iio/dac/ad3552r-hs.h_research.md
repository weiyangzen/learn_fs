
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad3552r-hs.h

## Purpose
`ad3552r-hs.h` defines the platform-data contract between the AD3552R high-speed driver and its backend/bus provider.

## Important APIs, types, and functions
- Forward declares `struct iio_backend`.
- `enum ad3552r_io_mode` enumerates SPI, dual-SPI, and quad-SPI bus modes.
- `struct ad3552r_hs_platform_data` provides callbacks for bus register read/write, bus IO mode switching, and the sample data clock rate.

## Control flow
No runtime control flow exists here. The high-speed platform driver calls these callbacks during setup, raw access, streaming enable, and streaming disable.

## State and persistence behavior
The header defines no state itself; backend providers populate platform data with function pointers and clock metadata.

## Dependencies and integration points
It is included by `ad3552r-hs.c` and by whatever platform/backend glue instantiates the high-speed platform device. It also relies on the IIO backend abstraction.

## Risks and edge cases
The callback contract assumes bus providers can safely switch IO modes while the DAC target is sequenced by the driver. Incorrect callback ordering or wrong `bus_sample_data_clock_hz` directly affects streaming mode and reported sample frequency.

## Test signals
Compile backend providers against this header and validate callback invocation order during high-speed postenable/predisable and raw register access.
