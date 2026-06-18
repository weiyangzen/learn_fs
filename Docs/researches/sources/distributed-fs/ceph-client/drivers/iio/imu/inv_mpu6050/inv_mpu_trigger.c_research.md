<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_trigger.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_trigger.c

Purpose: trigger, IRQ, and FIFO enablement support for the InvenSense MPU6050/MPU9x50 IIO driver. It decides which sensor engines feed the FIFO, arms data-ready interrupts, captures IRQ timestamps, and forwards raw data-ready and wake-on-motion events to IIO.

Important APIs/functions: `inv_mpu6050_prepare_fifo()` is exported to reset and arm/disarm the hardware FIFO. `inv_mpu6050_probe_trigger()` allocates the IIO trigger and threaded IRQ. Internal helpers include `inv_scan_query_mpu6050()`, `inv_scan_query_mpu9x50()`, `inv_mpu6050_set_enable()`, and the IRQ top/thread handlers.

Control flow: trigger enable queries the active scan mask, resumes runtime PM, switches off unneeded engines except WoM, enables selected engines, computes initial skip samples, resets FIFO, programs `fifo_en`, enables FIFO reads through `user_ctrl`, and sets data-ready interrupt enable. Trigger disable clears all FIFO-enable booleans, disables the data-ready interrupt, clears `fifo_en`, restores `user_ctrl`, and releases runtime PM. The hard IRQ stores `it_timestamp`; the thread acknowledges status where needed, pushes WoM events, and calls `iio_trigger_poll_nested()` for raw data-ready.

State and persistence: persistent state is in `struct inv_mpu6050_state`: `chip_config.*_fifo_enable`, `skip_samples`, `it_timestamp`, runtime PM state, FIFO/user-control register state, and WoM enablement. The code preserves `chip_config.user_ctrl` when disabling FIFO.

Dependencies and integration: depends on the MPU core header for register definitions and engine switching, regmap, runtime PM, IIO triggers/events, and `inv_sensors_timestamp_reset()`. It is called by the main MPU probe path after IRQ discovery.

Risks: `inv_mpu_data_rdy_trigger_set_state()` calls `inv_mpu6050_set_enable()` twice with the same state, which looks accidental and can double-run PM/FIFO transitions. MPU6000/6050 bypass interrupt-status reads by assuming data-ready. MPU9x50 magnetometer operation skips the first sample and depends on `magn_disabled` auxiliary-bus state. Error paths rely on autosuspend cleanup after partially enabled engines.

Test signals: IIO buffer enable/disable, runtime PM reference balance, FIFO reset and `fifo_en` programming, IRQ timestamp monotonicity, WoM event delivery, magnetometer first-sample skip, and trigger-only operation with no active scan mask.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_trigger.c -->
