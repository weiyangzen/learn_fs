<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/ms5611_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/ms5611_spi.c

## Purpose
`ms5611_spi.c` is the SPI wrapper for MS5611/MS5607 sensors. It configures safe SPI parameters, implements reset/PROM/ADC callbacks, and delegates IIO registration and compensation to the common core.

## Important APIs, types, and functions
`ms5611_spi_reset()` sends the reset command. `ms5611_spi_read_prom_word()` uses `spi_w8r16be()`. `ms5611_spi_read_adc()` writes the read-ADC command and reads three bytes. `ms5611_spi_read_adc_temp_and_pressure()` issues temperature and pressure conversion commands via `spi_write_then_read()` and waits for OSR-specific conversion times. Probe sets SPI mode 0, caps speed at 20 MHz, calls `spi_setup()`, fills callbacks, and invokes `ms5611_probe()`.

## Control flow
The SPI core probes the device, the wrapper enforces bus settings, and the common core performs reset/PROM validation/registration. Runtime conversions call wrapper helpers in the sequence temperature conversion/read, pressure conversion/read.

## State and persistence behavior
Wrapper state is limited to `st->client = spi` and callback assignments. Common state owns coefficients and OSR selections.

## Dependencies and integration points
It depends on Linux SPI, OF/SPI IDs for `meas,ms5611` and `meas,ms5607`, unaligned big-endian ADC assembly, and namespace `IIO_MS5611`.

## Risks
The code relies on `&osr->cmd` being suitably aligned for `spi_write_then_read()`, as documented in the shared header. Board-provided `max_speed_hz` is only capped, not raised. Type selection comes from `spi_get_device_id()`, so OF-only binding must still map to a SPI ID.

## Test signals
Verify SPI mode/speed setup, PROM endian reads, ADC reads, all OSR conversion delays, MS5611/MS5607 ID matching, and bus error propagation into common direct and buffered reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/ms5611_spi.c -->
