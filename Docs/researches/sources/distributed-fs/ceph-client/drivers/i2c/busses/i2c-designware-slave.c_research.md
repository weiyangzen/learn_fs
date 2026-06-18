# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-slave.c

## Purpose
Optional DesignWare I2C slave-mode implementation. It registers/unregisters an I2C slave client, configures the controller for slave operation, and translates slave interrupts into Linux `i2c_slave_event()` callbacks.

## Important APIs, Types, And Functions
Exports `i2c_dw_reg_slave()`, `i2c_dw_unreg_slave()`, `i2c_dw_isr_slave()`, and `i2c_dw_configure_slave()`. Internal helper `i2c_dw_read_clear_intrbits_slave()` acknowledges slave-relevant interrupts using individual clear registers.

## Control Flow
Register checks adapter slave functionality, rejects an existing slave and ten-bit clients, acquires the hardware lock, runtime-resumes the device, disables the controller, stores `dev->slave`, and switches to slave mode. ISR validates enabled/raw status and slave presence, handles RX_FULL as master-write-to-slave, RD_REQ as master-read-from-slave, writes outbound data, and sends STOP events. Unregister masks interrupts, disables the controller, synchronizes IRQ, clears `dev->slave`, switches to master mode, and runtime-suspends.

## State And Persistence
Slave state is `dev->slave`, `dev->status`, and controller registers including SAR and interrupt mask. No persistent storage exists; slave registration persists only while the client is bound.

## Dependencies And Integration Points
Depends on shared DesignWare common code, regmap, runtime PM, IRQ synchronization, Linux I2C slave callbacks, and Kconfig `CONFIG_I2C_SLAVE`.

## Risks
Polling-mode controllers do not advertise slave support. Slave and master mode switching shares the same `status` flags, so mode transitions must happen with hardware disabled. Event ordering for write-request/write-received/read-request/read-processed depends on FIFO and RD_REQ behavior. Unregister must avoid use-after-free via `synchronize_irq()`.

## Test Signals
Test slave registration rejection cases, master write to slave, master read from slave, repeated reads, STOP delivery, unregister during idle and after IRQ activity, runtime PM balancing, and configurations without `CONFIG_I2C_SLAVE`.
