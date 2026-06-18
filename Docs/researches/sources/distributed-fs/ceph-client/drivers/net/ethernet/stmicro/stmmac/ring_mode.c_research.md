# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/ring_mode.c

Purpose: Implements ring-mode descriptor helpers for jumbo-frame TX and DES3 buffer management.

Important APIs and flow: Exported `ring_mode_ops` provides jumbo detection, jumbo TX mapping, 16 KiB RX buffer selection, DES3 initialization/refill, and DES3 cleanup. `jumbo_frm()` maps the linear skb head into one or two DMA descriptors, sets DES2/DES3 addresses for split buffers, prepares descriptors through the selected descriptor ops, and advances `cur_tx`.

Control flow and state: State is in `stmmac_tx_queue` and `stmmac_rx_queue` ring indices, descriptor memory, and `tx_skbuff_dma` metadata. Jumbo descriptors mark `is_jumbo` so cleanup knows when DES3 was used as an extra buffer pointer. RX DES3 is filled only for 16 KiB buffers.

Dependencies and integration: Depends on `stmmac.h`, DMA mapping APIs, buffer size constants, and descriptor callbacks. `hwif.c` selects ring mode for most non-chain configurations.

Risks and test signals: DMA mapping errors after partially mapping a jumbo frame can leave earlier mappings needing cleanup by callers. Test MTUs around 4 KiB, 8 KiB, and above 8 KiB, nonlinear skbs, extended versus normal descriptors, TX timestamp interaction with DES3 cleanup, and RX 16 KiB buffer refill.
