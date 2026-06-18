<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_core.c

Purpose: shared ST LSM6DSx family core. It contains the per-chip settings table, WHO_AM_I validation, sensor allocation, raw/config/event sysfs, power/reset/timer/shub initialization, IRQ handling, buffer setup selection, mount-matrix handling, registration, and suspend/resume.

Important APIs/functions: exported `st_lsm6dsx_set_page()`, `st_lsm6dsx_check_odr()`, `st_lsm6dsx_sensor_set_enable()`, `st_lsm6dsx_set_watermark()`, `st_lsm6dsx_probe()`, and `st_lsm6dsx_pm_ops`. Internal functions include WHOAMI lookup, full-scale/ODR setters, oneshot reads, event read/write/config, shub/timer/device init, IIO allocation, event reporting, threaded IRQ, software-trigger handler, IRQ setup, software-buffer setup, regulator init, suspend, and resume.

Control flow: transport probe passes bus regmap, IRQ, and hardware ID. Core allocates `st_lsm6dsx_hw`, initializes locks/regulators/buffer, verifies ID and WAI against settings, allocates accel and gyro IIO devices, resets and initializes hardware, probes external shub sensors when enabled, configures IRQ and hardware FIFO if an IRQ exists, otherwise configures software-triggered buffers, reads ACPI `ROTM` or generic mount matrix, registers every present IIO device, and enables wakeup if requested. Raw reads temporarily enable the sensor, wait settling time, read data, and disable it. ODR/gain writes update cached state or registers. IRQ thread reports enabled motion/tap events then drains FIFO until empty or error.

State and persistence: device-wide masks track enabled, FIFO-enabled, suspended, and event-enabled sensors. Per-sensor cached `odr`, `hwfifo_odr_mHz`, `gain`, and `watermark` control later hardware programming. Suspend disables enabled sensors unless used as wake event sources and stores `suspend_mask`; resume re-enables them and resumes FIFO. Regulator enablement and reset/boot operations persist for the lifetime of the device.

Dependencies and integration: depends on extensive settings tables, regmap, regulators, IIO, IIO ACPI/generic mount matrix helpers, ST platform data, IRQ trigger type handling, FIFO helpers, sensor-hub helpers, and bus modules importing `IIO_LSM6DSX`.

Risks: settings-table drift is the main correctness risk because all chip variants share the same code. `st_lsm6dsx_read_raw()` in the viewed source contains a duplicated `return -EBUSY;` after the direct-claim check. Event enable logic keeps accelerometer powered while events are active and can interact with FIFO users. IRQ setup rejects unsupported trigger types. Reset flushes FIFO first to avoid IRQ-line/I3C mode races.

Test signals: probe for each supported HW ID/WAI, regulator failure handling, raw reads, ODR/gain sysfs, event threshold/tap configuration and reporting, IRQ polarity/open-drain setup, hardware FIFO and software-trigger modes, sensor-hub discovery, mount matrix from ACPI and firmware properties, wakeup-source suspend/resume, and FIFO resume after PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_core.c -->
