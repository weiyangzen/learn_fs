# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/scan.c

## Purpose
Implements wl12xx-family hardware scan and scheduled-scan operations behind the common wlcore scan hooks. The file translates cfg80211 scan requests into wl1271 firmware command payloads, drives a multi-stage active/passive scan state machine, builds probe-request templates through wlcore command helpers, and starts/stops firmware periodic scans.

## Important APIs, types, and functions
- `wl12xx_scan_start()` starts the scan state machine through `wl1271_scan_stm()`; the cfg80211 request has already been recorded in `wl->scan.req` by common wlcore.
- `wl12xx_scan_stop()` sends `CMD_STOP_SCAN` and rejects calls while the common scan state is idle.
- `wl12xx_scan_completed()` advances the state machine after firmware scan-complete events.
- `wl12xx_sched_scan_start()` configures and starts periodic scanning; `wl12xx_scan_sched_scan_stop()` sends `CMD_STOP_PERIODIC_SCAN`.
- `wl1271_scan_send()` builds `struct wl1271_cmd_scan`, optional split-scan timeout command, probe template, and the final `CMD_SCAN`.
- `wl1271_get_scan_channels()` filters cfg80211 channels into firmware `basic_scan_channel_params` entries and marks each selected request index in `wl->scan.scanned_ch`.
- `wl1271_scan_sched_scan_config()` fills `struct wl1271_cmd_sched_scan_config`, uses wlcore shared SSID/channel helpers, and builds band-specific periodic probe templates.

## Control flow
The immediate scan flow is a four-phase state machine: 2.4 GHz active, 2.4 GHz passive, 5 GHz active, 5 GHz passive. Active phases are skipped when no SSIDs are supplied; passive phases scan remaining channels. Each phase calls `wl1271_scan_send()`, which selects a P2P device role when needed, validates the role id, computes the channel list, fills rate/band/SSID fields, builds a probe request template, sends `CMD_TRIGGER_SCAN_TO`, and then sends `CMD_SCAN`. A local sentinel `WL1271_NOTHING_TO_SCAN` causes recursive state advancement to the next phase without reporting failure.

Scheduled scan first programs an SSID filter list via `wlcore_scan_sched_scan_ssid_list()`, derives channel buckets through `wlcore_set_scan_chan_params()`, copies them into wl12xx firmware layout with `wl12xx_adjust_channels()`, builds 2.4/5 GHz periodic probe templates for active bands, then sends `CMD_CONNECTION_SCAN_CFG`. `wl1271_scan_sched_scan_start()` then sends `CMD_START_PERIODIC_SCAN`.

## State and persistence behavior
State lives in `wl->scan`: `state`, `req`, `ssid`, `ssid_len`, `failed`, `scanned_ch`, and `scan_complete_work`. The file updates `scanned_ch` as channels are consumed so later phases skip them, clears `failed` when reaching `WL1271_SCAN_STATE_DONE`, and queues common completion work immediately. No persistent storage is written; configuration values are read from `wl->conf.scan` and `wl->conf.sched_scan`.

## Dependencies and integration points
Depends on cfg80211/mac80211 scan request structures, common wlcore scan helpers, wlcore command/probe-template helpers, `wl1271_cmd_send()`, wlcore role helpers, wlcore debug/dump utilities, and wlcore TX rate selection. It is wired into the wl12xx lower-driver ops elsewhere and relies on common wlcore event handling to call `wl12xx_scan_completed()`.

## Risks and test signals
Risks include incorrect active/passive filtering for `IEEE80211_CHAN_NO_IR`, failure to clear or initialize `scanned_ch`, invalid role ids for P2P management scans, recursion through empty scan phases, and firmware ABI mismatches in packed command structures. Useful tests are active scan with and without SSIDs, passive-only regulatory channels, 5 GHz disabled/enabled NVS cases, P2P management scans using `dev_role_id`, scheduled scan with no SSIDs forcing passive behavior, split-scan timeout handling, and stop requests during active firmware scans.
