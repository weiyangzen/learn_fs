# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/usb.c

Purpose: USB bus driver for MT7921U devices. It declares supported USB IDs, adapts MCU send and reset flows to USB endpoints, probes/registers the mt76 device, and implements USB suspend/resume.

Important APIs/types/functions: `mt7921u_probe()` allocates and registers the device; `mt7921u_mcu_send_message()` sends MCU/FWDL messages over bulk endpoints; `mt7921u_mcu_init()` installs MCU ops and runs firmware; `mt7921u_mac_reset()` recovers the chip; PM hooks `mt7921u_suspend()` and `mt7921u_resume()` coordinate HIF suspend and USB queue restart.

Control flow: probe selects mac80211 ops/features from firmware name, allocates mt76 device with USB/SDIO TX handlers, resets the USB device, initializes mt76 USB bus ops, reads ASIC revision, resets already-running firmware if needed, powers MCU, allocates queues, initializes DMA, configures TX fragmentation based on scatter-gather support, and calls `mt7921_register_device()`. Reset stops workers/RX/TX, resets WFSYS, resumes RX, powers MCU, initializes DMA, reruns firmware/eeprom/MAC, and restarts.

State/persistence: uses USB interface driver data, device revision, `dev->fw_features`, `dev->hif_ops`, `MT76_RESET`/`MT76_MCU_RESET` bits, UDMA firmware download select, PM suspended flag, and USB queue/DMA state. Firmware files are declared with `MODULE_FIRMWARE`.

Dependencies/integration: integrates Linux USB core, mt76 USB helpers, common MT792x USB helpers, MT7921 core registration, connac2 MCU framing, and mac80211 device ops. Device table includes MediaTek, Comfast, Netgear, and TP-Link IDs.

Risks: probe calls `usb_reset_device()` before mt76 initialization, which can disturb composite/host state if assumptions change. Resume heuristics depend on firmware suspend event bits and may require DMA reinit. Error cleanup must keep USB references, interface data, queues, and mt76 allocation balanced.

Test signals: enumerate every USB ID, firmware download over correct endpoints, reset after firmware assert, suspend/resume with and without DMA reinit, scatter-gather AMSDU behavior, and clean disconnect/error paths.
