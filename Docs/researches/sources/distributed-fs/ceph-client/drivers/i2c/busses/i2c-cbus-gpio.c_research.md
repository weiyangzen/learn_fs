# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cbus-gpio.c

## Purpose
GPIO bit-banged CBUS adapter for Nokia Internet Tablets, exposed through the I2C SMBus word-data API. CBUS is not normal I2C; this driver maps its 3-bit device, 1-bit direction, 5-bit register, and 16-bit data protocol onto SMBus word read/write operations.

## APIs, Control Flow, and State
`struct cbus_host` holds a spinlock, device, and three GPIO descriptors (`clk`, `dat`, `sel`). Bit helpers drive/read GPIOs without delays. `cbus_transfer()` disables local interrupts via `spin_lock_irqsave()`, asserts SEL, switches DAT direction, shifts address/direction/register and optional write data, reads 16-bit words for reads, then deasserts SEL and clocks an end pulse. `cbus_i2c_smbus_xfer()` accepts only `I2C_SMBUS_WORD_DATA` and passes the SMBus address/command/data to CBUS. Probe requires exactly three unnamed GPIOs, sets consumer names, fills a numbered HWMON-class adapter, and registers it.

## Dependencies and Integration
Depends on gpiolib descriptor APIs, platform/OF binding `i2c-cbus-gpio`, Linux I2C SMBus xfer hooks, and atomic SMBus support by reusing the same transfer function.

## Risks and Test Signals
Risks include timing sensitivity from no explicit udelays, interrupt masking duration, GPIO direction failures leaving SEL asserted, and protocol mismatch if non-Nokia CBUS variants differ. Test word reads/writes to known CBUS devices, atomic SMBus users, GPIO polarity/order from DT, error paths during DAT direction change, concurrent transfers, and remove after adapter registration.
