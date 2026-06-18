# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_drv_txrx.c

## Purpose

`htc_drv_txrx.c` implements the ath9k HTC host TX and RX data path. It builds firmware TX headers, maps mac80211 queues to firmware endpoints, tracks outstanding SKBs by slots and cookies, consumes firmware TX status events, handles TX cleanup/timeouts, configures TX queues, computes RX filters, validates firmware RX status headers, and hands accepted frames to mac80211.

## Important APIs, Types, and Functions

TX queue pressure is managed by `ath9k_htc_check_stop_queues()` and `ath9k_htc_check_wake_queues()`, which count outstanding host frames and stop/wake mac80211 queues around `ATH9K_HTC_TX_THRESHOLD`. `ath9k_htc_tx_get_slot()` and `ath9k_htc_tx_clear_slot()` allocate cookies from `priv->tx.tx_slot`.

`ath9k_htc_tx_start()` is the main transmit entry after `htc_drv_main.c` has selected a slot. It resolves firmware VIF and station indices, dispatches to `ath9k_htc_tx_data()` for data frames or `ath9k_htc_tx_mgmt()` for management frames, then sends through `htc_send()`. `ath9k_htc_tx_data()` fills `struct tx_frame_hdr` with node, VIF, cookie, data type, TID, RTS/CTS flags, crypto key type/index, and endpoint selection. `ath9k_htc_tx_mgmt()` fills `struct tx_mgmt_hdr` and handles probe response TSF adjustment.

Completion handling uses two stages. `ath9k_htc_txep()` is called by the HTC endpoint TX callback after HIF submission completes; successful SKBs are queued per endpoint, failed SKBs go to `tx_failed` and a tasklet. Later, WMI firmware status enters `ath9k_htc_txstatus()`, which locates the matching queued SKB by endpoint and cookie via `ath9k_htc_tx_get_packet()`. `ath9k_htc_tx_process()` strips firmware headers, maps status flags into `ieee80211_tx_info`, clears queued counters/slots, removes padding, and calls `ieee80211_tx_status_skb()`.

RX initialization and cleanup are `ath9k_rx_init()` and `ath9k_rx_cleanup()`. `ath9k_htc_rxep()` places incoming endpoint SKBs into an available `ath9k_htc_rxbuf` and schedules `ath9k_rx_tasklet()`. `ath9k_rx_prepare()` validates the firmware RX header, converts `struct ath_htc_rx_status` to `struct ath_rx_status`, processes errors, rate, RSSI, decrypt status, spectral/PHY errors, and fills mac80211 `ieee80211_rx_status`.

## Control Flow

The TX path is: mac80211 callback reserves padding and a TX slot, `ath9k_htc_tx_start()` prepends a firmware header, `htc_send()` prepends an HTC frame header and sends over HIF, `ath9k_htc_txep()` queues the SKB by endpoint after host submission, firmware later emits WMI TX status, `ath9k_htc_txstatus()` matches status to SKB, and `ath9k_htc_tx_process()` returns final status to mac80211. If the status arrives before the SKB is queued, the status is saved in `pending_tx_events` and retried by `ath9k_htc_tx_cleanup_timer()`.

The drain path sets `ATH9K_HTC_OP_TX_DRAIN`, stops HTC, kills WMI and failed-TX tasklets, drains every endpoint queue through `ath9k_htc_tx_process(..., NULL)`, frees pending TX events, and clears the drain flag. The cleanup timer scans pending status events and status-pending endpoint queues for timeout, returning timed-out frames to mac80211 with failure status.

The RX path is: HTC endpoint callback receives an SKB, claims a free RX buffer under `rxbuflock`, marks it in process, schedules the tasklet, validates/prepares the frame, copies RX status into the skb control block, queues PS work for beacons when PS is enabled, calls `ieee80211_rx()`, and requeues the RX buffer.

## State and Persistence Behavior

Persistent TX state includes endpoint SKB queues, the failed queue, queued count, queue stop/drain flags, slot bitmap, pending TX status list, per-AC queue statistics, and cleanup timer timestamps in `ath9k_htc_tx_ctl`. RX state is a fixed list of `ATH9K_HTC_RXBUF` host buffers with `in_process` and `skb` fields plus an `initialized` gate. Firmware station/VIF indices are embedded in each firmware TX header, and TX status uses endpoint/cookie matching rather than pointer identity.

## Dependencies and Integration Points

The file depends on mac80211 SKB control blocks, HTC endpoint callbacks, WMI TX status events, firmware header definitions from `htc.h`, shared ath9k queue APIs, common RX post-processing helpers, spectral scan helpers, and hardware RX filter/register functions from `hw.c`.

## Risks

The TX completion path is vulnerable to ordering races between HIF completion and WMI status, which is why `pending_tx_events` exists. Cookie reuse must be bounded by slot clearing; premature slot reuse can misattribute TX status. Queue counters must be decremented exactly once or queues can stick stopped. RX validation must reject short or inconsistent firmware-reported lengths before `skb_pull()`. RX cleanup and init are explicitly marked with a locking FIXME, so teardown during endpoint activity is a sensitive area. Timer callbacks, tasklets, and drain paths all touch the same queues and lists.

## Test Signals

Useful tests include high-throughput TX to force queue stop/wake, injected HIF submission failure, delayed or reordered TX status, TX timeout cleanup, AMPDU start and status mapping, management frame TX status, CAB/multicast traffic, malformed or short RX frames, invalid RX key indexes, PHY error/spectral frames, PS beacons scheduling `ps_work`, RX init failure cleanup, and hot unplug while endpoint queues contain SKBs.
