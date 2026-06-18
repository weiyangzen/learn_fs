# sources/distributed-fs/ceph-client/drivers/fsi/i2cr-scom.c

## Purpose
`i2cr-scom.c` exposes an IBM I2C Responder SCOM device as the same FSI character-device class used by normal SCOM, but it routes 64-bit register reads and writes through the I2CR FSI master helper instead of directly programming the FSI2PIB SCOM engine.

## Important APIs, Types, and Functions
`struct i2cr_scom` holds the child device, cdev, and `struct fsi_master_i2cr *`. File operations are `i2cr_scom_read()`, `i2cr_scom_write()`, and `i2cr_scom_llseek()`, with `simple_open` setting private data through the cdev helper. Probe uses `is_fsi_master_i2cr()`, `to_fsi_master_i2cr()`, `fsi_get_new_minor()`, and `cdev_device_add()`. The transport calls are `fsi_master_i2cr_read()` and `fsi_master_i2cr_write()`.

## Control Flow
Probe rejects devices whose slave master is not an I2CR master. It allocates private state with devres, stores the I2CR master pointer, initializes a child FSI cdev, allocates an FSI SCOM minor, and publishes `scomN`. Reads and writes require exactly eight bytes, cast the current file offset to a 32-bit address, and delegate to the I2CR master read/write operation before copying data to or from userspace. Remove deletes the cdev and frees the minor.

## State and Persistence
State is limited to the character device, minor number, and cached I2CR master pointer. The file has no explicit lock or `dead` flag; cdev removal and FSI device lifetime rules provide the safety boundary.

## Dependencies and Integration Points
The driver depends on `fsi-master-i2cr.h`, private `fsi-slave.h`, the FSI cdev type and minor allocator, and OF compatible `ibm,i2cr-scom`. It binds engine type `0x5` with any version.

## Risks and Test Signals
The offset is truncated to `u32`, so callers cannot address beyond the I2CR helper's 32-bit register space through this device. Unlike `fsi-scom.c`, there are no raw status ioctls, masking, reset handling, or mutex serialization. `copy_to_user()` and `copy_from_user()` return byte counts, but this code returns that value directly rather than normalizing to `-EFAULT`, which is worth checking against kernel style. Tests should cover non-I2CR probe rejection, basic read/write, invalid lengths, minor cleanup on `cdev_device_add()` failure, and disconnect while userspace holds a file descriptor.
