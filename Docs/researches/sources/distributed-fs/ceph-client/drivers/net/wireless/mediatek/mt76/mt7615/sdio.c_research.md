# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/sdio.c

Purpose: SDIO bus frontend for MT7663S devices. It binds SDIO IDs, initializes mt76 SDIO transport, parses SDIO interrupt data, registers the shared USB/SDIO mt7615 device, and implements SDIO suspend/resume.

Important APIs and functions: `mt7663s_table[]` matches vendor/device `0x7603`. `mt7663s_txrx_worker()` wraps `mt76s_txrx_worker()` in Connac PM references and queues wake work if asleep. `mt7663s_init_work()` initializes SDIO MCU then common work. `mt7663s_parse_intr()` reads `MCR_WHISR` into `struct mt7663s_intr` and copies ISR/TX/RX/mailbox fields into mt76's generic SDIO interrupt structure. `mt7663s_probe()` allocates mt76 device, installs SDIO bus ops, initializes hardware, allocates queues, creates a FIFO-low TX/RX worker, and calls `mt7663_usb_sdio_register_device()`. PM callbacks coordinate HIF suspend, keep-power, ownership, worker disable/enable, and TX status flushing.

Control flow: SDIO probe creates `mt7615_dev`, sets `mt7663_usb_sdio_reg_map`, uses `mt76s_init()`/`mt76s_hw_init()`, reads ASIC revision, allocates interrupt buffer and queues, starts a worker, then enters shared USB/SDIO registration. Remove unregisters hw only if initialized and deinitializes mt76 SDIO.

State and persistence: Tracks SDIO function drvdata, `mdev->sdio.parse_irq`, interrupt buffer, SDIO workers, PM ownership/state, and initialized bit. No persistent storage.

Dependencies: Linux MMC/SDIO APIs, mt76 SDIO helpers, `mt7663s_mcu_init()`, shared USB/SDIO data path helpers, Connac PM helpers, and firmware declarations.

Risks: SDIO host claiming must wrap register reads/writes correctly. PM reference failure must not run TX/RX while firmware owns the device. Suspend disables multiple workers and clears stats state; missed reenable can stall traffic. Interrupt struct layout must match device WHISR layout.

Test signals: SDIO enumeration, interrupt parsing under traffic, TX/RX worker wake from low power, suspend/resume with `MMC_PM_KEEP_POWER`, post-resume traffic, and clean remove.
