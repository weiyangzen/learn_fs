# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-at91-slave.c

## Purpose
Optional experimental AT91 slave-mode support, compiled when `CONFIG_I2C_AT91_SLAVE_EXPERIMENTAL` is enabled. It presents the AT91 TWI controller as an I2C slave endpoint and translates hardware slave events into Linux `i2c_slave_event()` callbacks.

## APIs, Control Flow, and State
`at91_twi_probe_slave()` requests the IRQ and installs `at91_twi_algorithm_slave`. `at91_reg_slave()` rejects duplicate or 10-bit clients, runtime-resumes the controller to keep the TWI clock alive, stores the `struct i2c_client`, programs `SMR`, reinitializes the bus, and enables `SVACC`. `atmel_twi_interrupt_slave()` handles address match, read/write direction, byte transmit/receive readiness, and end-of-slave-access, emitting `READ_REQUESTED`, `READ_PROCESSED`, `WRITE_REQUESTED`, `WRITE_RECEIVED`, and `STOP`. `at91_unreg_slave()` clears `slave`/`smr`, reinitializes hardware, and releases the runtime PM reference.

## Dependencies and Integration
Shares register access and device state from `i2c-at91-core.c`/`.h`. Integrates with the I2C slave framework and runtime PM; the core file decides whether to call this probe path through `i2c_detect_slave_mode()`.

## Risks and Test Signals
Risks include missing PM puts, stale `SMR` after unregister, incorrect interrupt mask transitions between `SVACC`, `TXRDY`, `RXRDY`, and `EOSACC`, and backend callbacks reentering unexpectedly. Test slave EEPROM-like backends, master reads/writes, repeated STARTs, STOP handling, unregister while idle, runtime suspend prevention while registered, and 10-bit rejection.
