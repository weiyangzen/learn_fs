# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/scan.h

## Purpose
`scan.h` declares common wlcore scan interfaces and defines the firmware-facing structures/constants used for regular and scheduled scans.

## Important APIs, Types, and Constants
The header declares regular scan entry points (`wlcore_scan()`, `wl1271_scan_build_probe_req()`, `wl1271_scan_stm()`, `wl1271_scan_complete_work()`), scheduled scan configuration/start/results helpers, channel parameter construction through `wlcore_set_scan_chan_params()`, and SSID-list programming through `wlcore_scan_sched_scan_ssid_list()`. It defines scan state constants, scan options, timeout (`WL1271_SCAN_TIMEOUT` 30000 ms), maximum channel arrays, SSID filter types, BSS types, scan channel flags, packed `struct conn_scan_ch_params`, packed `struct wl1271_cmd_sched_scan_ssid_list`, `struct wlcore_scan_channels`, and scan type enum values.

## Control Flow and Integration
There is no executable logic in the header. Its structures are filled by `scan.c` and consumed by chip-specific scan implementations and firmware command routines. `scan_complete_work` is shared with `main.c` allocation and cancellation paths.

## State, Risks, and Test Signals
The header stores no state. The packed command structures must match firmware ABI; max array sizes must remain compatible with wl12xx and wl18xx channel limits. Compile coverage plus scheduled scan command validation and channel packing tests are the key signals.
