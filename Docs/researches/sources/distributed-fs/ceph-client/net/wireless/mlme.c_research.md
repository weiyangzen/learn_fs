# sources/distributed-fs/ceph-client/net/wireless/mlme.c

## Purpose
This file implements cfg80211 MLME service access helpers: association response processing, auth/deauth/disassoc event handling, userspace SME auth/assoc requests, management frame registration and TX/RX dispatch, Michael MIC failure reporting, DFS channel timers, radar/CAC events, background CAC, and MLO reconfiguration completion.

## Important APIs, types, and functions
Event ingress includes `cfg80211_rx_assoc_resp()`, `cfg80211_rx_mlme_mgmt()`, `cfg80211_auth_timeout()`, `cfg80211_assoc_failure()`, `cfg80211_tx_mlme_mgmt()`, and `cfg80211_michael_mic_failure()`. Userspace SME requests include `cfg80211_mlme_auth()`, `cfg80211_mlme_assoc()`, `cfg80211_mlme_deauth()`, `cfg80211_mlme_disassoc()`, and `cfg80211_mlme_down()`.

Management frame state uses `struct cfg80211_mgmt_registration`, `cfg80211_mlme_register_mgmt()`, `cfg80211_mlme_unregister_socket()`, `cfg80211_mlme_purge_registrations()`, `cfg80211_mlme_mgmt_tx()`, and `cfg80211_rx_mgmt_ext()`. DFS/radar functions include `cfg80211_sched_dfs_chan_update()`, `cfg80211_dfs_channels_update_work()`, `__cfg80211_radar_event()`, `cfg80211_cac_event()`, background CAC helpers, and stop functions. MLO helpers include `cfg80211_mlme_check_mlo()`, `cfg80211_assoc_ml_reconf()`, and `cfg80211_mlo_reconf_add_done()`.

## Control flow
Association responses are converted into `cfg80211_connect_resp_params`, including per-link BSS/address/status data for MLO, sent to userspace, then consumed by the SME connection-result path unless SME retry logic suppresses a reassoc rejection. Auth/deauth/disassoc frames are classified by frame control and routed to nl80211 notifications plus SME state updates. Auth and association requests validate BSS presence, MLO link compatibility, local address conflicts, shared-key requirements, connected state, and capability masks before calling driver ops.

Management registration validates frame type, supported stypes, station auth match specificity, and duplicate matches under `mgmt_registrations_lock`, then updates driver registration bitmasks. RX matching compares frame type and match bytes after the 802.11 header and sends matching frames to the owning netlink port. TX validates frame class, supported TX stypes, interface-mode addressing rules, random transmitter-address feature bits, and driver support before `rdev_mgmt_tx()`.

DFS work scans all channels for NOP expiry or pre-CAC expiry, updates states to usable, notifies nl80211, propagates regulatory state, and reschedules for the next timeout. Radar detection marks affected channels unavailable, aborts offchannel CAC if needed, schedules DFS updates, notifies userspace, and propagates state. CAC start/finish/abort updates per-link CAC flags and channel CAC timestamps. Background CAC owns one offchannel chain per rdev and schedules delayed completion.

## State and persistence
State is in memory: wdev connection flags and current BSS refs, management registration lists, `crit_proto_nlportid`, `unexpected_nlportid`, per-channel DFS/CAC state, per-link CAC fields, background radar owner/chandef, delayed work, and MLO valid link masks. No durable persistence exists.

## Dependencies and integration points
The file integrates with nl80211 notifications, SME helpers, scan/BSS refcounting, driver ops, regulatory propagation, channel helpers, WEXT notifications, cfg80211 workqueue, wiphy locking, RTNL in DFS work, and MLO IEEE 802.11 element parsing.

## Risks
BSS reference ownership across assoc success/failure and MLO link addition is high risk. Management registration matching can leak or stale-program driver filters if socket unregister and purge paths miss updates. DFS timers and background CAC must avoid legal-state regressions and races with interface shutdown. Address validation for management TX must remain aligned with new MLO addressing rules.

## Test signals
Cover association success/reject/failure, MLO link mismatch extack paths, auth/deauth/disassoc local and AP-originated flows, management registration duplicates and socket cleanup, management TX per iftype, DFS NOP/pre-CAC expiry, radar during background CAC, CAC start/finish/abort, interface shutdown during CAC, and BSS refcount balance under KASAN/lockdep.
