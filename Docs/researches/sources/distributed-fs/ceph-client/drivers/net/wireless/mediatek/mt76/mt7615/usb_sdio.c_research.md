# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/usb_sdio.c

Purpose: Shared MT7663 USB/SDIO helper layer for register maps, TX descriptor preparation/completion, rate update work, USB DMA scheduler setup, common hardware init, and common mac80211 registration.

Important APIs and functions: `mt7663_usb_sdio_reg_map[]` defines absolute register bases for non-PCI transports. `mt7663_usb_sdio_write_txwi()` writes a USB/SDIO-sized TXWI before skb data. `mt7663_usb_sdio_set_rates()` programs WTBL rate fields and LPON TSF-derived rate-set state. `mt7663_usb_sdio_rate_work()` drains queued WTBL rate descriptors under PM mutex. `mt7663_usb_sdio_tx_status_data()` polls station stats. `mt7663_usb_sdio_tx_complete_skb()` removes transport headroom and completes skb status. `mt7663_usb_sdio_tx_prepare_skb()` handles rate-probe setup, packet ID, TXWI push, USB length header, and padding. `mt7663u_dma_sched_init()` configures DMASHDL/UDMA for USB. `mt7663_usb_sdio_register_device()` performs common init, headroom/max-fragment setup, mac80211 registration, VHT AMSDU adjustment, MCU work scheduling, TX power init, and debugfs init.

Control flow: USB and SDIO probes allocate transport queues, then call `mt7663_usb_sdio_register_device()`. TX preparation rewrites skb headroom in-place before mt76 queueing. Rate changes are queued on `dev->wrd_head`, then workqueue context programs WTBL with device awake. Common registration initializes EEPROM/global WCID before mac80211 registration and schedules transport-specific MCU init work.

State and persistence: Maintains WTBL rate fields, station `rate_probe`, `rate_set_tsf`, `rate_count`, `wcid.tx_info`, queued rate descriptors, global WCID 0, `MT76_STATE_INITIALIZED`, USB SG-dependent headroom/fragment limits, and VHT capability adjustment. No persistent storage beyond EEPROM reads.

Dependencies: mt76 USB/SDIO helpers, `mt7615_mac_write_txwi()`, EEPROM init, mt7615 common init/debugfs/TX power, WTBL/LPON/DMASHDL/UDMA registers, and Connac PM mutex wrappers.

Risks: skb headroom and padding differ between USB and SDIO; mistakes corrupt packets or completion pulls. WTBL update polling can time out and rate-work return values are not surfaced. Packet ID must be removed on padding failure. USB SG capability changes maximum A-MSDU behavior. Register-map exports are shared by both bus modules.

Test signals: USB and SDIO TX/RX traffic, TX status completion, rate probing, WTBL rate update behavior, no-SG VHT cap downgrade, DMA scheduler register programming on USB, and common registration/debugfs success.
