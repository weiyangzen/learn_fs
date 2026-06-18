# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/acx.c

Purpose: Implements wl1251 ACX information-element configuration and interrogation helpers. These functions allocate packed ACX payloads, fill firmware parameters, send `CMD_CONFIGURE` or `CMD_INTERROGATE`, and update selected driver state.

Important APIs, types, and functions: Configuration helpers cover frame rates, station ID, default key, wake/sleep authorization, TX power, feature flags, data path params, RX config, slot time, multicast table, RTS threshold, beacon filtering, connection monitoring, SoftGemini BT coexistence, CCA, DTIM/broadcast behavior, AID, event mask, low RSSI, preamble/CTS protection, memory config, TBTT/DTIM, BET, ARP filter, AC/TID QoS. Interrogation helpers include firmware version, memory map, statistics, and TSF.

Control flow: Most functions follow a strict pattern: allocate zeroed ACX struct, fill fields and defaults from arguments or constants, call `wl1251_cmd_configure()` with an ACX ID, log failures, free memory, and return. Readback functions call `wl1251_cmd_interrogate()` and copy response fields. `wl1251_acx_data_path_params()` first configures ring sizes and thresholds, then interrogates response parameters and validates command status.

State and persistence: Host state updates are limited, e.g. `wl->default_key` and returned buffers such as firmware version/statistics/TSF. Firmware runtime state is extensively changed but not persisted by the host.

Dependencies and integration points: Depends on `cmd.c` mailbox helpers, ACX structs/IDs from `acx.h`, rate/filter constants, power-save code, and wl1251 core state. It is used by boot/init/mac80211 operations to establish firmware behavior.

Risks: Many helpers trust caller-provided sizes/counts; multicast copy can overflow if `mc_list_len` exceeds firmware table capacity. Some FIXME comments note unset PD threshold and ambiguous data-path response ID. All allocations are per-command, so memory pressure can fail configuration. Firmware defaults embedded as constants may not suit all board/NVS variants.

Test signals: Validate boot/init sequence reaches configured data path, RX filters match interface modes, event masks generate expected events, debugfs statistics reads succeed, multicast table bounds are respected, and power-save/BT coexistence parameters do not regress association stability.
