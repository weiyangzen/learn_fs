# Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi160/bmi160_core.c

Purpose: common IIO core for Bosch BMI160/BMI120 over regmap. It provides accelerometer and gyroscope raw channels, scale and sample-frequency controls, triggered buffer capture, IRQ trigger setup, regulators, mount matrix, and runtime PM.

Important APIs, types, and functions: exports `bmi160_regmap_config`, `bmi160_core_probe()`, `bmi160_enable_irq()`, `bmi160_probe_trigger()`, and `bmi160_core_pm_ops`. Internal tables map sensor type to data/config/range/PMU registers, scale values, and ODR values. `bmi160_set_mode()`, `bmi160_set_scale()`, `bmi160_get_scale()`, `bmi160_set_odr()`, `bmi160_get_odr()`, and `bmi160_get_data()` back IIO raw access. `bmi160_trigger_handler()` reads active channels into the aligned buffer.

Control flow: core probe allocates IIO state, gets regulators, reads orientation, initializes the chip, registers cleanup, configures channel metadata and buffer setup, optionally discovers INT1/INT2 and configures trigger IRQ, then registers the IIO device. Chip init enables regulators, soft-resets, performs an SPI dummy read when needed, validates chip ID, and powers accel/gyro into normal mode. Cleanup suspends gyro/accel and disables regulators.

State and persistence: device registers persist PMU modes, ranges, ODRs, and interrupt routing. Host state tracks regmap, trigger, supplies, orientation, and scan buffer. Runtime PM suspends/resumes IIO triggering, not the chip PMU directly.

Dependencies and integration: relies on regmap, regulator bulk APIs, firmware IRQ names `INT1`/`INT2`, optional `drive-open-drain`, IIO mount matrix, IIO triggered buffers, and bus wrappers.

Risks: no hardware FIFO despite TODO; buffered reads loop individual active channels from the raw data window. IRQ configuration needs correct firmware trigger type and pin name. Chip ID mismatch is warned but not fatal after `bmi160_check_chip_id()` returns a failure, so compatible-but-unexpected silicon behavior should be reviewed. SPI mode requires dummy read after reset.

Test signals: regulator failure paths, chip ID reads for BMI120/BMI160, SPI dummy read, scale/ODR sysfs round trips, direct raw reads, buffered capture for all channels, INT1/INT2 IRQ polarity/open-drain combinations, trigger enable/disable, mount matrix, and runtime PM trigger suspend/resume.
