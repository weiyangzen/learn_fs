# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/mac.c

## Purpose
MT7603 low-level MAC, WTBL, RX/TX descriptor, rate-control, security, airtime, DMA control, watchdog reset, EDCCA, CCA, and sensitivity implementation.

## Important APIs, Types, And Functions
- TX arbitration helpers stop/start AC queues; `mt7603_mac_start()`, `mt7603_mac_stop()`, and `mt7603_mac_dma_start()` control MAC and WPDMA operation.
- WTBL management: `mt7603_wtbl_init()`, `mt7603_wtbl_clear()`, `mt7603_wtbl_update_cap()`, `mt7603_wtbl_set_smps()`, `mt7603_wtbl_set_ps()`, `mt7603_filter_tx()`, `mt7603_wtbl_set_rates()`, and `mt7603_wtbl_set_key()`.
- Block-ack helpers: `mt7603_mac_rx_ba_reset()` and `mt7603_mac_tx_ba_reset()`.
- RX parsing: `mt7603_mac_fill_rx()` decodes RX descriptors/RXV groups, security state, A-MPDU metadata, RSSI, rate/band/frequency, padding, and CCMP header reinsertion.
- TX building/status: `mt7603_mac_write_txwi()`, `mt7603_tx_prepare_skb()`, `mt7603_fill_txs()`, `mt7603_mac_add_txs_skb()`, `mt7603_mac_add_txs()`, and `mt7603_tx_complete_skb()`.
- Recovery and maintenance: `mt7603_pse_client_reset()`, `mt7603_pse_reset()`, `mt7603_mac_watchdog_reset()`, DMA busy/hang checks, `mt7603_mac_work()`, `mt7603_update_channel()`, `mt7603_cca_stats_reset()`, EDCCA, and dynamic sensitivity adjustment.

## Control Flow
Normal TX enters through common mt76 queues into `mt7603_tx_prepare_skb()`, which handles PS wake conditions, aggregation sequence checks, TX-status PID allocation, optional probe-rate WTBL update, and TXWI construction. Hardware TX status frames are parsed by DMA RX dispatch into `mt7603_mac_add_txs()`, which matches SKBs by PID or emits no-SKB status. Normal RX frames are parsed by `mt7603_mac_fill_rx()` and passed to shared mt76 RX. Station setup and rate updates program WTBL records. Periodic `mt7603_mac_work()` updates surveys, EDCCA, aggregation stats, false-CCA sensitivity, and watchdog counters; on persistent hangs it performs a full MAC/DMA/PSE reset and restarts queues/NAPI/tasklets.

## State And Persistence
State spans WTBL hardware entries, per-station `struct mt7603_sta` fields (`ps`, `smps`, rate sets, airtime counters, `psq`), `dev->mphy.aggr_stats`, RX A-MPDU timestamp/reference, RSSI offsets, reset-cause counters, sensitivity/EDCCA fields, DMA indices, watchdog counters, `tx_power_limit`, and queue/NAPI state. Security keys are written into WTBL key memory. All state is runtime hardware/driver state.

## Dependencies And Integration Points
Depends on mt76 core TX/RX/status/reorder helpers, mac80211 station/rate/key APIs, mt7603 descriptor definitions from `mac.h`, register definitions from `mt7603.h`, beacon and DMA paths, and debugfs readers. Firmware/MCU channel and txpower state complements but does not replace MAC register setup.

## Risks
This is the highest-risk file in the subset. Descriptor parsing must validate group lengths before `skb_pull()`. TX status reconstruction relies on rate-set TSF heuristics and can misreport after delayed status or rapid probe changes. WTBL programming stops TX around sensitive writes; missing stop/update/poll can corrupt peer state. PS handling moves frames between hardware loopback, per-station queues, and raw TX queues under `ps_lock`. Watchdog reset disables workers, tasklets, NAPI, IRQs, queues, and DMA; ordering mistakes can deadlock or lose interrupts. Security handling supports limited ciphers and writes raw keys into hardware memory.

## Test Signals
Stress STA/AP traffic with aggregation, rate probing, fixed-rate frames, PS/UAPSD, multicast buffering, key install/remove, TKIP/CCMP, RX FCS/MIC errors, monitor mode, channel changes, EDCCA toggling, and watchdog reset injection. Check TX status accuracy, airtime accounting, `ampdu_stat`, reset counters, no lockdep/KASAN warnings, and traffic recovery after each reset cause.
