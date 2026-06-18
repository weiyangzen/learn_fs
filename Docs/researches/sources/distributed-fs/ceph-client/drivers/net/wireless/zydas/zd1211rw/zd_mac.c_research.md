# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_mac.c

## Purpose
Implements the mac80211 softmac layer for ZD1211RW. It describes 2.4 GHz channels/rates, allocates/registers `ieee80211_hw`, implements ieee80211 operations, translates TX/RX frames to and from Zydas firmware formats, tracks ACK status, configures interface filters/multicast/beacons, and runs LED and beacon watchdog work.

## Important APIs, Types, And Functions
Exports `zd_mac_alloc_hw()`, `zd_mac_clear()`, `zd_mac_preinit_hw()`, `zd_mac_init_hw()`, `zd_mac_rx()`, `zd_mac_tx_failed()`, `zd_mac_tx_to_dev()`, `zd_op_start()`, `zd_op_stop()`, and `zd_restore_settings()`. Static mac80211 ops include `zd_op_tx`, `zd_op_add_interface`, `zd_op_remove_interface`, `zd_op_config`, `zd_op_prepare_multicast`, `zd_op_configure_filter`, `zd_op_bss_info_changed`, and `zd_op_get_tsf`. Key helpers include `fill_ctrlset()`, `zd_calc_tx_length_us()`, `filter_ack()`, `zd_mac_tx_status()`, `zd_mac_config_beacon()`, `zd_process_intr()`, beacon watchdog handlers, and link LED housekeeping.

## Control Flow
Probe allocates `ieee80211_hw`, initializes local channel/rate tables and work items, then reads the permanent MAC before registration. `start` initializes USB hardware if needed, enables USB interrupts, sets basic rates/filter/hash, powers radio, enables RX/TX and hardware interrupts, then starts periodic work. TX prepends `struct zd_ctrlset`, computes PLCP service/current length, stores the hw pointer in skb metadata, and submits through USB. TX completion either reports immediate status or queues the frame for ACK matching; retry-fail USB interrupts call `zd_mac_tx_failed()`. RX validates length/status, builds `ieee80211_rx_status`, filters ACKs into TX status, copies data into a new skb, and calls `ieee80211_rx_irqsafe()`. AP/IBSS/mesh beacon changes write the beacon FIFO under a hardware semaphore and watchdog recovery resets stale beacon state.

## State And Persistence
`struct zd_mac` persists the current vif/type, regulatory domain, channel, multicast hash, association state, filter flags, ack wait queue, pending ACK signal, channel/rate tables, and delayed work. `beacon.cur_beacon` caches the last programmed beacon to avoid redundant writes. Hardware state persists through chip registers and is restored by `zd_restore_settings()` after USB reset/resume.

## Dependencies And Integration Points
Depends on mac80211/cfg80211 APIs, netdevice helpers, USB reset queueing, local chip/RF/USB APIs, global `zd_workqueue`, and Linux skb/workqueue/spinlock infrastructure. It is called by the USB probe/reset paths and calls into chip methods for all hardware register updates.

## Risks
ACK accounting is heuristic and queue-based; lost or reordered retry-fail/ACK interrupts can misreport TX status. Beacon programming can wedge if `CR_BCN_FIFO_SEMAPHORE` is not released, so the code resets the USB device on timeout. RX uses unlocked reads of filter flags by design. Single-vif assumptions are enforced by `mac->type != UNSPECIFIED`. `set_mac_and_bssid()` returns `-1` when no vif exists rather than a conventional errno. Repeated copies on RX and beacon writes are simple but not zero-copy.

## Test Signals
Validate station, AP, ad-hoc, mesh, and monitor-like filter cases; TX status under success, retry fail, no-ACK, queue pressure, and AP buffered multicast after beacon; RX bad-FCS pass-through, control-frame pass-through, ACK filtering, QoS/A4 padding; regulatory hints from EEPROM; beacon semaphore timeout recovery; reset/resume restore; LED scanning/associated behavior.
