# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/scan.h

## Purpose
Defines the wl12xx firmware scan command ABI and exports the wl12xx scan/scheduled-scan entry points used by the chip-family operation table.

## Important APIs, types, and functions
- `struct basic_scan_params` and `struct basic_scan_channel_params` are packed firmware payload fragments for normal scans.
- `struct wl1271_cmd_scan` wraps the normal scan header, parameters, fixed-size channel array, and source MAC address.
- `struct wl1271_cmd_sched_scan_config`, `wl1271_cmd_sched_scan_start`, and `wl1271_cmd_sched_scan_stop` describe firmware periodic-scan commands.
- Exports `wl12xx_scan_start()`, `wl12xx_scan_stop()`, `wl12xx_scan_completed()`, `wl12xx_sched_scan_start()`, and `wl12xx_scan_sched_scan_stop()`.

## Control flow
The header itself has no executable flow. Its packed layouts constrain how `scan.c` fills fields before issuing `CMD_SCAN`, `CMD_CONNECTION_SCAN_CFG`, `CMD_START_PERIODIC_SCAN`, and `CMD_STOP_PERIODIC_SCAN`.

## State and persistence behavior
No local state. The structures carry role ids, dwell times, filter thresholds, SSIDs, channel lists, and scan tags to firmware. Endianness annotations identify multi-byte fields that callers must convert.

## Dependencies and integration points
Includes wlcore core, command, and scan headers for common types such as `wl1271_cmd_header`, `conn_scan_ch_params`, and band/channel constants. The wl12xx-specific `WL12XX_MAX_CHANNELS_5GHZ` limit shapes scheduled-scan channel arrays.

## Risks and test signals
Packed firmware ABI drift is the main risk: field order, size, padding, or endian mistakes can corrupt firmware commands. Compile-time size checks would be valuable around firmware API updates. Runtime signals are successful normal scans, periodic scans, and stop commands on wl12xx hardware across both bands.
