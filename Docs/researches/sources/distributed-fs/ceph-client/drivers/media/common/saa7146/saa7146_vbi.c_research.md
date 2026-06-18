# sources/distributed-fs/ceph-client/drivers/media/common/saa7146/saa7146_vbi.c

Purpose: VBI capture support for the SAA7146 VV module, using DMA3/BRS and RPS1 programs.

Important APIs/functions: exports `saa7146_vbi_uops` with `init` and `irq_done`. Internal `vbi_begin()` claims `RESOURCE_DMA3_BRS`, tunes arbitration, initializes BRS, and may run `vbi_workaround()`. `saa7146_set_vbi_capture()` programs DMA3 and an RPS1 capture sequence. VB2 qops allocate/build/free page tables and handle streaming.

Control flow: start streaming resets sequence if needed and calls `vbi_begin()`. Queued buffers activate DMA3/RPS1 and set a timeout. IRQ completion marks current buffer done and advances; stop disables RPS1 IRQs/DMA3, deletes timers, returns queued buffers, and frees the resource.

State/persistence: VBI state lives in `vv->vbi_dmaq`, `vv->vbi_read_timeout`, `vv->vbi_wq`, resource bits, and BRS/DMA registers. No durable persistence.

Dependencies/integration: uses SAA7146 core registers, `saa7146_write_out_dma()`, shared buffer helpers, VB2 DMA-SG page tables, extension flags such as `SAA7146_USE_PORT_B_FOR_VBI`, and VV IRQ dispatch.

Risks/test signals: `vbi_workaround()` sleeps waiting for IRQ and is signal-sensitive; some constants are PAL-specific; stop has a `return_buffers()` call before resource free in source order that makes the following free unreachable. Tests should cover port A/B paths, signal interruption, timeout, stop cleanup/resource release, and 16-line buffer sizing.
