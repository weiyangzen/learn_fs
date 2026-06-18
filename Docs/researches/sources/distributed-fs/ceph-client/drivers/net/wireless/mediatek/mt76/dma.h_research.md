# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/dma.h

Purpose: declares mt76 DMA descriptor formats, bitfield definitions, queue register access macros, WED/RRO/NPU descriptor helpers, queue operation prototypes, and small inline helpers shared by `dma.c` and hardware-specific mt76 drivers.

Important APIs/types/functions: defines descriptor bit masks such as `MT_DMA_CTL_SD_LEN*`, `MT_DMA_CTL_LAST_SEC*`, `MT_DMA_CTL_DMA_DONE`, token/drop/PN/RRO fields, header lengths, `struct mt76_desc`, `struct mt76_wed_rro_desc`, `struct mt76_rro_rxdmad_c`, `enum mt76_qsel`, `enum mt76_mcu_evt_type`, and `enum mt76_dma_wed_ind_reason`. Declares `mt76_dma_rx_poll`, `mt76_dma_attach`, `mt76_dma_cleanup`, `mt76_dma_rx_fill`, and `mt76_dma_queue_reset`. Provides inline `mt76_dma_reset_tx_queue`, `mt76_dma_should_drop_buf`, and `mt76_priv`.

Control flow: `Q_READ` and `Q_WRITE` abstract queue register access across plain MMIO, WED-backed queues, and optional NPU queues. `mt76_dma_reset_tx_queue` delegates to queue ops, then redoes WED DMA setup if active. `mt76_dma_should_drop_buf` decodes descriptor drop state, including newer descriptor version behavior for WED indication reasons and PN check failures. `mt76_priv` maps a dummy NAPI netdev back to its owning `mt76_dev`.

State and persistence: no independent state; structures describe coherent DMA descriptors and helper functions inspect queue/device state. Drop decisions are derived from descriptor `ctrl`, `buf1`, and `info` values produced by hardware.

Dependencies and integration: depends on Linux bitfield macros, MMIO accessors, optional `CONFIG_NET_MEDIATEK_SOC_WED`, optional `CONFIG_MT76_NPU`, RCU/regmap for NPU register access, mt76 queue flags, WED setup helpers, and netdev private storage. It is tightly coupled to `dma.c` descriptor programming.

Risks: bit definitions are hardware ABI; wrong masks corrupt descriptor programming. `Q_READ/Q_WRITE` macro branches must use the correct queue variable and are sensitive to compile-time config combinations. Drop logic changes receive semantics for repeat/old/PN-fail packets; errors can either leak bad frames upward or drop valid fragments. `DMA_DUMMY_DATA` uses an invalid pointer sentinel and must never be dereferenced.

Test signals: compile with WED enabled, NPU enabled, and neither enabled; validate descriptor bit encoding in TX/RX paths; exercise `mt76_dma_should_drop_buf` cases for normal, repeat, old packet with/without fragment, PN failure, and legacy descriptor versions; verify dummy netdev private lookup during NAPI.
