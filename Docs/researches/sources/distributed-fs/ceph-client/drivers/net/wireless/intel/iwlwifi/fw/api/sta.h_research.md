# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/sta.h

## Purpose
Defines station-table and station-key firmware command ABI for iwlwifi MVM. It describes station flags, add/modify/remove station commands, aggregation setup, U-APSD and power-save state, key programming, management multicast keys, WEP keys, and EOSP notifications.

## Important APIs, Types, And Functions
Key enums include `iwl_sta_flags`, `iwl_sta_key_flag`, `iwl_sta_modify_flag`, `iwl_sta_mode`, `iwl_sta_sleep_flag`, `iwl_sta_type`, and `iwl_mvm_add_sta_rsp_status`. Main structures are `iwl_mvm_add_sta_cmd_v7`, `iwl_mvm_add_sta_cmd`, `iwl_mvm_add_sta_key_common`, `iwl_mvm_add_sta_key_cmd_v1`, `iwl_mvm_add_sta_key_cmd`, `iwl_mvm_rm_sta_cmd`, `iwl_mvm_mgmt_mcast_key_cmd`, `iwl_mvm_wep_key_cmd`, and `iwl_mvm_eosp_notification`.

## Control Flow
Driver station lifecycle maps to firmware table operations: add a station with MAC/context/type/capability flags, modify selected fields through `modify_mask`, configure BA sessions and queue ownership, install keys, and remove the station on teardown. Power-save changes use sleep flags, U-APSD ACs, and sleep TX counts. Security commands program per-station, multicast management, and WEP keys, then TX/RX paths rely on key offsets and flags.

## State And Persistence
The actual persistent state lives in firmware station/key tables. This header defines the packed records that mutate that state: station ID, MAC context, association/auth flags, channel width/MIMO capabilities, aggregation parameters, queue masks, RX BA window, key material, PN/RSC counters, and management key IDs. Firmware may update some capability flags after action frames.

## Dependencies And Integration Points
Integrates with mac80211 station/key callbacks, iwlwifi MVM station tracking, TX queue setup, RX reorder setup, security offload, TDLS station types, multicast/AP beacon behavior, and U-APSD service period handling. It uses shared context IDs, station counts, endian annotations, and crypto constants.

## Risks
The station table is central to TX, RX, security, and aggregation, so ID/color mismatches or stale station IDs can misdirect traffic. `modify_mask` must match changed fields or firmware may ignore updates. Key flag aliases share bits for WEP/non-WEP meanings, and version differences in TKIP/RSC layout can break replay protection. Queue masks are obsolete for newer TX APIs but still present in older command versions.

## Test Signals
Test add/modify/remove for AP, client, multicast, TDLS, and auxiliary stations; key install/remove for WEP, CCMP, GCMP, TKIP, CMAC/GMAC; RX BA setup/removal; U-APSD/EOSP; powersave transitions; and station-table exhaustion. Firmware responses should surface overload, BA failure, or modify-nonexistent errors.
