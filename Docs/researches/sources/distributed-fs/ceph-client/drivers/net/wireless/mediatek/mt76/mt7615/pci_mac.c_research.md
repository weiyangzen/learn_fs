# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/pci_mac.c

Purpose: PCI/MMIO TX preparation, DMA reset, and firmware-coordinated MAC reset recovery for mt7615.

Important APIs and functions: `mt7615_write_fw_txp()` converts mt76 scatter-gather buffers into firmware TXP descriptors for MT7615 firmware TX processing. `mt7615_tx_prepare_skb()` allocates a token, sets rate-probe state, writes TXWI, writes either firmware or hardware TXP, and hands skb ownership to the queue. `mt7615_dma_reset()` disables DMA, cleans TX/MCU/RX queues, flushes TX status, and restarts DMA. `mt7615_mac_reset_work()` handles SER reset by stopping queues, setting reset bits, disabling workers/NAPI, notifying firmware, resetting DMA/tokens, reinitializing PDMA, resuming NAPI/queues, updating beacons, and rescheduling MAC work.

Control flow: TX begins in mt76 driver ops and enters `mt7615_tx_prepare_skb()`. Rate-probe frames update WTBL rates under lock before descriptor writing. For reset, interrupt code stores `dev->reset_state` and queues `reset_work`; reset work waits for firmware state transitions (`STOP_PDMA`, `RESET_DONE`, `RECOVERY_DONE`, `NORMAL_STATE`) and mirrors each phase with HIF events.

State and persistence: Manages token IDR/cache entries, queue contents, per-station rate-probe fields, reset bits in `mphy.state`, `reset_state`, ROC timers/work, NAPI/worker enablement, and beacon offload state. No persistent storage.

Dependencies: mt76 DMA/queue/token APIs, Connac TXP helpers, `mt7615_mac_write_txwi()`, MCU beacon offload, MT7622 HIF interrupt trigger, register definitions, and mac80211 queue control.

Risks: TX token leaks or incorrect `tx_info->nbuf` rewrites can break completions and DMA unmap. Reset sequencing is highly race-sensitive around NAPI, workers, ROC timers, MCU waits, and token IDR reinitialization. Firmware state waits only warn on timeout, so partial recovery may continue. Beacon updates must cover both main and ext phys.

Test signals: TX traffic with software and hardware TXP modes, rate probing, token exhaustion recovery, forced SER/reset events, post-reset beaconing, NAPI reenablement, and DMA queue cleanup without use-after-free.
