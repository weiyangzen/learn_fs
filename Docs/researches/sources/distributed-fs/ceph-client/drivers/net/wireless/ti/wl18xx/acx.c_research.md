# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/acx.c

## Purpose
Implements WiLink 8-specific ACX firmware configuration helpers. Each helper allocates a packed wl18xx ACX payload, fills it from wlcore or wl18xx configuration, sends it through `wl1271_cmd_configure()`, logs failures, and frees the payload.

## Important APIs, types, and functions
- `wl18xx_acx_host_if_cfg_bitmap()` configures host interface behavior, SDIO block size, extra TX memory blocks, and length-field width.
- `wl18xx_acx_set_checksum_state()` enables firmware checksum offload.
- `wl18xx_acx_clear_statistics()` clears firmware statistics used by debugfs.
- `wl18xx_acx_peer_ht_operation_mode()` updates a peer link between 20 and 40 MHz operation.
- `wl18xx_acx_set_peer_cap()` sets HT capabilities plus supported rates for a link.
- `wl18xx_acx_interrupt_notify_config()` and `wl18xx_acx_rx_ba_filter()` tune notification behavior during suspend.
- `wl18xx_acx_ap_sleep()`, `wl18xx_acx_dynamic_fw_traces()`, and `wl18xx_acx_time_sync_cfg()` configure AP sleep, dynamic firmware trace mask, and time sync parameters.

## Control flow
The functions all follow a linear pattern: allocate with `kzalloc_obj()`, fill command fields, convert multi-byte fields with `cpu_to_le*()` where required, call `wl1271_cmd_configure()` with the appropriate ACX id, handle negative status, then free. They are invoked from wl18xx setup/init paths, debugfs writes, suspend/resume hooks, AP sleep handling, and peer capability/rate-control updates via `wl18xx_ops`.

## State and persistence behavior
No persistent storage is written. Firmware state is changed by successful ACX commands. Host-side inputs come from `wl->dynamic_fw_traces`, `wl->conf.sg`, `wl->zone_master_mac_addr`, and `priv->conf.ap_sleep`. The command payloads are transient heap allocations.

## Dependencies and integration points
Depends on common wlcore command/debug headers, wlcore ACX base definitions, and wl18xx ACX structures. Integrated through `wl18xx/main.c` operations such as `interrupt_notify`, `rx_ba_filter`, `ap_sleep`, `set_peer_cap`, `hw_init`, and debugfs callbacks.

## Risks and test signals
Risks are wrong ACX ids, missing endian conversions, toggling checksum offload without matching TX/RX descriptor handling, and AP sleep/time sync settings that do not match firmware expectations. Test signals include successful boot `hw_init`, debugfs dynamic trace updates while device is on, suspend/resume notification filtering, HT bandwidth changes, and AP sleep configuration on AP roles.
