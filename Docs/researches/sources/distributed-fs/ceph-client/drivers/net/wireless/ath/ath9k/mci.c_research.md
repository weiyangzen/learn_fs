<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/mci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/mci.c

Purpose: Implements AR9003 MCI Bluetooth coexistence policy for ath9k. It tracks BT profile/status messages, manages DMA-backed MCI scheduler/GPM buffers, updates WLAN/BT duty cycle and aggregation limits, sets coexistence TX priorities, handles MCI interrupts/messages, updates WLAN channel maps, and adjusts concurrent TX power behavior based on RSSI.

Important APIs and functions: Public entry points are `ath_mci_flush_profile()`, `ath_mci_setup()`, `ath_mci_cleanup()`, `ath_mci_intr()`, `ath_mci_enable()`, `ath9k_mci_update_wlan_channels()`, `ath9k_mci_set_txpower()`, and `ath9k_mci_update_rssi()`. Internal helpers include profile add/delete/find, `ath_mci_update_scheme()`, `ath_mci_cal_msg()`, `ath_mci_process_profile()`, `ath_mci_process_status()`, `ath_mci_msg()`, `ath_mci_set_concur_txprio()`, and `ath9k_mci_stomp_audio()`.

Control flow: Setup allocates one coherent DMA region, splits it into scheduler and GPM buffers, fills reserved patterns, calls `ar9003_mci_setup()`, and initializes work. Interrupt handling reads MCI interrupt/status bits, handles wake/sleep/reset/recovery messages, walks GPM entries until no more data, dispatches calibration messages or coexistence-agent messages, recycles entries, and queues `mci_work` when profile/status changes require scheme recalculation. Scheme update derives duty cycle, BT period, stomp type, aggregation limit, no-stomp airtime, and BTCOEX timer state from active BT profile counts and channel band.

State and persistence: Mutates `sc->btcoex.mci` profile list, profile counters, status bitmap, management count, aggregation limit, voice priority, `btcoex` duty cycle/period/stomp/no-stomp/audio/RSSI counters, `ah->btcoex_hw.mci` BT state/config/channel maps/concurrent TX flag, and MCI DMA buffer descriptors. State is runtime-only and should be flushed after BT info reset or device teardown.

Dependencies and integration points: Depends on `mci.h`, `ar9003_mci.h`, ath9k BTCOEX timer/hardware helpers, `ath9k_queue_reset()` for calibration requests, mac80211 workqueue, channel definitions, RSSI statistics, and TX power limit recalculation. `main.c` enables MCI interrupts and calls channel/TX power updates around association/offchannel/reset state.

Risks: MCI interrupt context uses GFP_ATOMIC profile allocation and list mutation; allocation failures silently drop profiles. Profile counters must stay balanced across type changes and deletes. GPM parsing uses fixed offsets and assumes alignment of payload casts. Scheme tuning is 2.4 GHz-specific and must avoid enabling BTCOEX on 5 GHz. Concurrent TX power changes are tied to calibration channel boundaries and RSSI hysteresis.

Test signals: MCI setup allocation failure, GPM version/status/profile messages, profile add/delete/type-change overflow limits, management critical status count changes, calibration request/grant reset behavior, RX invalid header recovery, 2 GHz vs 5 GHz scheme selection, WLAN channel map masking for HT20/HT40+/HT40-, concurrent TX RSSI threshold switching, and cleanup after disable/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/mci.c -->
