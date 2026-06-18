# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/scan.h

Purpose: Declares MLD scan entry points, scan state enums, scan runtime state, and channel survey structures shared by scan implementation, notification dispatch, and mac80211 callbacks.

Important APIs and types: Exports start/stop APIs for regular, scheduled, and internal MLO scans; notification handlers for scan iteration, match, start, completion, and channel survey; `iwl_mld_mac80211_get_survey()`; `iwl_mld_alloc_scan_cmd()`; and `iwl_mld_report_scan_aborted()`. Defines `enum iwl_mld_scan_status`, scheduled-scan pass-all states, `enum iwl_mld_traffic_load`, `struct iwl_mld_scan`, `struct iwl_mld_survey_channel`, and `struct iwl_mld_survey`.

Control flow and integration: The header binds mac80211 operation callbacks, firmware notification dispatch, restart handling, and survey access to `scan.c`. The inline `iwl_mld_scan_max_template_size()` encodes firmware template capacity after driver-added management header and IEs.

State and persistence: `struct iwl_mld_scan` separates restart-zeroed state from command allocation and timing fields that survive firmware restart. Survey structs mirror a compact subset of mac80211 `survey_info`.

Dependencies: Requires firmware scan constants such as `SCAN_OFFLOAD_PROBE_REQ_SIZE`, Linux band counts, MLD core types, and mac80211/cfg80211 types supplied by includers.

Risks: The struct grouping controls restart cleanup semantics; adding fields in the wrong group can preserve stale scan state or lose needed command allocation data. Scan status values are bit masks and must stay compatible with UID status storage.

Test signals: Compile coverage of scan callbacks, restart cleanup, survey callback registration, and command-size assertions.
