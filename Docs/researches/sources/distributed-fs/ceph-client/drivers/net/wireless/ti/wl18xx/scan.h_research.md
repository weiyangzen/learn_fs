# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/scan.h

## Purpose
Defines the WiLink 8 unified scan command ABI and scan function prototypes.

## Important APIs, types, and functions
- `struct tracking_ch_params` extends common channel params with BSSID fields for tracking scans.
- Probe request rate enum defines 1, 5.5, and 6 Mbps firmware encodings.
- `WL18XX_MAX_CHANNELS_5GHZ` raises the 5 GHz channel array size to 32.
- `struct wl18xx_cmd_scan_params` contains role, scan type, thresholds, filter flags, channel buckets, cycle timing, SSID, rate, and report/termination controls.
- `struct wl18xx_cmd_scan_stop` carries role id and scan type for `CMD_STOP_SCAN`.
- Prototypes expose normal and scheduled scan operations.

## Control flow
No executable flow. `scan.c` fills these structures for search and periodic scan commands.

## State and persistence behavior
No local state. Packed structures describe transient firmware command payloads that install scan state in firmware.

## Dependencies and integration points
Includes wlcore core, command, and common scan headers. The anonymous union in `wl18xx_cmd_scan_params` lets callers use either per-band channel arrays or tracking-scan channels against the same firmware area.

## Risks and test signals
ABI size/packing and channel array bounds are primary risks. Runtime tests are successful immediate/scheduled scans across 2.4/5 GHz, DFS scans, and stop commands.
