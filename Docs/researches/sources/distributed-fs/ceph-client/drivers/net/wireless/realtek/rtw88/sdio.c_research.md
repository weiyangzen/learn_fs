## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/sdio.c

Purpose: SDIO HCI implementation for rtw88. It provides register access, firmware/H2C/reserved-page writes, RX FIFO draining, TX queueing, interrupt handling, power-save hooks, probe/remove/shutdown, and `rtw_hci_ops` for SDIO devices.

Important APIs/functions: exported `rtw_sdio_probe`, `rtw_sdio_remove`, `rtw_sdio_shutdown`, and `rtw_sdio_pm_ops`. Core internal functions include direct/indirect read/write helpers, `rtw_sdio_read_port`, `rtw_sdio_write_port`, `rtw_sdio_check_free_txpg`, RX aggregation setup, IRQ handler `rtw_sdio_handle_interrupt`, TX worker `rtw_sdio_tx_handler`, and HCI ops `rtw_sdio_ops`.

Control flow: probe allocates `ieee80211_hw` plus `rtw_sdio`, initializes core, claims/enables the SDIO function, initializes IRQ mask and TX workqueue, sets chip info, claims SDIO IRQ, then registers mac80211 hardware. Interrupts read/ack HISR, handle TX errors and RX requests, drain RX lengths up to a 64 KiB budget, split aggregated frames, route C2H or mac80211 RX, and clear status. TX writes prepare descriptors, enqueue by hardware queue, and a single-thread workqueue drains queues with free-page checks and retry-by-requeue.

State and persistence: owns `struct rtw_sdio` fields: SDIO function, IRQ mask, RX address counter, SDIO3 mode, current IRQ thread marker, TX workqueue, work data, and per-queue skb queues. It mutates power flags for deep leisure PS.

Dependencies and integration: depends on Linux MMC/SDIO APIs, rtw88 core/mac/firmware/power/RX/TX helpers, and chip-specific page-size/free-page semantics.

Risks and test signals: high-risk areas are host-claim recursion in IRQ context, indirect register access when powered off, unaligned SDIO buffers, RX aggregation split bounds, TX free-page retry behavior, and removal while work/IRQ is active. Test with SDIO3 and non-SDIO3 hosts, suspend/resume, traffic under low TX pages, C2H events, and remove/shutdown races.
