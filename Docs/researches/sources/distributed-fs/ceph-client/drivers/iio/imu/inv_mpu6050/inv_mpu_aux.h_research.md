# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_aux.h

Purpose: declares the MPU auxiliary I2C-master helper API.

Important APIs: `inv_mpu_aux_init()` configures the internal I2C master; `inv_mpu_aux_read()` reads up to 15 bytes from an auxiliary I2C device; `inv_mpu_aux_write()` writes one byte. All take `struct inv_mpu6050_state`, binding calls to the parent MPU register map.

Control flow and state: no runtime behavior; it defines the contract used by the magnetometer implementation.

Dependencies and integration: includes `inv_mpu_iio.h` for state and register definitions. Consumers are in the same shared MPU module.

Risks and tests: prototype changes ripple into magnetometer code. Test signals are compile/link coverage and magnetometer init/read success on MPU9150/9250/9255.
