# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/pci_init.c

Purpose: Common PCI/MMIO registration and teardown path after raw MMIO probing. It initializes EEPROM/DMA/global WCID state, registers with mac80211, starts asynchronous MCU initialization, and tears down the device.

Important APIs and functions: `mt7615_pci_init_work()` retries `mt7615_mcu_init()` up to ten times on `-EAGAIN`, then calls `mt7615_init_work()`. `mt7615_init_hardware()` clears interrupt source, initializes EEPROM, performs MT7663 RGU toggling, initializes DMA, marks `MT76_STATE_INITIALIZED`, and allocates global WCID 0 for beacon/mgmt frames. `mt7615_register_device()` performs common device init, reset work setup, optional LED callbacks, MT7622 WMAC init, hardware init, `mt76_register_device()`, thermal init, MCU work scheduling, TX power init, ext-phy registration, and debugfs init. `mt7615_unregister_device()` waits for MCU, unregisters ext phy and mac80211, exits MCU, releases tokens/DMA/tasklet, and frees mt76 device.

Control flow: Bus probe calls `mt7615_register_device()` after IRQ/MMIO setup. Registration initializes low-level state before mac80211 registration, then schedules firmware init asynchronously so the netdev can complete setup while firmware retry logic runs in workqueue context. Unregister reverses order, avoiding MCU exit if firmware never ran.

State and persistence: Initializes EEPROM-backed state in `dev->mt76.eeprom`, DMA rings, global WCID array, LED callbacks, reset work, thermal/debugfs state, and optional DBDC ext phy. Persistent calibration comes from EEPROM/efuse, not written here.

Dependencies: EEPROM, DMA, MCU, thermal, debugfs, init, MT7622 platform support, mac80211 registration, and mt76 WCID allocation.

Risks: If global WCID allocation returns nonzero, registration fails because management frames are required to use index 0. Asynchronous MCU failure is silently left after retries. Error paths after `mt76_register_device()` can return without fully unregistering earlier registration work, so callers must handle partial state carefully.

Test signals: Successful device registration, EEPROM/DMA init logs, MCU retry behavior, global WCID index 0 allocation, thermal/debugfs availability, ext-phy registration for DBDC, and clean module unload.
