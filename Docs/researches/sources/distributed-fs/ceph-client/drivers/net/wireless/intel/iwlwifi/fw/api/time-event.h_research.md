# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/time-event.h

## Purpose
Defines firmware scheduling ABI for time events, remain-on-channel operations, Hotspot/AUX ROC, P2P activities, and session protection. These commands reserve channel/time windows needed for association, P2P discovery/negotiation, quiet periods, channel switch, and other MAC activities.

## Important APIs, Types, And Functions
Key enums include `iwl_time_event_type`, v1/v2 fragmentation and repetition constants, `iwl_time_event_policy`, `iwl_mvm_hot_spot`, `iwl_roc_activity`, and `iwl_session_prot_conf_id`. Main structures are `iwl_time_event_cmd`, `iwl_time_event_resp`, `iwl_time_event_notif`, `iwl_hs20_roc_req`, `iwl_hs20_roc_res`, `iwl_roc_req_v5`, `iwl_roc_req`, `iwl_roc_notif`, `iwl_session_prot_cmd`, and `iwl_session_prot_notif`.

## Control Flow
The driver adds/removes time events by MAC/link ID and action. Firmware assigns unique IDs, schedules events according to apply time, max delay, dependencies, duration, repetition, fragmentation, and policy bits, then sends start/end notifications. ROC commands request a channel and duration for P2P/Hotspot activities. Session protection requests reserve association or P2P windows and always produce start/end notifications, even on scheduling failure.

## State And Persistence
Scheduled events persist in firmware until they expire, repeat-endlessly, are removed, or are superseded by session protection rules. Persistent identifiers include MAC/link IDs, unique event IDs, session IDs, activity IDs, and configuration IDs. The header itself stores no state but defines the fields used by driver-side tracking.

## Dependencies And Integration Points
Includes PHY channel context definitions and depends on common MAC context action/id concepts. Integrates with association protection, P2P listen/action scans, remain-on-channel mac80211 operations, CSA/NoA behavior, firmware scheduler arbitration, and MLO link-specific protection in newer notification versions.

## Risks
Time units mix GP2 timestamps, microseconds, and TUs across structures. Misinterpreting policy bits can create absent/present windows at the wrong time or suppress critical notifications. Unique IDs from responses must be retained for removal and matched against notifications. Only one concurrent session protection per vif is supported, so adding a new one replaces the old one.

## Test Signals
Validate association under scan/P2P load, ROC start/end notifications, ROC cancellation, P2P discovery and negotiation, session protection replacement, endless/repeated events, TSF/dependency scheduling, and firmware failure notifications. Race tests around remove vs. start/end notification are important.
