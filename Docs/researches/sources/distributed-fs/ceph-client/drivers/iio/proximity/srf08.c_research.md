<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/srf08.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/srf08.c

Purpose: I2C IIO driver for Devantech SRF02/SRF08/SRF10 ultrasonic rangers. It exposes one distance channel, triggered-buffer capture, and for SRF08/SRF10 adds custom sysfs attributes for maximum range and sensitivity.

Important APIs, types, and functions: `struct srf08_chip_info` provides sensitivity tables/defaults and range default. `struct srf08_data` stores client, sensitivity, range in mm, mutex, sensor type, and chip info. `srf08_read_ranging()` sends the ranging command, waits based on configured range, polls software revision until ready, then reads the first echo. `srf08_write_range_mm()` and `srf08_write_sensitivity()` program custom attributes. `srf08_trigger_handler()` and `srf08_read_raw()` expose buffer/direct reads.

Control flow: probe checks SMBus byte/word functionality, selects chip info by I2C ID driver data, initializes the IIO device, sets up triggered buffer, writes default range/sensitivity when supported, and registers. Direct and buffered reads run the same locked ranging command and centimeter-scale result path. SRF02 omits range/sensitivity attributes by using a smaller `iio_info`.

State and persistence: `range_mm` and `sensitivity` are driver caches because the hardware registers cannot be read back. These values also influence wait time before readiness polling. Hardware keeps range/gain settings after writes.

Dependencies and integration points: depends on I2C SMBus byte data, word reads, IIO direct mode, triggered buffers, and OF/I2C matching for SRF02/SRF08/SRF10.

Risks and test signals: test all three sensor types, default write failures, range parsing in 43 mm increments, sensitivity table validation, readiness polling failure, word-swapped echo decoding, and buffer direct interaction. Risks include no explicit direct-mode claim, buffer handler locking again only around push after `srf08_read_ranging()` already locked/unlocked, and fixed readiness polling assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/srf08.c -->
