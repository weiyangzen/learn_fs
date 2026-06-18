## sources/distributed-fs/ceph-client/drivers/dma/dw/dw.c

Purpose: Register-variant implementation for the standard DesignWare AHB DMA controller.

Important APIs/types/functions: exports `dw_dma_probe()` and `dw_dma_remove()`. Installs callbacks `dw_dma_initialize_chan()`, `dw_dma_suspend_chan()`, `dw_dma_resume_chan()`, `dw_dma_prepare_ctllo()`, `dw_dma_bytes2block()`, `dw_dma_block2bytes()`, `dw_dma_set_device_name()`, `dw_dma_disable()`, and `dw_dma_enable()`.

Control flow: probe allocates `struct dw_dma`, assigns channel and device operation callbacks, stores it in `chip->dw`, and delegates to `do_dma_probe()`. Channel initialization programs CFG_LO/HI with priority, FIFO mode, handshakes, polarity, peripheral IDs, and protection control. Transfer prep callbacks in the core call `prepare_ctllo()` and block conversion helpers to build descriptor CTL fields.

State and persistence: no independent persistent state; it provides behavior used by the shared `struct dw_dma` state. Register writes persist only while hardware is powered and configured.

Dependencies and integration: integrates with `internal.h`, `regs.h`, shared core, DMAengine direction helpers, and exported probe/remove symbols for platform/PCI glue.

Risks and test signals: wrong burst encoding or master selection can cause broken transfers on slave paths. Test standard DW controllers with memory copy and peripheral SG, different master IDs, handshake polarity, suspend/resume, and block-size boundary transfers.
