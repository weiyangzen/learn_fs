# sources/distributed-fs/ceph-client/drivers/net/ethernet/toshiba/ps3_gelic_wireless.h

Purpose: Defines the Gelic wireless/Eurus firmware ABI and the wireless private state consumed by `ps3_gelic_wireless.c`. It covers LV1 WLAN event IDs, Eurus command IDs and packed command payloads, scan result formats, wireless configuration state enums, scan/association state, and driver entry-point prototypes.

Important APIs and types: Event and command enums include `GELIC_LV1_WL_EVENT_*` and `GELIC_EURUS_CMD_*`. Packed firmware payloads include `struct gelic_eurus_common_cfg`, `gelic_eurus_wep_cfg`, `gelic_eurus_wpa_cfg`, `gelic_eurus_scan_info`, and `gelic_eurus_rssi_info`; all command fields are documented as big-endian. Driver-side state is held in `struct gelic_wl_info`, including scan lists, workqueues, completions, config bits, ciphers, keys, PSK, ESSID/BSSID, active BSSID, and Wireless Extensions stats. `struct gelic_eurus_cmd` carries one synchronous command through the workqueue. Inline helpers convert between `gelic_wl_info` and the enclosing `gelic_port`.

Control flow and integration: The header is included by both the shared Gelic net driver and the wireless implementation. `gelic_wl_driver_probe()` and `gelic_wl_driver_remove()` are called from PS3 Gelic probe/remove. `gelic_wl_interrupt()` is called from the shared IRQ handler when WLAN event or command-complete bits are present. The private ioctl constants provide pass-through PSK operations, though the C file mainly uses standard encodeext PMK handling.

State and persistence: The header defines runtime-only state. Scan cache entries own duplicated firmware scan blobs and are rotated between active/free lists. Config state flags track whether userspace provided ESSID, BSSID, PSK, WPA level, and channel info. Association state records disconnected/associating/associated and is coordinated with completions.

Dependencies and integration points: Depends on Linux Wireless Extensions and `iw_handler`, Linux list/completion/workqueue/spinlock primitives through users, and `ps3_gelic_net.h` for `struct gelic_port` layout. Firmware command structures must match the LV1/Eurus ABI exactly.

Risks: Packed big-endian firmware structures must be accessed with endian helpers. `gelic_eurus_scan_info` has a flexible `elements[]` tail, so consumers must validate `size` before parsing IE data. `gelic_wl_info` is appended after `struct gelic_port::priv`, so struct size/alignment changes affect netdev private layout. PSK/key buffers hold sensitive material and debug logging must not expose them.

Test signals: Compile wireless-enabled builds; validate structure sizes/packing against firmware expectations; scan result parsing with and without `elements[]`; state transitions for scan and association enums; private layout access through `wl_port()` and `port_wl()`; interrupt entry-point linkage from `ps3_gelic_net.c`.
