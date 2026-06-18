# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/scan.h

## Purpose
Defines Intel iwlwifi firmware scan command, response, and notification ABI. It covers directed SSID scans, LMAC and UMAC scan requests, scheduled/offloaded scan profiles, channel optimization, probe request segmentation, 6 GHz/UHB discovery flags, adaptive dwell controls, scan abort/start/complete notifications, match reporting, and channel survey statistics.

## Important APIs, Types, And Functions
Important structures include `iwl_ssid_ie`, `iwl_scan_offload_profile`, `iwl_scan_offload_profile_cfg`, `iwl_scan_req_lmac`, `iwl_lmac_scan_complete_notif`, `iwl_scan_config_v1/v2`, `iwl_scan_config`, `iwl_scan_channel_cfg_umac`, `iwl_scan_req_umac`, `iwl_scan_req_umac_v12/v17/v18`, `iwl_umac_scan_abort`, `iwl_umac_scan_complete`, `iwl_scan_offload_match_info`, `iwl_umac_scan_iter_complete_notif`, and `iwl_umac_scan_channel_survey_notif`. Enums define scan clients, auth algorithms, profile network/band matching, priority, channel flags, UMAC general flags, abort status, and EBS status.

## Control Flow
The driver first configures scan defaults such as chains, dwell times, MAC address, rates, and supported channels. A scan request then combines general parameters, channel lists, periodic schedules, and probe parameters. Firmware performs channel iteration, may send start and per-iteration/per-channel notifications, emits matched-profile notifications for scheduled scans, and finishes with complete/abort status. UMAC APIs evolved from a flexible-tail command to versioned aggregate parameter structures in v12+.

## State And Persistence
No C state is stored here, but command payloads persist firmware scan state: active clients, blocklists, profiles, schedules, probe frame buffers, short SSIDs, BSSID filters, channel lists, adaptive dwell overrides, and UIDs that identify scans across abort/start/complete notifications. Flexible arrays and fixed maximum channel/profile counts determine command allocation sizes in callers.

## Dependencies And Integration Points
Integrates with mac80211 scan and scheduled-scan APIs, iwlwifi MVM scan builders, firmware command groups, regulatory channel lists, 6 GHz colocated AP discovery, station/probe TX setup, and survey reporting. It relies on Ethernet/SSID constants, bit macros, and TX/rate definitions from neighboring API headers.

## Risks
Versioned structures have subtly different sizes, field ordering, channel limits, and flag meanings. Mixing general flag version 1 and version 2 can change passive scan, preemptive, adaptive dwell, OCE, or 6 GHz behavior. Probe request segment offsets and flexible data tails must match constructed buffers. Bad channel counts or adaptive-dwell bitmaps can overrun firmware expectations or skip regulatory-required passive behavior.

## Test Signals
Validate active/passive scans on 2.4, 5, and 6 GHz; scheduled scan profile matching; abort races; scan preemption; adaptive dwell; fragmented scan; per-channel survey notifications; short-SSID/BSSID filters; and UHB/PSC discovery behavior. Firmware logs, cfg80211 scan completion, and mac80211 survey data are the primary runtime indicators.
