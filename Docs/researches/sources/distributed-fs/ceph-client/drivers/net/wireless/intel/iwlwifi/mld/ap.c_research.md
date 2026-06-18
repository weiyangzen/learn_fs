# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/ap.c

## Purpose

`ap.c` implements AP/IBSS support helpers for the MLD opmode. It builds firmware beacon templates, computes beacon rate flags, locates TIM/CSA/TWT offsets, handles early AP keys that arrive before broadcast/multicast stations exist, and starts/stops AP or IBSS firmware state.

## Important APIs, Types, and Functions

Public entry points are `iwl_mld_set_tim_idx()`, `iwl_mld_get_rate_flags()`, `iwl_mld_send_beacon_template_cmd()`, `iwl_mld_update_beacon_template()`, `iwl_mld_store_ap_early_key()`, `iwl_mld_free_ap_early_key()`, `iwl_mld_start_ap_ibss()`, and `iwl_mld_stop_ap_ibss()`. The main local helper is `iwl_mld_fill_beacon_template_cmd()`.

## Control Flow

Beacon update obtains a mac80211 template, fills link ID, channel-derived FILS and short-SSID data, byte count, beacon rate flags, TIM index for AP mode, BTWT/CSA/ECSA offsets, then sends `BEACON_TEMPLATE_CMD` with the command and beacon payload. AP/IBSS start sends AP TX power constraints for AP mode, updates the beacon template, modifies the link context, adds multicast and broadcast stations, flushes early keys to firmware, updates P2P device state and low-latency flags, and refreshes PHY chandef. Stop reverses active flags and removes broadcast/multicast stations.

## State and Persistence Behavior

State changes include `mld_vif->ap_ibss_active`, low-latency causes, P2P device firmware context, per-link `ap_early_keys[]`, multicast/broadcast station firmware state, and beacon template firmware state. Debugfs beacon injection can temporarily block template updates through `beacon_inject_active`.

## Dependencies and Integration Points

The file depends on mac80211 beacon APIs, cfg80211 channel helpers, firmware beacon command definitions, MLD link/vif/sta/key/power/phy helpers, CRC32 for short SSID, and AP multicast/broadcast station management.

## Risks and Edge Cases

Failure rollback in `iwl_mld_start_ap_ibss()` must remove only resources already added. Early key storage has fixed slots and returns `-ENOSPC` if full. TIM parsing assumes valid beacon element lengths from mac80211. Non-transmitting AP support is gated by a constant currently set false.

## Test Signals

Test AP and IBSS start/stop, beacon updates with/without configured beacon TX rate, 6 GHz FILS/PSC handling, CSA/ECSA/TWT offset reporting, early key storage/removal/send, P2P GO interactions, debugfs beacon injection interaction, and rollback after failures in link modify, multicast, broadcast, or key setup.
