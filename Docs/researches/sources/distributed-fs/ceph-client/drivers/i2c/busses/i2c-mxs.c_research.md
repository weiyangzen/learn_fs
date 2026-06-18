# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mxs.c

Purpose: Freescale MXS/i.MX23/i.MX28 I2C bus driver. It combines PIO transfers for small messages with DMA engine transfers for larger messages and programs timing registers from a fixed 24 MHz block clock.

Important APIs/types: `struct mxs_i2c_dev` stores device type, MMIO registers, completion, last command error, adapter, timing register values, DMA channel, PIO command/data buffers, scatterlists, and read/write DMA mode. Important functions include `mxs_i2c_xfer()`, `mxs_i2c_xfer_msg()`, `mxs_i2c_pio_setup_xfer()`, `mxs_i2c_dma_setup_xfer()`, `mxs_i2c_isr()`, `mxs_i2c_reset()`, `mxs_i2c_derive_timing()`, and `mxs_i2c_probe()`.

Control flow: probe identifies i.MX23 versus i.MX28, maps registers, requests IRQ, derives timing from `clock-frequency` or 100 kHz default, requests the shared rx-tx DMA channel, resets hardware, and registers a numbered adapter. Each message chooses PIO for reads up to 4 bytes and writes under 7 bytes, otherwise DMA. PIO writes chunk bytes through the data register with optional clock retention; PIO reads issue a select then read command. DMA queues PIO register writes and memory/device SG descriptors, waits on completion from the last descriptor callback, then checks command error.

State and persistence: timing register values persist in software and are restored by `mxs_i2c_reset()`. `cmd_err` is set by ISR or PIO error checks per transfer. DMA scatterlists and command buffers are reused in the device object. Remove unregisters the adapter, releases the DMA channel, and soft-resets the block.

Dependencies and integration: depends on OF compatibles `fsl,imx23-i2c` and `fsl,imx28-i2c`, STMP reset helper, DMA engine and MXS DMA flags, I2C core, completions, IRQs, and DMA-safe I2C message buffers. It registers at `subsys_initcall`, likely to be available early for dependent devices.

Risks: i.MX23 requires reset after every transfer because of documented PIO/DMA residue behavior. DMA setup has several descriptor stages and must unmap the right SG entries on partial failure. PIO read is hard-limited by `BUG_ON(msg->len > 4)` but selection logic should prevent larger PIO reads. Timeout cleanup calls `mxs_i2c_dma_finish()` even after the callback might have raced, so completion ordering matters. Timing derivation clamps out-of-range speeds and may silently run at a different rate with only warnings.

Test signals: cover i.MX23 and i.MX28 compatibles, PIO read/write boundary lengths, DMA read/write paths, NAK and early termination IRQs, DMA timeout reset, timing clamping for high/low requested speeds, no-zero-length quirk, and remove-time DMA release/reset.
