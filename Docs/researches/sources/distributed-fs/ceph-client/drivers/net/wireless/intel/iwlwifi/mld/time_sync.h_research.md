# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/time_sync.h

Purpose: Defines time-sync runtime state and declares MLD time-sync configuration, frame interception, deinit, and notification handlers.

Important APIs and types: `struct iwl_mld_time_sync_data` holds RCU head, peer address, active protocols, and pending frame queue. APIs configure firmware, configure/replace local state, deinitialize, intercept frames, and handle measurement/confirm notifications.

Control flow and integration: Used by TX/RX paths to queue timing/FTM frames and by firmware notification dispatch to attach timestamps and complete mac80211 delivery.

State and persistence: Time-sync state is RCU-protected and runtime-only. Queued SKBs are owned by this subsystem until notification delivery, drop, or deinit.

Dependencies: Requires Ethernet address size, SKB queue types, RCU, MLD core, and firmware RX packet types via includers.

Risks: Ownership transfer of SKBs is implicit in `iwl_mld_time_sync_frame()` returning true; callers must not free queued frames.

Test signals: Compile coverage plus behavioral tests for accepted/rejected frame ownership and notification completion.
