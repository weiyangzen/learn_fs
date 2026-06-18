# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-uniphier.c

## Purpose

`i2c-uniphier.c` supports the older non-FIFO Socionext UniPhier I2C controller. It implements byte-at-a-time interrupt-completed transfers, explicit STOP generation, clock setup, and bus recovery through SCL/SDA monitor pins.

## Important APIs, Types, and Functions

`struct uniphier_i2c_priv` holds completion, adapter, MMIO base, clock, busy counter, and clock cycle. `uniphier_i2c_xfer_byte()` writes one command byte and waits for the edge-triggered IRQ. `uniphier_i2c_send_byte()` checks arbitration and NAK status. `uniphier_i2c_tx()`, `uniphier_i2c_rx()`, `uniphier_i2c_stop()`, `uniphier_i2c_xfer_one()`, and `uniphier_i2c_xfer()` compose message transfers.

## Control Flow

The IRQ handler only completes the waiter, intentionally avoiding register reads because the hardware interrupt is edge-triggered. Transfers check bus-not-busy, then execute each message and send STOP when it is the last message or `I2C_M_STOP` is set. Timeout or STOP failure triggers `i2c_recover_bus()`. Probe maps resources, enables the clock, computes timing, initializes adapter/recovery metadata, initializes hardware, requests IRQ, and registers the adapter.

## State and Persistence Behavior

The driver carries minimal per-transfer state; most state is in hardware registers and the stack frame. `busy_cnt` remembers repeated busy-bus observations and triggers recovery after more than three occurrences. Suspend disables the clock; resume re-enables and reinitializes timing/control registers.

## Dependencies and Integration Points

It binds to `socionext,uniphier-i2c`, uses platform resources, clock APIs, MMIO, `i2c_algorithm`, and generic SCL recovery callbacks. `clock-frequency` is optional and defaults to standard mode; values above fast mode are rejected.

## Risks

Byte-at-a-time transfers are sensitive to IRQ loss and timeout behavior. The interrupt handler's no-touch design is correct for edge triggering but shifts all status validation to the waiter. Recovery depends on GPIO-like SCL/SDA monitor behavior through controller registers. `clk_cycle = clk_rate / bus_speed` can under-represent periods at non-divisible rates.

## Test Signals

Exercise single-byte and multi-byte reads/writes, combined messages with repeated START and `I2C_M_STOP`, NAK and arbitration-lost propagation, timeout recovery, stuck-bus retry count behavior, standard/fast timing, and suspend/resume reinitialization.
