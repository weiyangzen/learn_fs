# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-axxia.c

## Purpose
I2C master and slave driver for the LSI Axxia API2C controller. It supports 7/10-bit addressing, SMBus block reads, combined write-read sequence mode, generic SCL recovery, and controller-backed slave operation.

## APIs, Control Flow, and State
`struct axxia_i2c_dev` tracks MMIO, current TX/RX messages, FIFO counters, completion, clock, bus rate, slave client, and IRQ. `axxia_i2c_init()` resets the block, enables master mode, computes SCL high/low/setup/hold/filter timing from the input clock and `clock-frequency`, configures timeout counters, and masks interrupts. Master transfers use either `axxia_i2c_xfer_seq()` for exactly one short write followed by read to the same address, or `axxia_i2c_xfer_msg()` for individual auto/manual commands. ISR logic services RX/TX FIFOs, maps arbitration/NACK/invalid/timeout status to errno, and completes the wait. Slave registration enables slave mode/address decode and slave interrupts; slave ISR paths convert FIFO/start/stop/read events into `i2c_slave_event()` callbacks.

## Dependencies and Integration
Integrates with OF compatible `lsi,api2c`, clk, platform IRQ/MMIO, I2C adapter quirks with 255-byte limits, and `i2c_generic_scl_recovery` via controller SCL/SDA monitor/control bits.

## Risks and Test Signals
Risks include sequence-mode NAK timing, busy command recovery, SMBus block length validation, manual-mode timeout handling, slave/master interrupt sharing, and reset side effects during recovery. Test single and combined transfers, lengths near 255 and FIFO size 8, 10-bit targets, invalid SMBus block lengths, arbitration loss, clock stretching timeouts, bus recovery, slave write/read/stop flows, and remove ordering around clock disable and adapter deletion.
