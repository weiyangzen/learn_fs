# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/rx.c

## Purpose
`rx.c` contains the generic receive notification and response handlers for the Intel DVM driver. It dispatches firmware RX packets, handles firmware errors, channel switch notifications, spectrum and power-management notifications, statistics, RF-kill/card-state changes, missed beacons, RX PHY/MPDU data, P2P Notice of Absence updates, and setup of the RX handler table.

The file is the bridge from transport-level firmware responses to mac80211-visible RX frames and driver-maintained health/calibration state.

## Important APIs, Types, And Functions
- `iwl_setup_rx_handlers()` installs command-id handlers into `priv->rx_handlers`.
- `iwl_rx_dispatch()` is the op-mode RX dispatcher. It notifies waiters, increments handler stats, and invokes the registered handler by firmware command id.
- `iwlagn_rx_reply_error()` logs firmware `REPLY_ERROR` details.
- `iwlagn_rx_csa()` handles channel switch completion/failure and calls `iwl_chswitch_done()`.
- `iwlagn_rx_statistics()` parses normal or Bluetooth-aware statistics notifications, updates `priv->statistics`, schedules calibration work, and triggers temperature callbacks.
- `iwlagn_rx_reply_statistics()` handles explicit statistics replies and clears debugfs accumulated statistics when firmware says counters were cleared.
- `iwl_force_rf_reset()` requests a radio reset by scheduling an internal short hardware scan.
- `iwlagn_recover_from_statistics()` and `iwlagn_good_plcp_health()` detect excessive PLCP errors and trigger RF reset.
- `iwlagn_rx_card_state_notif()` processes software/hardware/thermal RF-kill state and command blocking.
- `iwlagn_rx_reply_rx_phy()` caches PHY metadata for the following MPDU.
- `iwlagn_rx_reply_rx()` validates MPDU data, builds `struct ieee80211_rx_status`, translates decrypt status, calculates RSSI, handles AMPDU metadata, and passes frames to mac80211.
- `iwlagn_pass_packet_to_mac80211()` builds an skb, attaches a stolen RX page fragment when needed, applies passive-channel beacon recovery, and calls `ieee80211_rx_napi()`.
- `iwlagn_rx_noa_notification()` replaces P2P NoA data under RCU.

## Control Flow
RX setup is table-driven. `iwl_setup_rx_handlers()` assigns handlers for firmware command IDs and delegates scan handler registration to `iwl_setup_rx_scan_handlers()`. Once operational, `iwl_rx_dispatch()` receives every RX command buffer, first wakes notification waiters through `iwl_notification_wait_notify()`, then calls the command-specific function if present.

Statistics notifications are parsed by payload length into either `struct iwl_bt_notif_statistics` or `struct iwl_notif_statistics`. Under `priv->statistics.lock`, the handler updates accumulative debug stats, checks PLCP health if associated and enough time elapsed, copies current counters into `priv->statistics`, updates `rx_statistics_jiffies`, sets `STATUS_STATISTICS`, refreshes the periodic statistics timer, queues runtime calibration work outside scan, and invokes temperature handling on relevant changes.

RX frame delivery is split between PHY and MPDU notifications. `REPLY_RX_PHY_CMD` caches `priv->last_phy_res`, sets validity, and increments an AMPDU reference. `REPLY_RX_MPDU_CMD` requires that cache, validates packet sizes and CRC/FIFO status, computes channel/frequency/rate/signal/antenna/HT flags in `ieee80211_rx_status`, translates firmware decrypt bits to mac80211 flags, and hands the payload to `iwlagn_pass_packet_to_mac80211()`.

Card-state notifications can command-block firmware, enter or exit critical-temperature handling, update hardware RF-kill state, cancel scans when RXON is not disabled, and inform cfg80211 via `wiphy_rfkill_set_hw_state()`. Missed beacon notifications reinitialize sensitivity when thresholds are exceeded and not scanning.

## State And Persistence Behavior
The file updates persistent driver state in `struct iwl_priv`: statistics snapshots and debug deltas, measurement reports and flags, `ibss_manager`, RF reset counters/timestamps, `last_phy_res` and `last_phy_res_valid`, `ampdu_ref`, `ucode_beacon_time`, `passive_no_rx`, RF-kill bits, `noa_data`, and RX handler statistics.

Most RX frame state is transient per command buffer. If a frame is larger than the allocated skb headroom, `iwlagn_pass_packet_to_mac80211()` steals the RX page into an skb fragment, transferring ownership from the RX command buffer to mac80211.

`noa_data` is RCU-replaced and old data is freed with `kfree_rcu()`. Statistics timers and calibration work persist beyond the handler invocation.

## Dependencies And Integration Points
This file depends on the transport RX buffer API (`rxb_addr()`, `rxb_offset()`, `rxb_steal_page()`), firmware command/notification structs, CSR/HBUS register accessors, mac80211 RX APIs, cfg80211 RF-kill integration, calibration (`iwl_init_sensitivity()`, runtime calibration work), scan cancellation, Bluetooth RX handler setup, station add callback, TX reply/BA handlers, and notification wait infrastructure.

It integrates with `scan.c` by installing scan handlers and canceling scans on card-state changes. It integrates with `rxon.c` through CSA channel updates and passive-channel beacon recovery. It integrates with `sta.c` through `REPLY_ADD_STA` callback registration, and with aggregation/TX through BA and TX reply handlers registered here.

## Risks And Edge Cases
- `iwlagn_rx_reply_rx()` depends on receiving a valid PHY notification before MPDU. Missing or out-of-order notifications drop the frame.
- Packet length checks protect against firmware-reported length mismatches; weakening them risks skb overread or invalid page-frag offsets.
- Decryption handling drops WEP/TKIP packets with bad ICV/MIC because hardware decrypts in place. Incorrect status translation can either leak bad frames or drop recoverable software-decrypt frames.
- Statistics parsing relies on exact payload sizes for normal vs Bluetooth statistics.
- `accum_stats()` deliberately ignores counter roll-over in debugfs builds.
- RF reset is rate-limited for internal requests but external requests bypass that interval; both require association.
- Card-state command blocking manipulates device registers and must stay synchronized with firmware RF-kill semantics.
- The passive-channel beacon workaround wakes queues when beacons for active BSSIDs arrive; incorrect BSSID matching could leave queues stopped or lift restrictions too early.

## Test Signals
Test signals include RX data delivery with small and large frames, AMPDU RX status, encrypted WEP/TKIP/CCMP success and failure cases, scan plus card-state interactions, CSA success/failure, RF-kill toggles, thermal kill entry/exit, missed beacon sensitivity reinit, statistics notifications with and without Bluetooth sections, PLCP-error recovery scans, and P2P NoA update/free behavior under RCU. NAPI RX tests should verify that stolen RX pages are not reused after skb handoff.
