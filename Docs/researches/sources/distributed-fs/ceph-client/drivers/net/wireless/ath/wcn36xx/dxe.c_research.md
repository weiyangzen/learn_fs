<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/dxe.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/dxe.c

Purpose: Implements WCN36xx DXE DMA engine setup and runtime handling for high/low priority TX and RX channels, including descriptor rings, IRQs, DMA memory pools, TX completion, RX refill, BMPS wake signaling, and flush/deinit.

Important APIs/types/functions: Exports `wcn36xx_dxe_alloc_ctl_blks()`, `wcn36xx_dxe_free_ctl_blks()`, `wcn36xx_dxe_allocate_mem_pools()`, `wcn36xx_dxe_free_mem_pools()`, `wcn36xx_dxe_init()`, `wcn36xx_dxe_deinit()`, `wcn36xx_dxe_tx_frame()`, `wcn36xx_dxe_tx_flush()`, `wcn36xx_dxe_rx_frame()`, and `wcn36xx_dxe_tx_ack_ind()`. Key internals include descriptor initialization/freeing, `wcn36xx_dxe_fill_skb()`, `reap_tx_dxes()`, IRQ handlers, and `wcn36xx_rx_handle_packets()`.

Control flow: Allocation builds circular control-block rings for TX low/high and RX low/high and initializes SMSM TX state. Init resets DXE, selects interrupt routing, allocates coherent descriptor rings, assigns TX BD pools, primes RX skbs, writes channel next/source/destination registers, requests TX/RX IRQs, creates a TX ACK timer, and enables channel interrupts. TX uses paired descriptors: one for the firmware buffer descriptor and one for skb data; it maps skb DMA, marks descriptors valid in order, advances the head, and either writes channel control or signals SMSM when in BMPS. TX IRQs clear per-channel status and reap completed descriptors, transferring requested-status frames to either immediate mac80211 status, an ACK-indication wait slot, or timeout. RX IRQs process invalidated descriptors, replace skb buffers, unmap and deliver old skbs, then re-enable the channel.

State and persistence: Maintains descriptor/control rings, coherent BD pools, DMA mappings, queued skb pointers, channel head/tail pointers, locks, TX ACK pending skb/timer, queue-stopped flag, IRQ registrations, and SMSM state bits. All state is runtime and freed on deinit.

Dependencies and integration points: Depends on MMIO DXE/CCU register bases, Qualcomm SMEM state, mac80211 TX status and queue control, WCN36xx TX/RX parsing (`wcn36xx_rx_skb()`), platform IRQs, DMA API, and power-save state in `wcn36xx_vif`.

Risks and test signals: Risks include descriptor ownership ordering, DMA mapping leaks on TX errors, RX refill allocation failure dropping packets, TX ACK timeout races, queue stop/wake imbalance, IRQ cleanup ordering, and BMPS wake signaling. Test signals are high/low priority TX/RX traffic, requested TX status with ACK indication and timeout, ring-full backpressure, RX allocation-failure resilience, suspend/remove deinit, DMA API debug, and BMPS data transmission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/dxe.c -->
