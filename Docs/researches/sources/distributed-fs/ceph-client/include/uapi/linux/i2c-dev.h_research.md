<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/i2c-dev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/i2c-dev.h

## Purpose
`i2c-dev.h` defines the ioctl ABI for `/dev/i2c-X` adapter character devices, exposing adapter configuration, direct I2C combined transfers, and SMBus transactions to userspace.

## Important APIs, types, and functions
Ioctls include `I2C_RETRIES`, `I2C_TIMEOUT`, `I2C_SLAVE`, `I2C_SLAVE_FORCE`, `I2C_TENBIT`, `I2C_FUNCS`, `I2C_RDWR`, `I2C_PEC`, and `I2C_SMBUS`. `struct i2c_smbus_ioctl_data` carries read/write direction, command, transaction size, and `union i2c_smbus_data` pointer. `struct i2c_rdwr_ioctl_data` carries an array of `struct i2c_msg` and count. `I2C_RDWR_IOCTL_MAX_MSGS` caps combined messages, with misspelled `I2C_RDRW_IOCTL_MAX_MSGS` retained.

## Control flow
User space opens an adapter, selects a slave address and options, queries supported functions, then performs `I2C_RDWR` for combined messages or `I2C_SMBUS` for SMBus operations. `I2C_SLAVE_FORCE` bypasses normal driver ownership checks and should be rare.

## State and persistence behavior
Retries, timeout, selected slave address, ten-bit mode, and PEC mode are per open adapter fd. Transfer buffers are transient and copied/validated by i2c-dev.

## Dependencies and integration points
It depends on `<linux/types.h>` and `<linux/compiler.h>` and uses structures from `linux/i2c.h`. It integrates with I2C adapter drivers, SMBus emulation, sensor/EEPROM tooling, and board-management utilities.

## Risks and test signals
Risks include using unsupported functions, overlong message arrays, unsafe `I2C_SLAVE_FORCE`, ten-bit limitations, pointer compat issues, and devices with side-effectful register writes. Test signals include `i2cdetect`/`i2ctransfer` behavior, function-mask checks, invalid message rejection, SMBus block transfers, PEC toggling, and 32/64-bit compat ioctl tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/i2c-dev.h -->
