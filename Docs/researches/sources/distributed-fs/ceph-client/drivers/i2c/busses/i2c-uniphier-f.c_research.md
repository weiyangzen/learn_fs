# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-uniphier-f.c

## Purpose

`i2c-uniphier-f.c` is the FIFO-based Socionext UniPhier I2C controller driver. It provides interrupt-driven master transfers, hardware FIFO management, programmable bus timings, STOP/repeated START handling, and generic SCL bus recovery.

## Important APIs, Types, and Functions

`struct uniphier_fi2c_priv` stores the adapter, MMIO base, clock, completion, IRQ mask, current buffer/length, flags, error, busy counter, clock-cycle timing, and IRQ spinlock. Transfer helpers include `uniphier_fi2c_fill_txfifo()`, `uniphier_fi2c_drain_rxfifo()`, `uniphier_fi2c_tx_init()`, `uniphier_fi2c_rx_init()`, `uniphier_fi2c_stop()`, `uniphier_fi2c_xfer_one()`, and `uniphier_fi2c_xfer()`. `uniphier_fi2c_interrupt()` drives the FIFO state machine.

## Control Flow

Probe maps registers, gets IRQ and clock, reads `clock-frequency`, computes `clk_cycle`, initializes adapter and recovery info, initializes hardware timing registers, requests the IRQ, and adds the adapter. Each transfer first checks device-busy status, then processes messages sequentially. `xfer_one()` resets FIFOs, arms fault interrupts, initializes TX or RX, starts the controller unless this is a repeated START, waits for completion, disables IRQs, polls deferred STOP completion when required, and returns any stored error.

## State and Persistence Behavior

Runtime transfer state lives in `priv->len`, `buf`, `enabled_irqs`, `flags`, and `error`, protected against IRQ races by `lock`. Hardware setup persists in timing, noise/filter, reset, and bus-reset registers until suspend or reset. Suspend disables the clock; resume re-enables it and reruns hardware init.

## Dependencies and Integration Points

The driver integrates through platform/OF matching on `socionext,uniphier-fi2c`, Linux clock and MMIO APIs, `i2c_algorithm`, and `i2c_bus_recovery_info`. It supports standard and fast mode only by rejecting invalid `clock-frequency` values above fast mode.

## Risks

The receive path has special handling for lengths at or above 256 bytes because the byte counter cannot cover them; manual NACK and byte-wise tail logic are high-risk. A documented hardware bug requires deferred STOP polling after read-address NACK. IRQ status bits pause the controller until cleared, so missed or incorrectly masked IRQs can stall transfers. Clock-cycle computation uses integer division without rounding safeguards.

## Test Signals

Test standard and fast mode timing setup, write/read messages of lengths 1, 8, 16, 255, 256, and larger, repeated START sequences, address NAK on reads and writes, arbitration loss as `-EAGAIN`, timeout recovery, suspend/resume, and generic SCL recovery line toggling.
