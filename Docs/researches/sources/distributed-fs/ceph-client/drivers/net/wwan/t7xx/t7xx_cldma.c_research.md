# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_cldma.c

Purpose: provides low-level CLDMA register operations for the t7xx control DMA engines, including queue start/stop, interrupt mask/unmask, reset, address programming, and address-mode restoration.

Important APIs/functions: `t7xx_cldma_hw_init()` configures UL/DL address mode, disables invalid address checks, sets busy masks, and clears interrupt mask. `t7xx_cldma_hw_restore()` reapplies UL settings after resume. `t7xx_cldma_hw_set_start_addr()` programs 64-bit GPD ring start addresses. `t7xx_cldma_hw_start_queue()`, `t7xx_cldma_hw_resume_queue()`, and `t7xx_cldma_hw_stop_all_qs()` control queue execution. `t7xx_cldma_hw_irq_en/dis_txrx()` and `_eq()` manipulate L2 masks. `t7xx_cldma_hw_tx_done()`/`rx_done()` clear interrupt status. `t7xx_cldma_hw_reset()` toggles infrastructure reset bits.

Control flow and state: state lives in `struct t7xx_cldma_hw`, especially AP AO/PDN register bases, hardware mode, and physical interrupt ID. Functions directly read/write MMIO and assume callers serialize higher-level queue state.

Dependencies and integration points: used by `t7xx_hif_cldma.c`; depends on register constants in `t7xx_cldma.h`, Linux MMIO helpers, 64-bit lo/hi IO helpers, and delay primitives.

Risks and test signals: incorrect base selection, interrupt mask polarity, reset timing, and address-mode mismatch can break all control channels. Test start/stop, resume, queue active polling, interrupt clear/mask behavior, and 64-bit DMA addressing on supported hardware.
