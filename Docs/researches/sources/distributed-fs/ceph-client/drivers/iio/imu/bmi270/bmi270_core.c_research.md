# Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi270/bmi270_core.c

Purpose: common IIO core for Bosch BMI260/BMI270 six-axis IMUs. It supports accel, gyro, temperature, step counter, motion/no-motion events, triggered buffered accel/gyro capture, firmware/init-data loading, IRQ routing, and runtime PM.

Important APIs, types, and functions: exports `bmi260_chip_info`, `bmi270_chip_info`, `bmi270_core_probe()`, and `bmi270_core_pm_ops`. `struct bmi270_data` stores device/regmap/chip info, IRQ pin, trigger, mutex, step-enable state, DMA-safe scan buffer, and feature-register scratch. Feature access is through `bmi270_{read,write,update}_feature_reg()`. Raw IIO paths use `bmi270_{get,set}_scale()`, `bmi270_{get,set}_odr()`, `bmi270_get_data()`, and `bmi270_read_steps()`. Event paths use `bmi270_anymotion_event_en()`, `bmi270_nomotion_event_en()`, `bmi270_step_wtrmrk_en()`, and event value/config callbacks.

Control flow: core probe initializes mutex/state, validates chip ID, uploads firmware/init data, configures power and default ODR/BWP, sets IIO channels and available scan masks, probes optional INT1/INT2 trigger, installs triggered buffer, and registers IIO. IRQ thread reads status registers, polls the data-ready trigger for accel/gyro, and pushes IIO events for motion, no-motion, and step watermark. Buffer handler bulk-reads six accel/gyro words from `BMI270_ACCEL_X_REG`.

State and persistence: device state includes firmware-loaded feature engine, power control, ODR/range, interrupt mapping, feature pages, motion thresholds/durations, step counter enable/watermark/reset, and interrupt latch/polarity. Host state `steps_enabled` gates step watermark use and direct read/write paths use `iio_device_claim_direct()` to avoid buffered races.

Dependencies and integration: depends on regmap, request_firmware for `bmi260-init-data.fw`/`bmi270-init-data.fw`, IIO events, triggered buffers, firmware IRQ names `INT1`/`INT2`, `drive-open-drain`, and bus wrappers.

Risks: firmware file absence fails probe. Feature-register page switching and shared scratch require mutex coverage. `bmi270_enable_steps()` sets `steps_enabled = true` even when asked to write zero, so disable semantics are limited. `bmi270_validate_chip_id()` refuses BMI160 but may update chip info when actual ID differs from match data. Motion threshold scaling depends on current accel scale.

Test signals: firmware load success/failure, BMI160 rejection, BMI260/BMI270 chip switching, raw reads with direct-mode locking, scale/ODR available lists, buffered all-channel scan, INT1/INT2 edge/level/open-drain configuration, data-ready trigger polling, motion/no-motion event enable and values, step enable/read/reset/watermark, and runtime PM.
