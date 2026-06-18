# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/sdio_mac.c

Purpose: SDIO MAC/reset support for MT7921, covering interrupt masking, firmware/driver ownership transitions, Wi-Fi subsystem reset, host-card reset, and full MAC recovery for the SDIO variant.

Important APIs/types/functions: `mt7921s_wfsys_reset()` toggles `MCR_WHCR` reset bits and waits for `WF_RST_DONE`; `mt7921s_init_reset()` performs early reset with MCU queues drained; `mt7921s_mac_reset()` is the main SER recovery path. Internal helpers `mt7921s_enable_irq()`, `mt7921s_disable_irq()`, `mt7921s_check_bus()`, `mt7921s_host_reset()`, and work item `mt7921s_card_reset()` integrate SDIO/MMC host operations.

Control flow: reset starts by freeing pending TX SKBs, checking SDIO bus health, and returning early if the bus is marked hung. Otherwise it schedules TX queues, disables TX/SDIO workers, marks MCU reset, wakes waiters, purges MCU responses, waits for SDIO queues to empty, disables interrupts, performs WFSYS reset, reenables workers and IRQs, reloads firmware, reapplies EEPROM, reinitializes MAC, and restarts the device.

State/persistence: persistent state is in hardware registers, SDIO host state, `dev->mt76.bus_hung`, `dev->fw_assert`, `dev->mphy.state` bits, and mt76 worker/queue state. PM wake/sleep ownership is coordinated through `mt7921s_mcu_drv_pmctrl()` and `mt7921s_mcu_fw_pmctrl()`, but the file itself does not store durable configuration.

Dependencies/integration: depends on Linux SDIO/MMC APIs, mt76 SDIO helpers, connac2 MAC definitions, MT7921 firmware/eeprom/MAC startup functions, and mt76 worker/queue infrastructure. The global `msdio` and static `sdio_reset_work` bridge device reset to MMC host remove/add.

Risks: `msdio` is a single global pointer, so simultaneous SDIO devices would share reset context. Card reset removes/re-adds the MMC host and releases the SDIO IRQ, which is high impact. Reset sequencing is timing-sensitive and error handling after `readx_poll_timeout()` in `mt7921s_wfsys_reset()` does not propagate timeout failure.

Test signals: exercise SDIO firmware assert/SER, bus-hung detection, suspend/resume ownership handoff, TX queue drain during reset, and successful reload through `mt7921_run_firmware()`, `mt7921_mcu_set_eeprom()`, `mt7921_mac_init()`, and `__mt7921_start()`.
