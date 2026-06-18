# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/pci.c

Purpose: this file implements the PCIe MT76x0 driver: PCI probe/remove, mac80211 operations, start/stop, hardware init, suspend/resume, and module registration for MT7610/MT7630/MT7650 devices.

Important functions: `mt76x0e_probe` enables PCI, maps BAR0, sets DMA mask, allocates an `mt76x02_dev`, initializes MMIO, requests IRQ, and registers the device. `mt76x0e_init_hardware` powers WLAN on, loads MCU firmware through `mt76x0e_mcu_init`, initializes DMA when not resuming, runs common hardware init, configures beacon behavior, and applies PCI/chip quirks. `mt76x0e_start` starts MAC/calibration work; `mt76x0e_stop` and `mt76x0e_stop_hw` stop running state and drain DMA/MAC. `mt76x0e_cleanup`, `mt76x0e_remove`, `mt76x0e_suspend`, and `mt76x0e_resume` handle teardown and PM.

Control flow: probe follows standard PCI driver ordering: enable, map, master, DMA mask, disable ASPM, allocate mt76 device, init MMIO/revision, mask interrupts, request IRQ, then register. Registration calls hardware init and common mac80211 registration, then sets initialized state. Runtime start schedules MAC and calibration delayed work. Stop/suspend cancel work, disable workers/NAPI/DMA, clean queues, stop MAC, and power down. Resume restores PCI state, re-enables worker/NAPI, schedules NAPI, then reinitializes hardware with resume flag.

State and persistence behavior: persistent runtime state includes `MT76_STATE_RUNNING`, `MT76_STATE_INITIALIZED`, queue/NAPI state, DMA enable bits, delayed works, PCI power state, and WLAN function power. It reads EEPROM for quirks but does not persist hardware storage.

Dependencies and integration: integrates with Linux PCI, mac80211 `ieee80211_ops`, mt76 MMIO/DMA/IRQ helpers, common MT76x0 init/PHY/main APIs, PCI MCU loader, and mt76x02 shared callbacks for TX/RX, stations, keys, AMPDU, survey, and debug.

Risks: resume skips DMA init but still reinitializes hardware, so queue/NAPI ordering must be correct. Stop warnings mention TX DMA twice, including the RX wait path. Empty `flush` may be acceptable through mt76 queues but gives no explicit drain semantics. Hardware quirks for MT7610 PA current and raw registers need device coverage.

Test signals: PCI probe/remove, firmware load, IRQ RX/TX traffic, suspend/resume, module unload under traffic, DFS/channel switching, calibration work scheduling, and devices for all PCI IDs. Check no DMA busy warnings or queue leaks appear.
