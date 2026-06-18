# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sh_mobile.c

Purpose: SuperH Mobile/R-Mobile/R-Car IIC controller driver. It supports interrupt and atomic transfers, optional DMA, variant-specific timing setup, R8A7740 erratum workaround, runtime PM, and noirq suspend adapter marking.

Important APIs/types/functions: `struct sh_mobile_i2c_data` stores device, MMIO, adapter, timing, clock, ICIC flags, lock/wait queue, current message position/status, STOP/DMA state, DMA channels, resource, and bounce buffer. `enum sh_mobile_i2c_op` models byte-level operations. Main routines are `sh_mobile_i2c_init()`, `sh_mobile_i2c_v2_init()`, `i2c_op()`, `sh_mobile_i2c_isr_tx()`, `sh_mobile_i2c_isr_rx()`, `sh_mobile_i2c_isr()`, DMA helpers, `start_ch()`, `sh_mobile_xfer()`, probe/remove, and PM callbacks.

Control flow: probe gets clock, hooks one or more IRQs, maps registers, parses `clock-frequency`, detects extra ICIC bits by resource size, initializes timing under runtime PM, initializes DMA channel placeholders, fills adapter, and registers it. Transfer resumes PM, processes messages, decides whether to emit START, prepares channel and optional DMA buffer, kicks START, then waits for IRQ or polls in atomic mode. ISR records status, starts DMA after address preface when applicable, handles arbitration/TACK non-destructively until STOP, dispatches TX/RX byte sequencer, clears WAIT, and wakes on software done. After each message, the caller polls busy or DTE depending on STOP/repeated-start behavior, disables the channel, and drops PM.

State and persistence: state includes `pos` where `-1` is address phase and RX real position is `pos - 2`; `sr` accumulates status flags; `send_stop` controls STOP versus repeated-start; `stop_after_dma` indicates successful DMA completion for buffer sync. DMA channels persist and are released at remove.

Dependencies/integration: I2C core, OF compatible data, clk/runtime PM, DMA engine, scatterlist/dma mapping, platform IRQ resources, wait queues/spinlocks, and `i2c_get_dma_safe_msg_buf()`.

Risks: byte sequencing is tightly coupled to documented WAIT/DTE order. DMA is skipped in atomic mode and only starts after the address preface. Timeout cleanup must terminate DMA if active. Polling for DTE/busy maps TACK to `-ENXIO` and arbitration loss to `-EAGAIN`; missed status accumulation could misreport. R8A7740 workaround directly toggles pads and timing.

Test signals: 0/1/multi-byte writes, 1/2/>3-byte reads, repeated-start multi-message transfer, explicit `I2C_M_STOP`, atomic path, DMA read/write over threshold, NACK/TACK and arbitration loss, timeout with active DMA, variants with ICIC67 timing bits, R8A7740 workaround, multiple IRQ resources, and suspend/resume adapter state.
