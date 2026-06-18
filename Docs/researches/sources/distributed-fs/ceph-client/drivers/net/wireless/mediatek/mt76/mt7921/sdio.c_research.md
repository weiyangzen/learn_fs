# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/sdio.c

## Purpose
This file is the SDIO transport driver for MT7921S and MT7902 SDIO devices. It owns SDIO device matching, bus initialization, interrupt parsing, RX/TX queue setup, SDIO worker PM gating, common device registration, remove, suspend/resume, and module metadata.

## Important APIs, Types, And Functions
The module entry is `module_sdio_driver(mt7921s_driver)`. Core callbacks are `mt7921s_probe()`, `mt7921s_remove()`, `mt7921s_suspend()`, and `mt7921s_resume()`. `mt7921s_txrx_worker()` wraps the generic SDIO TX/RX worker with mt76 connac PM references. `mt7921s_unregister_device()` performs cleanup. `mt7921s_parse_intr()` reads and validates SDIO interrupt status into generic `struct mt76s_intr`.

## Control Flow
Probe obtains mac80211 ops based on firmware metadata, allocates an mt76 device with SDIO-oriented driver ops, installs HIF ops, initializes the SDIO bus and hardware, reads ASIC revision, installs interrupt parser and interrupt data buffer, allocates main and MCU RX queues plus TX resources, creates the SDIO txrx worker with FIFO scheduling, and calls `mt7921_register_device()`.

The txrx worker takes a PM reference; if the device is asleep it queues wake work and returns, otherwise it runs `mt76s_txrx_worker()` and drops the PM reference. Interrupt parsing claims the SDIO host, reads `MCR_WHISR` into `mt7921_sdio_intr`, rejects impossible RX counts, and exposes ISR/mailbox/TX quota/RX length arrays. Suspend marks PM suspended, sets `MT76_STATE_SUSPEND`, cancels PM/reset/ROC work, takes driver ownership, forces deep sleep, drains TX queues, suspends HIF, disables SDIO workers, gives firmware ownership, and asks MMC to keep power. Resume clears suspend state, takes driver ownership, re-enables workers, restores deep sleep if needed, clears HIF suspend, and resets on failure.

## State And Persistence
State includes SDIO drvdata, `fw_features`, HIF ops, bus ops, interrupt buffer, SDIO wait queue, txrx/status/stat/net workers, PM suspend flag, suspend state bit, bus_hung flag, revision, SDIO scheduler quotas populated by MCU capability parsing, and RX/TX queues. Hardware state includes SDIO function registers, HIF suspend state, deep sleep, firmware/driver ownership, and retained MMC power during suspend.

## Dependencies And Integration Points
It depends on Linux MMC/SDIO APIs, mt76 SDIO core, common MT7921 mac80211/MAC/MCU functions, SDIO reset/MCU helpers in `sdio_mac.c`/`sdio_mcu.c`, and mt792x PM helpers.

## Risks
Interrupt parsing is layout-sensitive; invalid RX counts are rejected to avoid overruns. Worker PM gating can starve TX/RX if wake work fails. Suspend requires all TX queues to empty before HIF suspend; timeout or worker ordering mistakes can hang resume. Error paths call `mt76s_deinit()` and `mt76_free_device()` before registration, while registered removal uses `mt7921s_unregister_device()`.

## Test Signals
Probe MT7921 and MT7902 SDIO IDs, parse interrupts with RX count limits, run traffic through PM sleep/wake cycles, suspend/resume with MMC keep-power, drain TX queues, remove during init failure, and validate reset on resume/suspend failures. Debugfs `sched-quota` should reflect SDIO scheduler data after NIC capability parsing.
