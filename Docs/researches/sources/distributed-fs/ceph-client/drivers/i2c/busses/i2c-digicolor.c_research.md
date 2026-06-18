# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-digicolor.c

## Purpose
Conexant Digicolor SoC I2C adapter. It implements an interrupt-driven state machine around byte-wide controller command/data registers and exposes I2C plus SMBus emulation and `I2C_FUNC_NOSTART`.

## Important APIs, Types, And Functions
`struct dc_i2c` stores adapter, device, MMIO registers, clock, frequency, active message pointer, buffer position, last-message flag, spinlock, completion, state, and error. Core functions are `dc_i2c_irq()`, `dc_i2c_xfer_msg()`, `dc_i2c_xfer()`, `dc_i2c_start_msg()`, `dc_i2c_init_hw()`, and small command/data helpers.

## Control Flow
Probe reads optional `clock-frequency`, gets clock, maps MMIO, requests IRQ, initializes adapter fields, initializes hardware clock timing, enables the clock, and registers the adapter. Each message is started under lock with interrupts enabled. The IRQ clears the flag, checks command completion status for ACK/abort failures, advances through START, ADDR, WRITE, READ, and STOP states, filling or draining one byte at a time, and completes when the message or stop is done.

## State And Persistence
The transfer state machine is stored in `dc_i2c` fields and protected by a spinlock. The clock divider is programmed at probe. No persistent storage is used.

## Dependencies And Integration Points
Depends on OF compatible `cnxt,cx92755-i2c`, platform MMIO/IRQ resources, clocks, completions, spinlocks, and Linux I2C core.

## Risks
Timeout is fixed at 100 ms per message. Command status maps bad ACK and abort to `-EIO` rather than distinct NACK errors. Clock timing must fit an 8-bit register. IRQ-driven state must correctly handle `I2C_M_NOSTART` and repeated-start cases.

## Test Signals
Test adapter probe, clock-frequency limits, write/read/repeated-start/no-start transfers, ACK-bad and abort status handling, timeout reset to idle, IRQ disable after transfer, and remove clock cleanup.
