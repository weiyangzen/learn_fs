# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_aux.c

Purpose: implements internal MPU I2C-master transfers used to access auxiliary devices, especially AKM magnetometers embedded in MPU9x50 parts.

Important APIs and functions: `inv_mpu_aux_init()` configures the MPU I2C master clock and slave delays. `inv_mpu_aux_read()` programs SLV0 for a read, runs one master transfer, and reads external sensor data registers. `inv_mpu_aux_write()` programs SLV0 plus output data for a one-byte write. Internal `inv_mpu_i2c_master_xfer()` temporarily sets a 50 Hz divider, enables I2C master, waits one-and-a-half periods, disables it, restores the previous divider, disables SLV0, and checks NACK status.

Control flow and state: uses current `st->chip_config.user_ctrl` and `divider` as the baseline to restore after transfers. Initialization has a legacy MPU9150 level-shifter tweak.

Dependencies and integration: regmap, delay helpers, `inv_mpu_iio.h` register constants, and `inv_mpu_magn.c`. It is part of the shared MPU module, not a Linux I2C adapter itself.

Risks and tests: transfer error paths must restore sample rate, user control, and SLV0 state or the main FIFO rate/magnetometer state can be corrupted. Size is limited to 15 bytes. Test signals include magnetometer probe/read, NACK handling, divider restoration, level-shifter property behavior, and no regression to FIFO sampling rate after aux reads.
