# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/sta.c

Purpose: Implements the WFx mac80211 station/AP/IBSS/interface/configuration callbacks and firmware state coordination for BSS, PM, filters, beaconing, TIM, link IDs, channel contexts, WoWLAN, and thermal suspend/resume events.

Important APIs and functions: Public callbacks include start/stop, add/remove interface, configure filter, conf_tx, set RTS/default key, BSS info changed, sta_add/remove, start/stop AP, join/leave IBSS, set_tim, ampdu_action, channel context assign/unassign, suspend/resume/set_wakeup, and update PM. Firmware callback helpers include cooling timeout, hot-device suspend, multicast suspend/resume, RSSI report, and reset.

Control flow and integration: Interface add initializes per-vif work/completions/queues/policies, assigns a vif slot, sets MAC address, and adjusts block-ack policy depending on combo mode. BSS changes trigger join/reset/finalize, beacon wake/filter changes, ARP filters, template uploads, beacon enable, keepalive, ERP/slot/RSSI/TX power/PS updates. AP start uploads beacon/probe templates, starts firmware BSS, and configures MFP from RSN IE. Station add maps TDLS/AP peers to firmware link IDs when needed. Reset locks/flushed TX, sends HIF reset, resets policies, restores BA policy, clears join state, cancels beacon loss, and updates PM on all vifs.

State and persistence: Maintains `wdev->vif[]`, per-vif `id`, `channel`, `link_id_map`, `after_dtim_tx_allowed`, `join_in_progress`, PM completion, beacon loss/TIM/scan/ROC work, U-APSD mask, queues, and TX policies. Firmware-persistent state includes MAC address, BSS/join/start state, beacon/probe templates, filters, PM mode, BA policy, MFP, ARP filters, and link map.

Dependencies: Depends on mac80211/cfg80211 APIs, HIF request and MIB helpers, queue/TX flush, scan locks, key handling, debug/common state, and API-version helpers.

Risks and test signals: Risks include lock ordering with `conf_mutex`/`scan_lock`/TX lock, reset during scan/join, link ID exhaustion/leaks, combo-mode BA disablement, PM timeout waits, beacon filter hiding needed beacons, TIM update with malformed beacon, MFP RSN IE parsing bounds, WoWLAN limited validation, and thermal suspend freezing TX. Tests should cover STA join/assoc/disassoc, IBSS, AP start/stop/templates/TIM, add/remove station including TDLS, two-vif combo mode, PS/U-APSD changes, RSSI CQM, beacon loss/regain, ARP filter limits, channel context assign/unassign, suspend/resume wakeup, and interface removal with clean queues.

Test signals: Source read size: 841 lines, 23585 bytes.
