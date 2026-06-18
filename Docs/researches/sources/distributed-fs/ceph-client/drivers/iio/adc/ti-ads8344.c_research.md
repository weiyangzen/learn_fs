# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads8344.c

Purpose: compact SPI IIO direct-mode driver for the TI ADS8344 16-bit ADC, exposing eight single-ended channels and eight differential channel combinations.

Important APIs/types/functions: `struct ads8344` holds SPI, vref regulator, mutex, and small DMA-safe tx/rx buffers. Channel macros create single-ended and differential `iio_chan_spec` entries with raw and shared scale attributes. `ads8344_adc_conversion()` sends the control byte, waits for conversion, reads three bytes, and assembles the 16-bit result. `ads8344_read_raw()` handles raw and scale. `ads8344_probe()` enables vref and registers IIO.

Control flow: probe allocates IIO, initializes the mutex, assigns static channels, gets and enables `vref`, installs a devm regulator-disable action, and registers the IIO device. Raw reads lock the ADC, build a command from START, single-ended/differential mode, channel address, and internal clock bits, write one byte, delay 9 microseconds, read three bytes, then combine the serial response.

State and persistence: no cached hardware configuration beyond regulator enable. Shared transfer buffers are protected by the mutex. No persistent storage, IRQs, or buffered path.

Dependencies and integration: SPI, vref regulator, IIO direct mode, OF compatible `ti,ads8344`.

Risks: no SPI setup constraints are enforced in this driver; conversion timing is a fixed delay; differential channel mapping relies on address encoding in the static table. Test signals include single-ended and differential raw reads, scale from regulator voltage, mutex serialization under concurrent sysfs reads, and probe cleanup when vref enable fails.
