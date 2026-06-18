# sources/distributed-fs/ceph-client/drivers/iio/temperature/maxim_thermocouple.c

Purpose: shared SPI IIO driver for Maxim MAX6675 and MAX31855 thermocouple sensors. It supports direct raw reads, scale, thermocouple type reporting, and triggered-buffer capture.

Important APIs/types/functions: chip metadata in `struct maxim_thermocouple_chip` selects channel table, scan mask, read size, and status bit. `struct maxim_thermocouple_data` stores SPI, chip info, thermocouple type char, and aligned read/buffer union. `maxim_thermocouple_read()` decodes raw values; `maxim_thermocouple_trigger_handler()` pushes raw scan data.

Control flow: probe maps SPI ID to MAX6675 or MAX31855 metadata, allocates IIO, sets channels and scan masks, installs triggered buffer, warns on generic MAX31855 ID, and registers. Direct raw reads claim direct mode, perform a 2- or 4-byte SPI read, reject status-bit fault, shift and sign-extend the requested channel, and return integer raw. Buffer handler reads a whole frame and pushes it with timestamp.

State and persistence: there is no mutable hardware configuration. The shared buffer is used by both direct and triggered paths, with direct reads protected by IIO direct-mode claim but no explicit mutex.

Dependencies/integration: depends on SPI, IIO direct mode, IIO triggered buffers, OF/SPI IDs for generic and type-specific MAX31855 variants.

Risks and test signals: triggered buffer does not check status fault bits before pushing samples; consumers must interpret scan data. Test MAX6675 and MAX31855 frame decoding, type chars for specific IDs, deprecated generic warning, scan masks, direct-read/buffer exclusion, SPI short/error paths, and fault-bit behavior.
