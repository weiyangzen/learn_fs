# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/sdio.c

## Purpose
Provides the shared SDIO bus implementation for mt76 devices. It handles SDIO register access before and after MCU startup, hardware ownership/interrupt initialization, queue allocation, TX/RX queue ops, TX status workers, RX delivery workers, and SDIO worker lifecycle.

## Important APIs, Types, And Functions
Exported register/bus APIs include `mt76s_rr()`, `mt76s_wr()`, `mt76s_rmw()`, `mt76s_read_copy()`, `mt76s_write_copy()`, `mt76s_wr_rp()`, `mt76s_rd_rp()`, `mt76s_read_pcr()`, and `mt76s_hw_init()`. Queue/lifecycle APIs include `mt76s_alloc_rx_queue()`, `mt76s_alloc_tx()`, `mt76s_init()`, and `mt76s_deinit()`. Queue ops are `mt76s_tx_queue_skb()`, `mt76s_tx_queue_skb_raw()`, and `mt76s_tx_kick()`.

## Control Flow
Before MCU startup, register reads/writes use mailbox handshakes through H2D/D2H registers and WHISR polling. After MCU startup they delegate to `mcu_ops`. `mt76s_hw_init()` enables the SDIO function, claims driver ownership, sets block size, enables interrupts, configures WHIER/WHCR per SDIO generation, and claims the SDIO IRQ. Runtime TX queueing prepares SKBs, appends entries, and schedules the SDIO TX/RX worker. Status workers retire completed queue entries, fetch driver TX status data, wake waiters, and reschedule the generic TX worker when data queues drain.

## State And Persistence
State lives in `dev->sdio`: `func`, `hw_ver`, `xmit_buf`, `xmit_buf_sz`, scheduler quotas, SDIO worker threads, and status/stat workers. Queue state lives in `dev->q_rx`, `dev->phy.q_tx[]`, and `dev->q_mcu[MT_MCUQ_WM]`. Hardware state includes SDIO ownership, interrupt enable bits, block size, mailbox contents, and WHCR aggregation mode.

## Dependencies And Integration Points
Depends on Linux MMC/SDIO APIs, mt76 worker helpers, mt76 queue ops, MCU register access methods, driver `tx_prepare_skb()` and `tx_status_data()` callbacks, SDIO register definitions in `sdio.h`, and `mt76s_txrx_worker()`/IRQ handling in `sdio_txrx.c`.

## Risks
Mailbox register access has timeout and mismatch failure modes. Queue entry publication relies on memory barriers before bus access. Raw MCU SKBs are freed differently from data SKBs. Deinit must stop all workers, flush pending TX status, release SDIO IRQ under host claim, and free queued RX SKBs; ordering mistakes can cause use-after-free or stalled SDIO IRQs.

## Test Signals
SDIO probe on CONNAC and CONNAC2 devices, driver ownership acquisition, interrupt delivery, register access both before and after MCU startup, TX/RX queue activity, suspend/reset paths with `MT76_MCU_RESET`, clean deinit, and no stuck `tx_wait` or `MT76_READING_STATS` bits.
