# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-xlp9xx.c

## Purpose

`i2c-xlp9xx.c` is the Broadcom/Cavium XLP9XX/5XX I2C master driver. It provides interrupt-driven FIFO transfers, 7-bit and 10-bit addressing, SMBus block receive-length handling, configurable bus frequency, and optional SMBus Alert device setup.

## Important APIs, Types, and Functions

`struct xlp9xx_i2c_dev` stores adapter, completion, SMBus alert data/client, IRQ, transfer flags, MMIO base, buffer pointers, clock rates, and error status. Helpers include `xlp9xx_i2c_update_rx_fifo_thres()`, `xlp9xx_i2c_fill_tx_fifo()`, `xlp9xx_i2c_drain_rx_fifo()`, `xlp9xx_i2c_isr()`, `xlp9xx_i2c_init()`, `xlp9xx_i2c_xfer_msg()`, and `xlp9xx_i2c_xfer()`.

## Control Flow

Probe maps registers, gets main and optional SMBAlert IRQs, derives input and target clock frequencies, initializes hardware, requests IRQ, registers the adapter, optionally creates an SMBus alert client, and stores driver data. Each message checks bus idle, resets FIFO, programs slave address and direction, sets length and RX thresholds, fills TX FIFO when needed, unmasks relevant interrupts, starts the command with optional STOP, waits for completion, maps errors, and updates actual length for `I2C_M_RECV_LEN`.

## State and Persistence Behavior

Per-message state lives in `msg_buf`, `msg_buf_remaining`, `msg_len`, `msg_read`, `len_recv`, `client_pec`, and `msg_err`. Hardware initialization persists prescaler and enable/master bits until reset/remove. Timeout reinitializes the controller. Remove disables interrupts, synchronizes IRQ, deletes adapter, and disables the controller.

## Dependencies and Integration Points

It binds ACPI IDs `BRCM9007` and `CAV9007`, uses platform MMIO/IRQ, optional clock, I2C and SMBus alert helpers, completions, and ACPI companion propagation. Functionality includes I2C, SMBus emulation, SMBus read block data, and 10-bit addresses.

## Risks

SMBus block reads dynamically adjust controller length after reading the first byte; invalid or zero lengths abort by forcing remaining length to zero. Timeout recovery resets the controller but may not emit a STOP first. Frequency calculation assumes the internal 5x SCL relationship and valid input frequency. Optional SMBus alert failure is only debug logged.

## Test Signals

Test ACPI probe, default and clock-provided input frequencies, invalid bus frequency fallback, 7-bit and 10-bit transfers, zero-length quick commands, FIFO refills/drains above 128 bytes, SMBus block reads with PEC and invalid lengths, bus busy recovery, NAK/bus-error/arbitration errors, timeout reset, SMBAlert registration, and remove cleanup.
