# sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_mtl.c

Purpose: Implements SXGBE MTL operation callbacks used by the main driver to configure queue scheduling, FIFO sizes, TX/RX queue enablement, thresholds, flow control, and RX queue to DMA channel mapping.

Important APIs and flow: `sxgbe_mtl_init()` updates global MTL operation mode fields for ETS algorithm and receive arbitration. `sxgbe_mtl_dma_dm_rxqueue()` enables dynamic RX queue mapping across three mapping registers. FIFO helpers encode queue FIFO size in 256-byte units. Queue helpers enable/disable TX queues. Flow-control helpers set active/deactive thresholds and enable RX flow control. FEP/FUP helpers toggle forwarding of error/undersized packets. `sxgbe_set_tx_mtl_mode()` maps byte thresholds to TTC encodings or store-and-forward; `sxgbe_set_rx_mtl_mode()` maps RTC thresholds or RX store-and-forward. `sxgbe_get_mtl_ops()` exports the static ops table.

State and dependencies: The file has no persistent private state; it mutates MMIO registers through `readl()`/`writel()` using offsets and bit definitions from `sxgbe_reg.h` and mode constants from `sxgbe_mtl.h`. `sxgbe_main.c` calls these through `priv->hw->mtl`.

Risks and test signals: Several setters OR new mode bits without clearing old threshold fields, so repeated threshold changes may leave stale bits unless hardware encodings are compatible. FIFO-size helpers assume multiples of 256 and nonzero queue sizes. Tests should verify register bit results for each TTC/RTC threshold, store-and-forward mode, repeated threshold bumps from TX/RX interrupts, queue enable/disable, dynamic RX mapping, and flow-control threshold programming.
