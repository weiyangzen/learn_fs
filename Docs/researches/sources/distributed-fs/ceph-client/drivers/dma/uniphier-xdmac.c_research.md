# sources/distributed-fs/ceph-client/drivers/dma/uniphier-xdmac.c

## Purpose
`uniphier-xdmac.c` implements the UniPhier external DMA controller. Unlike the MIO DMAC driver, it supports both memory copy and slave SG transfers. It uses `virt-dma` for queueing and callbacks and programs one software node at a time into per-channel XDMAC registers.

## Important APIs, Types, and Functions
Core types are `struct uniphier_xdmac_device`, `struct uniphier_xdmac_chan`, `struct uniphier_xdmac_desc`, and `struct uniphier_xdmac_desc_node`. Nodes hold source, destination, burst size, and burst count. Key functions include `uniphier_xdmac_next_desc`, `uniphier_xdmac_chan_start`, `uniphier_xdmac_chan_stop`, `uniphier_xdmac_start`, `uniphier_xdmac_chan_irq`, `uniphier_xdmac_prep_dma_memcpy`, `uniphier_xdmac_prep_slave_sg`, `uniphier_xdmac_slave_config`, `uniphier_xdmac_terminate_all`, `uniphier_xdmac_issue_pending`, and `of_dma_uniphier_xlate`.

## Control Flow
Probe reads `dma-channels`, caps it at 16, maps the register bank, initializes all channels, registers one shared IRQ, registers dmaengine, and registers an OF DMA provider. OF translation takes two arguments: channel id and request factor; it stores them in the selected channel before returning a slave channel.

Memcpy preparation rejects transfers above the hardware maximum and creates one or more nodes split by `XDMAC_MAX_WORD_SIZE` and `XDMAC_MAX_WORDS`. Slave SG preparation uses the stored `dma_slave_config` to choose device address, bus width, and max burst. It rejects maxburst values above the dmaengine maximum, unaligned SG lengths relative to burst-size units, and node burst counts above hardware capacity. `issue_pending` moves descriptors into the issued list and starts the channel if idle.

`uniphier_xdmac_chan_start` writes transfer factor, 64-bit source/destination addresses, source/destination address modes, transfer size, transfer count, interrupt enable bits, and start request. The shared IRQ handler walks all channels and calls `uniphier_xdmac_chan_irq`. On error, the channel is stopped and an error is logged. On end interrupt, the current node advances; completion calls `vchan_cookie_complete` and starts the next descriptor, while intermediate nodes are immediately programmed.

## State and Persistence
Runtime state is held in the virt-dma lists, active descriptor pointer `xc->xd`, per-channel slave config, channel id, and request factor. There is no persistent state. Removal synchronously terminates every channel before unregistering the OF DMA controller and dmaengine device.

## Dependencies and Integration Points
The file depends on OF DMA, platform devices, `virt-dma`, bitfield helpers, MMIO accessors, and dmaengine slave/memcpy APIs. It advertises `DMA_MEMCPY` and `DMA_SLAVE`, supports `DMA_DEV_TO_MEM`, `DMA_MEM_TO_DEV`, and `DMA_MEM_TO_MEM`, and reports burst-level residue granularity while using plain `dma_cookie_status` for status.

## Risks and Review Signals
Memcpy node count is computed as `1 + len / XDMAC_MAX_WORD_SIZE`, which can over-allocate for exact multiples and can produce a zero-length final node depending on the loop inputs. Slave SG rejects residue-sized tails, so clients must configure maxburst carefully. IRQ handling scans every channel and always returns handled, which is typical for shared hardware summary IRQs but can mask unrelated interrupts if the line is shared externally. Tests should cover OF request-factor programming, memcpy boundary sizes, slave unaligned SG rejection, channel stop timeout, error interrupt behavior, and remove with active descriptors.
