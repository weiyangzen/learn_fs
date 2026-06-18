# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/cmd.c

## Purpose
`cmd.c` is the wlcore firmware command execution layer. It turns mac80211 and wlcore state into packed firmware command mailboxes, manages role and host-link allocation, programs templates and keys, starts and stops STA/AP/IBSS/device roles, controls remain-on-channel, configures firmware logging, and sends regulatory/DFS and generic feature commands.

## Important APIs and functions
The core API is `wl1271_cmd_send()`, backed by `__wlcore_cmd_send()` and `wlcore_cmd_send_failsafe()`. It writes a DMA-safe command buffer to `wl->cmd_box_addr`, triggers the chip-specific command doorbell through `wl->ops->trigger_cmd()`, polls `REG_INTERRUPT_NO_CLEAR` for `WL1271_ACX_INTR_CMD_COMPLETE`, reads command status back from the mailbox, ACKs the command interrupt, and queues recovery on transport or unexpected firmware status failures.

Role lifecycle functions include `wl12xx_cmd_role_enable()`, `wl12xx_cmd_role_disable()`, `wl12xx_cmd_role_start_sta()`, `wl12xx_cmd_role_stop_sta()`, `wl12xx_cmd_role_start_ap()`, `wl12xx_cmd_role_stop_ap()`, `wl12xx_cmd_role_start_ibss()`, `wl12xx_start_dev()`, and `wl12xx_stop_dev()`. Link allocation is owned by `wl12xx_allocate_link()` and `wl12xx_free_link()`, which update `wl->links_map`, per-vif link maps, session IDs, TX accounting, AP broadcast/global links, and recovery sequence padding.

Configuration helpers include `wl1271_cmd_interrogate()`, `wlcore_cmd_configure_failsafe()`, `wl1271_cmd_configure()`, `wl1271_cmd_data_path()`, `wl1271_cmd_ps_mode()`, `wlcore_cmd_regdomain_config_locked()`, `wl12xx_cmd_config_fwlog()`, `wl12xx_cmd_stop_fwlog()`, `wlcore_cmd_generic_cfg()`, and `wlcore_cmd_wait_for_event_or_timeout()`. Template/key helpers include `wl1271_cmd_template_set()`, null/QoS/PS-poll/probe/ARP template builders, `wl12xx_cmd_set_default_wep_key()`, `wl1271_cmd_set_sta_key()`, and `wl1271_cmd_set_ap_key()`.

## Control flow
Command control flow is synchronous: allocate and fill a packed command, call `wl1271_cmd_send()`, and unwind state if command submission fails. Role start paths allocate HLIDs before sending `CMD_ROLE_START`; error labels free partially allocated links. AP start allocates both global and broadcast HLIDs and preserves broadcast sequence accounting across recovery/resume. Peer removal sends `CMD_REMOVE_PEER` and then waits for `WLCORE_EVENT_PEER_REMOVE_COMPLETE`, but tolerates timeout because firmware may omit the event. Regulatory configuration builds a channel bitmap from pending channels plus current wiphy channel flags, sends `CMD_DFS_CHANNEL_CONFIG`, waits for `WLCORE_EVENT_DFS_CONFIG_COMPLETE`, then persists the last-applied bitmap.

## State and persistence behavior
The file mutates driver runtime state: `roles_map`, `links_map`, `roc_map`, `session_ids`, `active_link_count`, per-link TX counters, per-vif role IDs, per-vif HLIDs, `reg_ch_conf_pending`, `reg_ch_conf_last`, and AP/STA recovery counters. It also consumes persistent configuration from `wl->conf` for TX retries, AP aging, firmware logger settings, and power-save timing. Most allocations are transient command buffers, but link/session state persists until stop, recovery, or role teardown.

## Dependencies and integration points
`cmd.c` depends on IO wrappers in `io.h`, ACX configuration, `event.h` wait events, `tx.h` queue/watchdog helpers, mac80211 frame constructors, cfg80211 band/channel definitions, and chip-specific callbacks in `wl->ops`/`hw_ops.h`. It is called by wlcore main, scan, AP/STA setup, key management, regulatory updates, and debugfs firmware logger controls.

## Risks
The command ABI requires exact packed layouts and little-endian fields; buffer length, alignment, or status handling mistakes can lock the firmware or corrupt command interpretation. Link allocation and free paths are shared with TX under `wl_lock`; missing locking or bad unwind can leave stale HLID maps. Several paths accept firmware timeouts as recoverable, so regressions may appear as delayed recovery rather than immediate failure. Template builders must account for encryption padding and mac80211 skb ownership. Regulatory bitmap mapping is hand-coded and sensitive to band/channel tables.

## Test signals
Useful signals include successful interface bring-up in STA/AP/IBSS/P2P roles, association and disassociation without leaked HLIDs, scan and scheduled-scan probe templates, AP peer add/remove, encryption for WEP/TKIP/AES/GEM, remain-on-channel completion, DFS/regdomain update completion, firmware logger reconfiguration, command timeout recovery, and debug traces under `DEBUG_CMD`, `DEBUG_SCAN`, `DEBUG_CRYPT`, and `DEBUG_ACX`.
