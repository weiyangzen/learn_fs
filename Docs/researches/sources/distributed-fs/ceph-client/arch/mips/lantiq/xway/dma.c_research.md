# sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/dma.c

Purpose: provides low-level XWAY DMA engine setup and exported channel/port helper APIs for Lantiq drivers.

Important APIs/functions: `ltq_dma_enable_irq`, `ltq_dma_disable_irq`, `ltq_dma_ack_irq`, `ltq_dma_open`, `ltq_dma_close`, `ltq_dma_alloc_tx`, `ltq_dma_alloc_rx`, `ltq_dma_free`, `ltq_dma_init_port`, `ltq_dma_init`, and `dma_init`.

Control flow: platform probe maps DMA registers, enables/reset the DMA clock, disables interrupts, discovers channel count from `LTQ_DMA_ID`, resets each channel, and enables polling. Channel allocation allocates coherent descriptors, programs descriptor base/length, resets channel state, configures TX/RX direction, and enables descriptor interrupts.

State and persistence: global `ltq_dma_membase` and `ltq_dma_lock`; per-channel descriptor base, physical address, channel number, and device pointer live in `struct ltq_dma_channel`. Hardware registers persist channel configuration.

Dependencies and integration: exports symbols for Ethernet/PCI/peripheral drivers; uses Linux DMA coherent API, clk API, OF platform matching `lantiq,dma-xway`, and `xway_dma.h`.

Risks: probe panics on mapping or clock failure. Descriptor allocation uses `GFP_ATOMIC`; failure is not checked before programming hardware. Busy waits and global channel select register require locking.

Test signals: DMA probe log, descriptor IRQ delivery, TX/RX data-path tests, port burst/endian settings, and channel reset behavior.
