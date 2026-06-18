# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/scan.c

## Purpose
Implements WiLink 8 immediate and scheduled scanning using the wl18xx unified firmware `CMD_SCAN` layout, plus scan stop and completion hooks for wlcore.

## Important APIs, types, and functions
- `wl18xx_scan_start()` sends a normal search scan through `wl18xx_scan_send()`.
- `wl18xx_scan_stop()` and `wl18xx_scan_sched_scan_stop()` use `__wl18xx_scan_stop()` with search or periodic scan type.
- `wl18xx_scan_completed()` clears scan failure and queues common scan completion work.
- `wl18xx_sched_scan_start()` configures periodic scanning through `wl18xx_scan_sched_scan_config()`.
- `wl18xx_adjust_channels()` copies shared wlcore channel-bucket output into wl18xx command fields.

## Control flow
Normal scan allocates `struct wl18xx_cmd_scan_params`, selects device or role id, fills search-scan defaults, uses `wlcore_set_scan_chan_params()` to classify channels, sets total cycles to one, adjusts rate when `no_cck` is set, copies first SSID if present, builds active 2.4 GHz and active/DFS 5 GHz probe templates, then sends `CMD_SCAN`.

Scheduled scan builds the firmware SSID list, allocates the same command structure with `SCAN_TYPE_PERIODIC`, fills filter and threshold fields, computes short/long interval cycle fields from firmware config and cfg80211 scan plan, builds periodic probe templates, sets report threshold, and sends `CMD_SCAN`. Stopping sends `CMD_STOP_SCAN` with role and scan type.

## State and persistence behavior
Immediate completion mutates `wl->scan.failed` and queues `wl->scan_complete_work`. Scheduled scan configuration is held by firmware after `CMD_SCAN`; no host persistent state is written. Inputs come from `wl->conf.scan`, `wl->conf.sched_scan`, `wlvif` role ids, and cfg80211 requests.

## Dependencies and integration points
Depends on common wlcore scan helpers, probe template builder, wlcore command send path, mac80211 workqueue helpers, and wl18xx scan ABI. Exposed through `wl18xx_ops.scan_start`, `scan_stop`, `sched_scan_start`, and `sched_scan_stop`; completion is triggered by `event.c`.

## Risks and test signals
Risks include `WARN_ON(req->n_ssids > 1)` because only the first SSID is copied, no explicit empty-channel failure after `wlcore_set_scan_chan_params()`, active/DFS probe-template band handling, role id validity for P2P management, and interval truncation to 16-bit fields. Test normal scans with no SSID, one SSID, no-CCK, DFS channels, P2P device role, scheduled scan with short/long plan behavior, stop for both scan types, and firmware scan-complete events.
