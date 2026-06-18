<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/i2c.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/i2c.h

## Purpose
`i2c.h` defines the low-level I2C and SMBus transaction ABI shared by kernel and userspace. It describes I2C message segments, adapter functionality masks, SMBus data containers, and SMBus transaction type IDs.

## Important APIs, types, and functions
`struct i2c_msg` contains slave address, flags, length, and buffer pointer. Flags include `I2C_M_RD`, `I2C_M_TEN`, `I2C_M_DMA_SAFE`, `I2C_M_RECV_LEN`, `I2C_M_NO_RD_ACK`, `I2C_M_IGNORE_NAK`, `I2C_M_REV_DIR_ADDR`, `I2C_M_NOSTART`, and `I2C_M_STOP`. Function masks include raw I2C, 10-bit addressing, protocol mangling, PEC, no-start, slave mode, SMBus operation bits, and aggregate masks such as `I2C_FUNC_SMBUS_EMUL`. `union i2c_smbus_data`, `I2C_SMBUS_READ/WRITE`, and `I2C_SMBUS_*` size IDs define SMBus payloads.

## Control flow
An I2C transaction is a sequence of `i2c_msg` segments, each beginning with START and ending with STOP or repeated START unless special protocol-mangling flags apply. SMBus helpers encode common command/data flows with explicit transaction size IDs.

## State and persistence behavior
The header carries no state. Message buffers are transient transfer data; function masks reflect current adapter capabilities.

## Dependencies and integration points
It depends on `<linux/types.h>` and is used by i2c-dev, kernel adapter drivers, SMBus emulation, and userspace tools.

## Risks and test signals
Risks include using protocol-mangling flags without capability bits, `I2C_M_RECV_LEN` buffer underallocation, ten-bit address misuse, DMA-safe flag misuse in userspace, and SMBus block length off-by-one errors. Test signals include adapter functionality tests, combined transfer traces, SMBus block/proc-call validation, NACK behavior, and fuzzing message counts/lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/i2c.h -->
