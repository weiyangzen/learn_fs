<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mmio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mmio.c

Purpose: MMIO/PCI DMA, interrupt, beacon tasklet, MAC start, and watchdog reset support for mt76x02 devices. This is the bus-specific counterpart to USB core support.

Important APIs/types/functions: `mt76x02_dma_init()`, `mt76x02_irq_handler()`, `mt76x02_rx_poll_complete()`, `mt76x02_dma_disable()`, `mt76x02_mac_start()`, `mt76x02_wdt_work()`, and `mt76x02_reconfig_complete()`.

Control flow: DMA init allocates TX status FIFO, attaches DMA ops, creates AC/PSD/MCU TX queues, RX queues, NAPI, TX worker, and pre-TBTT tasklet. IRQ handler acknowledges masked interrupts, disables serviced sources, schedules RX/TX NAPI, pre-TBTT beacon work, TBTT PSD kick, TX status polling, and DFS tasklet. Watchdog detects stuck TX DMA or MCU timeout, stops queues/NAPI/tasklets, optionally resets mac80211 state for MCU restart, resets DMA/MAC/queues, restarts MAC/MCU, and either asks mac80211 to restart or wakes queues.

State and persistence: hardware rings, irqmask, NAPI/worker/tasklet state, txstatus kfifo, DMA indices, reset/restart bits, beacon/DFS state, and queue contents.

Dependencies/integration: mt76 DMA core, mac80211 restart/queues, DFS, beacon common code, tracepoints, shared MCU cleanup/restart, and mt76x2 PCI init.

Risks: reset ordering across IRQ/NAPI/tasklets, WCID/key sync during restart, TX status FIFO overflow, DMA busy hangs, and beacon/DFS tasklet disable balance. Test signals include IRQ flood, TX hang watchdog, MCU timeout restart, suspend/resume, beacon AP mode, DFS timer interrupts, and queue cleanup under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mmio.c -->
