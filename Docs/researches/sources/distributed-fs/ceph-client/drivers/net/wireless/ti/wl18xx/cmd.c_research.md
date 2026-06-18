# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/cmd.c

## Purpose
Implements WiLink 8-specific firmware commands that are not generic ACX configuration: channel switch, Smart Config, DFS CAC, radar debug, and DFS master restart.

## Important APIs, types, and functions
- `wl18xx_cmd_channel_switch()` converts mac80211 channel-switch data into `CMD_CHANNEL_SWITCH`, including band, switch time, TX stop flag, channel type, and supported-rate mask.
- `wl18xx_cmd_smart_config_start()`, `wl18xx_cmd_smart_config_stop()`, and `wl18xx_cmd_smart_config_set_group_key()` control vendor Smart Config behavior.
- `wl18xx_cmd_set_cac()` starts/stops DFS channel availability check with role/channel/bandwidth.
- `wl18xx_cmd_radar_detection_debug()` triggers firmware radar detection debug for a supplied channel.
- `wl18xx_cmd_dfs_master_restart()` restarts DFS master operation for an AP role.

## Control flow
Each command allocates the matching packed command structure, fills role/channel/rate/key fields, sends the correct `CMD_*` via `wl1271_cmd_send()`, handles negative errors, and frees. Channel switch selects 2.4/5 GHz band explicitly, derives rates from common wlcore hardware callbacks, and strips CCK rates for P2P. Smart Config key setting validates exact key length before allocation.

## State and persistence behavior
No host-side persistent state is changed, except firmware command effects. Commands depend on current `wlvif` state such as `role_id`, `channel`, `band`, `channel_type`, `bss_type`, and P2P flag.

## Dependencies and integration points
Depends on wlcore command, debug, and hardware-ops helpers. `wl18xx/main.c` exposes these through `wlcore_ops` for channel switch, Smart Config, CAC, and DFS master restart; `debugfs.c` calls radar debug.

## Risks and test signals
Risks include invalid band mapping, rate masks inconsistent with peer/AP capabilities, accepting wrong Smart Config key lengths, and DFS commands on invalid roles. Test with CSA in STA/AP/P2P modes, P2P channel switches without CCK, Smart Config vendor commands/events, DFS CAC start/stop on 5 GHz, and certification radar debug hooks.
