# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/roc.c

Purpose: implements remain-on-channel operations for P2P device, station hotspot, and management TX contexts, coordinating aux station setup, EMLSR blocking, firmware ROC commands, cancellation, and mac80211 ROC notifications.

Important APIs/functions: `iwl_mld_start_roc()`, `iwl_mld_cancel_roc()`, and `iwl_mld_handle_roc_notif()`. Static helpers find the VIF for a firmware ROC activity, block/unblock EMLSR across active interfaces, and destroy ROC state by resetting activity, synchronizing TX, flushing aux-station queues, and removing the aux station.

Control flow: start validates VIF type, maps mac80211 ROC type to firmware activity, rejects duplicate activity, blocks EMLSR, adds aux station, builds `ROC_CMD` add with 20 MHz channel, max delay, duration, station id, and node address, and records `mld_vif->roc_activity`. Cancel sends remove if active, cancels queued async ROC notification for the activity to handle races, then destroys local state. Firmware notification finds the VIF by activity, ignores stale canceled notifications, reports ready on successful start, otherwise cancels/removes and reports expiration.

State and persistence: state is `mld_vif->roc_activity` plus aux station state and queued async notifications. `synchronize_net()` ensures TX observes reset before queue flush/removal. No disk persistence.

Dependencies and integration: depends on mac80211 ROC APIs, firmware `ROC_CMD`/`ROC_NOTIF`, local aux-station helpers, notification cancellation, station TX flushing, MLO EMLSR blocking, and channel band conversion.

Risks and test signals: start error after aux-station add but failed command returns without local aux cleanup, which is a notable leak/race risk to audit. Duplicate activity detection assumes firmware supports one ROC per type. Tests should cover unsupported VIF types, P2P type mapping, duplicate activity, firmware start failure notification, cancel/notification race, and EMLSR blocker cleanup.
