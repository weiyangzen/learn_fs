# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-emev2.c

## Purpose
Renesas EMEV2 I2C adapter with both master and slave support. It drives an interrupt/completion master transfer path and translates addressed slave events into Linux I2C slave callbacks.

## Important APIs, Types, And Functions
`struct em_i2c_device` stores MMIO base, adapter, completion, registered slave, and IRQ. Core functions include `em_i2c_reset()`, `__em_i2c_xfer()`, `em_i2c_xfer()`, `em_i2c_slave_irq()`, `em_i2c_irq_handler()`, `em_i2c_reg_slave()`, `em_i2c_unreg_slave()`, and probe/remove.

## Control Flow
Probe maps MMIO, enables the `sclk`, initializes adapter fields, resets hardware, requests IRQ, and registers the adapter. Master transfer checks bus busy, then for each message sends START, address, waits for events, handles NACK/arbitration loss, reads or writes bytes, and optionally sends STOP. IRQ first gives slave handling a chance; if not handled as slave, it completes the master wait. Slave IRQ handling filters extension codes and stop events, handles addressed read/write directions, calls `i2c_slave_event()`, and writes or reads the shift register.

## State And Persistence
State is in MMIO registers, `msg_done` completion, and optional `slave` pointer. Adapter timeout and retries are configured at probe. No persistent storage exists.

## Dependencies And Integration Points
Depends on OF compatible `renesas,iic-emev2`, platform MMIO/IRQ, enabled clock `sclk`, Linux I2C master and slave APIs, completions, and IRQ synchronization.

## Risks
Master and slave share IRQ flow; stop detection may be ambiguous and can deliberately fall through to master completion. NACK is returned as `-ENXIO`; arbitration loss returns `-EAGAIN`. Slave unregister relies on clearing SVA and `synchronize_irq()` to avoid stale slave pointer use.

## Test Signals
Test master read/write/repeated messages, bus-busy `-EAGAIN`, NACK handling, arbitration-loss reset, slave write/read/stop events, slave unregister racing with IRQ, timeout reset, and adapter registration/removal.
