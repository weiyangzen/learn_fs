# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads8688.c

Purpose: SPI IIO driver for TI ADS8684/ADS8688 ADCs, with direct reads, triggered buffers, per-channel input-range programming through IIO scale/offset, and optional vref regulator.

Important APIs/types/functions: `struct ads8688_state` stores mutex, chip info, SPI, vref in mV, per-channel range, and aligned command/data buffers. `ads8688_read()` issues a manual-channel command followed by NOOP to retrieve the result. `ads8688_prog_write()` programs range registers. `ads8688_read_raw()`, `ads8688_write_raw()`, `ads8688_write_raw_get_fmt()`, and `ads8688_trigger_handler()` implement IIO behavior.

Control flow: probe reads optional `vref`, defaults to 4096 mV, selects 4- or 8-channel chip info, forces SPI mode 1, resets the device, initializes the mutex, configures a triggered buffer, and registers IIO. Direct raw reads lock, perform a two-transfer SPI transaction, and return the lower 16 bits. Scale/offset reads use `range[]`; writes validate supported combinations, write the channel range program register, then update cached range. Triggered scans iterate active channels and push a timestamped buffer.

State and persistence: `range[8]` mirrors range registers but starts at zero, matching reset default. Device range settings persist only until reset/power loss. Transfer buffers are shared under `lock`; no disk persistence.

Dependencies and integration: SPI, regulator helper, IIO triggered buffer, IIO sysfs attributes for available scale/offset, OF/SPI IDs `ads8684` and `ads8688`.

Risks: triggered handler calls `ads8688_read()` without taking `st->lock`, so concurrent range writes/direct reads may contend on shared buffers unless IIO serialization prevents it; invalid offset/scale combinations are rejected based on current cached range. Test signals include range changes for each legal scale/offset pair, default-vref fallback, buffered scan ordering, and reset behavior.
