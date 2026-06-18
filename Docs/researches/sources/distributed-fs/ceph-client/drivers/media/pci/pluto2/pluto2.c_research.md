# sources/distributed-fs/ceph-client/drivers/media/pci/pluto2/pluto2.c

Purpose: Implements the Satelco/SCM Pluto2 PCI DVB-T receiver driver. It handles PCI/MMIO setup, bit-banged I2C, TDA10046 frontend attachment, a directly programmed TUA6034 tuner, PID filtering, one small DMA buffer, interrupts, DVB demux/net registration, and cleanup.

Important APIs, types, and functions: `struct pluto` stores PCI, DVB, I2C, IRQ, and DMA state. Register helpers `pluto_readreg()`, `pluto_writereg()`, and `pluto_rw()` wrap MMIO. I2C bit callbacks are `pluto_setsda()`, `pluto_setscl()`, `pluto_getsda()`, and `pluto_getscl()`. Streaming paths are `pluto_start_feed()`, `pluto_stop_feed()`, `pluto_irq()`, and `pluto_dma_end()`. Hardware lifecycle helpers include `pluto_hw_init()`, `pluto_hw_exit()`, `pluto_reset_frontend()`, and `pluto_reset_ts()`. `frontend_init()` attaches/registers the TDA10046 frontend and tuner callback.

Control flow: Probe allocates state, enables PCI, enables card interrupts in config space, sets 32-bit DMA, requests regions, maps BAR0, requests IRQ, initializes hardware/DMA/interrupts, registers the bit-banged I2C adapter, registers a DVB adapter, reads revision/serial/MAC, initializes demux frontends, attaches frontend, and starts DVB net. IRQ handling checks `REG_TSCR`, rejects non-device interrupts, handles dead/ejected reads of `0xffffffff`, calls `pluto_dma_end()` on DMA completion, counts overflow, resets TS logic on overflow, and acknowledges interrupts. Feed start/stop toggles PID filter registers and full-TS mode.

State and persistence: Driver state includes user counts, full-TS counts, overflow/dead flags, bit-bang bug workaround state, mapped DMA address, and a fixed embedded `dma_buf`. PID filter register state is derived from active feeds. MAC/revision/serial are read from hardware but not persisted by the driver.

Dependencies and integration points: Integrates with PCI, DMA mapping, shared IRQs, I2C bit algorithm, DVB demux/dmxdev/frontend/net APIs, TDA10046 firmware callback, and direct tuner programming through frontend tuner ops.

Risks: `pluto_hw_init()` ignores the return value of `pluto_dma_map()`, so DMA mapping failure may not stop initialization. The DMA buffer is embedded in a `kzalloc` structure and mapped with `dma_map_single`, making cache synchronization correctness essential. Hardware workarounds infer packet counts by scanning for `0x47` and reset TS logic on invalid counters, which can drop data. `pluto_stop_feed()` decrements counters without guarding against imbalance. Serial printing uses `printk(KERN_CONT)`.

Test signals: Validate probe and all rollback labels, DMA mapping failure handling, IRQ none/handled/dead paths, overflow reset path, invalid packet counter recovery, PID filter programming for indexed and full-TS feeds, bit-banged I2C SDA workaround behavior, tuner frequency/bandwidth programming, frontend firmware request, MAC/revision reads, and remove while feeds are active.
