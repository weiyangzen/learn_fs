# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-hisi.c

Purpose: HiSilicon Kunpeng/Ascend I2C controller driver. It programs bus timing, fills command FIFOs for multi-message transfers, drains receive FIFO in interrupts, and reports standard I2C plus 10-bit and SMBus-emulated functionality.

Important APIs/types/functions: `struct hisi_i2c_controller` holds adapter, MMIO, clock, IRQ, transfer indices, target address, error bits, timing data, and spike length. Main functions are `hisi_i2c_configure_bus()`, `hisi_i2c_set_scl()`, `hisi_i2c_start_xfer()`, `hisi_i2c_xfer_msg()`, `hisi_i2c_read_rx_fifo()`, `hisi_i2c_irq()`, `hisi_i2c_xfer()`, and `hisi_i2c_probe()`.

Control flow: probe maps registers, disables interrupts, requests IRQ, obtains a clock or `clk_rate` property, computes timing from firmware, registers the adapter, and logs hardware version. A transfer resets software indices, sets address width/address, clears FIFOs and interrupts, enables all interrupts, then waits for completion. TX-empty interrupts enqueue command words with repeated-start and stop bits; RX-full or completion interrupts drain receive data. Transfer completion disables and clears interrupts.

State and persistence: active state includes message indices, buffer indices, `completion`, `msgs`, `msg_num`, and `xfer_err`. Bus timing, clock rate, spike length, and FIFO thresholds persist in registers after probe. There is no runtime PM or remove hook because devm-managed resources dominate lifetime.

Dependencies and integration: depends on platform MMIO, optional clock framework, OF/ACPI IDs, `i2c_parse_fw_timings()`, bitfield helpers, completions, and Linux I2C algorithm callbacks.

Risks: timeout recovery disables interrupts, synchronizes the IRQ, calls generic recovery, and returns `-EIO`; it does not fully reinitialize timing/FIFO registers. Timing arithmetic subtracts fixed controller offsets and can underflow if bad firmware timing or clock values are supplied. Interrupt masking helpers write mask values directly, so hardware mask polarity must remain understood. Errors are collapsed mostly to `-EIO`.

Test signals: probe with clock and `clk_rate` fallback, standard/fast/high-speed timing, 7-bit and 10-bit addressing, combined read/write messages with repeated starts, FIFO threshold behavior, timeout recovery, FIFO error logging, and hardware version log.
