# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/ps.c

## Purpose
`ps.c` implements wlcore power-save helpers for STA firmware power-save mode and AP-side station power-save accounting. It translates mac80211/driver power-save state into firmware ACX/CMD calls and keeps mac80211 informed when connected AP clients enter or leave sleep.

## Important APIs, Types, and Functions
`wl1271_ps_set_mode()` is the STA-side entry point. It accepts `STATION_AUTO_PS_MODE`, `STATION_POWER_SAVE_MODE`, or `STATION_ACTIVE_MODE`, programs wake-up conditions with `wl1271_acx_wake_up_conditions()`, sends `wl1271_cmd_ps_mode()`, toggles `WLVIF_FLAG_IN_PS`, and enables/disables beacon early termination for 2.4 GHz low-basic-rate links. `wl12xx_ps_link_start()` and `wl12xx_ps_link_end()` are AP-side helpers that use an HLID and `wlvif->ap.sta_hlid_map` to notify mac80211 of station sleep transitions through `ieee80211_sta_ps_transition_ni()`. The private `wl1271_ps_filter_frames()` marks queued frames for a sleeping station as `IEEE80211_TX_STAT_TX_FILTERED` and returns them to mac80211.

## Control Flow
STA power-save entry first configures wake conditions and then asks firmware to enter auto/forced PSM. Active mode reverses beacon early termination before leaving firmware PSM. AP station sleep starts only for AP vifs with an allocated station HLID and no existing bit in `wl->ap_ps_map`; after mac80211 notification it optionally drains the per-link low-level TX queues. Power-save end clears `wl->ap_ps_map` and notifies mac80211 that the station is awake.

## State and Persistence Behavior
The file updates in-memory flags only: `WLVIF_FLAG_IN_PS`, `wl->ap_ps_map`, global `wl->tx_queue_count[]`, and per-vif `tx_queue_count[]`. It does not persist data across reloads. Queue filtering returns ownership of queued SKBs to mac80211 and updates watermarks via `wl1271_handle_tx_low_watermark()`.

## Dependencies and Integration Points
Dependencies include `ps.h`, `io.h`, `tx.h`, `debug.h`, ACX/CMD helpers declared through wlcore headers, skb queues, RCU station lookup, and mac80211 station power-save notifications. `main.c` calls these helpers from BSS power-save changes and AP firmware-status regulation.

## Risks and Test Signals
Primary risks are stale HLID/station mappings, queue count underflow if filtering diverges from enqueue accounting, and RCU lookup failures during station removal. Tests should exercise STA PS on/off, AP client sleep/wake transitions, sleeping-client frame filtering, low-watermark wakeup, and 2.4 GHz beacon early termination gating.
