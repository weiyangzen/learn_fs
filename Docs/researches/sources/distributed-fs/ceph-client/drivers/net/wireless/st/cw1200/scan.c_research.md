# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/scan.c

Purpose: Implements mac80211 hardware scan and direct-probe workarounds for CW1200 firmware.

Important APIs and functions: Provides `cw1200_hw_scan`, `cw1200_scan_work`, `cw1200_scan_timeout`, `cw1200_clear_recent_scan_work`, `cw1200_scan_complete_cb`, `cw1200_scan_failed_cb`, and `cw1200_probe_work`. Internal helpers include `cw1200_scan_start`, `cw1200_scan_restart_delayed`, and `cw1200_scan_complete`.

Control flow: `cw1200_hw_scan` builds a probe request template, takes `scan.lock`, sets scan request state, locks TX, and queues scan work. `cw1200_scan_work` chunks channels by band/flags/power, may force background scanning while joined, adjusts output power, starts firmware scans, and completes by restoring PM/listening/filter state and notifying mac80211. Timeout and firmware callbacks race through the delayed timeout work to serialize completion. `cw1200_probe_work` converts a pending raw probe request into a one-channel scan, edits SSID handling, removes the original TX queue entry, and fakes ACK on success.

State and persistence: `struct cw1200_scan` tracks request pointers, channel iterators, SSIDs, output power, status, atomic progress, direct-probe flag, and work items. `recent_scan` keeps the device awake briefly after scans.

Dependencies and integration: Depends on WSM scan/template/probe-responder commands, STA listening/filtering/unjoin logic, PM stay-awake, queues, and mac80211 scan completion APIs.

Risks: Scan state is protected by both a semaphore and `conf_mutex`; wrong ordering can deadlock. AP mode scans are rejected because firmware MiniAP mode can be corrupted. Direct probe mutates skb contents temporarily and must restore offsets. Delayed unjoin/link-loss handling depends on scan completion paths.

Test signals: Active/passive scans, joined background scans, AP scan rejection, scan timeout, firmware failure callback, P2P listening restart, delayed unjoin during scan, and direct probe request conversion.
