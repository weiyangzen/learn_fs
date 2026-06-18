# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/mac.c

## Purpose
This file implements MT7921 MAC data-path support shared by PCI, SDIO, and USB. It parses RX descriptors, dispatches MCU events and TX status/free notifications, updates station airtime/rate/RSSI data from WTBL, handles chip reset and coredump work, and provides USB/SDIO TX descriptor preparation/completion helpers.

## Important APIs, Types, And Functions
Exported entry points include `mt7921_mac_wtbl_update()`, `mt7921_rx_check()`, `mt7921_queue_rx_skb()`, `mt7921_mac_reset_work()`, `mt7921_coredump_work()`, `mt7921_usb_sdio_tx_prepare_skb()`, `mt7921_usb_sdio_tx_complete_skb()`, and `mt7921_usb_sdio_tx_status_data()`. Internal core helpers include `mt7921_mac_sta_poll()`, `mt7921_mac_fill_rx()`, `mt7921_mac_add_txs()`, `mt7921_mac_tx_free()`, and `mt7921_vif_connect_iter()`.

## Control Flow
RX enters through `mt7921_queue_rx_skb()` or `mt7921_rx_check()`. Packet type selects TX free processing, TX status parsing, MCU event handling, or normal RX descriptor parsing. Normal RX validation rejects wrong band, non-running state, malformed A-MSDU/header translation cases, descriptor length errors, and unsupported rate parse results. Valid frames receive status metadata, checksum state, decryption flags, RSSI/rate/radiotap data, A-MPDU sequence info, and are passed to `mt76_rx()`.

TX free notifications clean DMA queues, release mt76 tokens, update retry/failure counters, free TXWIs, schedule TX worker, and poll stations. Reset work stops queues, cancels PM work, retries `mt792x_dev_reset()`, aborts scans if needed, wakes queues, reconnects active interfaces through MCU dev/BSS/STA/beacon commands, and reschedules power save. Coredump work aggregates queued firmware assert fragments before calling `dev_coredumpv()` and resetting.

## State And Persistence
State includes per-WCID airtime counters, rate info, average ACK signal, TX token idr, reset flags (`MT76_RESET`, `hw_full_reset`, `fw_assert`), scan state, coredump message queues, IPv6 NS queue, and PM queues. Hardware state includes WTBL counters, RX/TX descriptors, DMA queues, firmware assert data, beacon offload, BSS contexts, and station contexts rebuilt after reset.

## Dependencies And Integration Points
The code integrates mt76 DMA/token/RX/TX helpers, mac80211 RX status APIs, connac2 descriptor formats, MCU event code from `mcu.c`, common mt792x reset/PM helpers, coredump framework, and transport driver ops. USB/SDIO helpers are used by SDIO and USB modules; PCI uses `pci_mac.c`.

## Risks
RX descriptor parsing is length-sensitive and mixes header-translated and 802.11 paths; mistakes can corrupt SKBs or radiotap metadata. TX free parsing increments count when encountering WCID pairs and must stay within event bounds. Reset recovery does not fully replay all mac80211 state itself, so ordering with mac80211 queues, scans, PM, and firmware restart matters. Coredump aggregation drops excess data silently when exceeding the fixed dump size. USB/SDIO pad/headroom errors must release packet IDs.

## Test Signals
Test normal RX, monitor RX, header translation, fragmented encrypted frames, A-MSDU, checksum offload, HE radiotap, TX status and TX free events, airtime accounting, reset during scan and traffic, firmware coredump generation, USB/SDIO TX headroom/padding, and IPv6 NS offload work. KASAN, lockdep, and skb bounds diagnostics are important for this file.
