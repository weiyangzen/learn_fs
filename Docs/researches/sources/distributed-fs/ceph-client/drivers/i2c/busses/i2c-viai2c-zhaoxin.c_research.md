# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-viai2c-zhaoxin.c

## Purpose

`i2c-viai2c-zhaoxin.c` is the ACPI-matched Zhaoxin I2C controller driver. It extends the VIAI2C common byte-mode core with Zhaoxin-specific FIFO mode, speed setup, high-speed support, ACPI companion handling, and suspend resume restore.

## Important APIs, Types, and Functions

`struct viai2c_zhaoxin` stores hardware revision, timing/control values, and FIFO transfer length. `viai2c_fifo_xfer()` and `viai2c_fifo_irq_xfer()` drive 32-byte FIFO chunks. `zxi2c_xfer()` chooses FIFO mode for eligible single-message transfers and byte mode otherwise. `zxi2c_get_bus_speed()` reads ACPI speed, validates firmware timing against golden values, and sets TCR/MCR/TR. `zxi2c_isr()` dispatches byte or FIFO IRQ progression.

## Control Flow

Probe initializes common state for Zhaoxin, requests a shared IRQ, allocates private data, selects and programs bus speed, reads revision, configures adapter quirks and ACPI companion, and registers with `devm_i2c_add_adapter()`. Transfers wait for bus ready, clear RX/TX end bits, then either enable FIFO IRQ/mode and wait for completion or enable byte IRQ/mode and call common `viai2c_xfer()`. IRQs are disabled after each transfer.

## State and Persistence Behavior

Persistent hardware speed state is kept in `i2c->tcr`, `priv->tr`, and `priv->mcr` and restored on resume. Per-transfer mode, message pointer, `xfered_len`, and FIFO chunk length are mutable until completion. Hardware revision changes STOP preparation behavior.

## Dependencies and Integration Points

The driver binds ACPI ID `IIC1D17`, uses `i2c_acpi_find_bus_speed()`, shared VIAI2C exports, ACPI companion propagation, platform MMIO/IRQ, and I2C adapter quirks `I2C_AQ_NO_ZERO_LEN` and `I2C_AQ_COMB_WRITE_THEN_READ`.

## Risks

FIFO mode only applies to single messages with length at least two and revision/size constraints, so behavior differs by message shape. Firmware timing validation silently replaces out-of-range FSTP with golden values. Timeout in byte mode writes END bits after failure; missing equivalent recovery in FIFO timeout may leave hardware state sensitive. Shared IRQ handling must return `IRQ_NONE` on empty status, which this driver does.

## Test Signals

Test ACPI probe, speed modes 100 kHz/400 kHz/1 MHz/3.4 MHz, firmware FSTP warning path, FIFO reads/writes above and below 32 bytes, fallback byte-mode combined transfers, timeout and NAK paths, shared IRQ empty status, adapter quirks, and resume restoring speed registers.
