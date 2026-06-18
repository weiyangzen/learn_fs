# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/uap_cmd.c

## Purpose
`uap_cmd.c` builds firmware commands and TLVs for mwifiex AP/uAP operation. It translates cfg80211 AP settings and station parameters into firmware-understandable security, rate, WMM, HT/VHT, channel, beacon, threshold, custom IE, BSS start/stop, deauth, and add-station commands.

## Important APIs, Types, and Functions
Public helpers include `mwifiex_set_secure_params`, `mwifiex_set_ht_params`, `mwifiex_set_vht_params`, `mwifiex_set_tpc_params`, `mwifiex_set_vht_width`, `mwifiex_set_uap_rates`, `mwifiex_set_sys_config_invalid_data`, `mwifiex_set_wmm_params`, `mwifiex_config_uap_11d`, `mwifiex_uap_prepare_cmd`, `mwifiex_uap_set_channel`, and `mwifiex_config_start_uap`. Internal command builders include `mwifiex_uap_bss_wpa`, `mwifiex_uap_bss_wep`, `mwifiex_uap_bss_param_prepare`, `mwifiex_uap_custom_ie_prepare`, `mwifiex_cmd_uap_sys_config`, `mwifiex_cmd_uap_bss_start`, `mwifiex_cmd_uap_sta_deauth`, and `mwifiex_cmd_uap_add_station`.

## Control Flow and Integration
AP start configuration is assembled into `struct mwifiex_uap_bss_param`. Security parsing maps cfg80211 privacy/auth/AKM/cipher selections into firmware protocol/key-management/cipher fields, including static WEP material copied from `priv->wep_key`. HT/VHT/TPC/WMM/rate helpers extract IEs from beacon head/tail. `mwifiex_uap_bss_param_prepare` then appends TLVs for MAC, SSID/broadcast SSID, rates, channel/band, beacon/DTIM, RTS/fragment/retry, WPA/WEP security, auth type, encryption protocol, HT capability, WMM capability, station ageout timers, power constraint, and PS ageout timer.

`mwifiex_uap_prepare_cmd` dispatches command numbers to sys-config, BSS start/stop/reset/list, deauth, channel report, or add-station builders. Host MLME BSS start optionally adds a `TLV_TYPE_HOST_MLME`. Add-station command creation updates/creates the station node, copies AID/listen interval/capability, emits STA flags, extended capability, supported rates, QoS, HT/VHT, and opmode TLVs, and initializes peer AMPDU and RX sequence state.

`mwifiex_uap_set_channel` maps cfg80211 chandef to channel/band/secondary-channel fields and updates adapter `config_bands`; band changes trigger domain-info and TX power table downloads. `mwifiex_config_start_uap` sends sys-config and BSS-start commands, then updates MAC_CONTROL for WEP packet filtering.

## State and Persistence Behavior
The file mutates `priv->sec_info`, `priv->wmm_enabled`, `priv->ap_11n_enabled`, `priv->ap_11ac_enabled`, `priv->bss_chandef`, `priv->curr_pkt_filter`, station-node fields, and `adapter->config_bands`. Firmware state persists through `HostCmd_CMD_UAP_SYS_CONFIG`, `HostCmd_CMD_UAP_BSS_START`, `HostCmd_CMD_11AC_CFG`, `HostCmd_CMD_ADD_NEW_STATION`, `HostCmd_CMD_MAC_CONTROL`, and related AP commands.

## Dependencies and Risks
Dependencies include cfg80211 AP settings, Linux 802.11 IE structs, mwifiex 11n/11ac helpers, station-list utilities, regulatory/TX power download functions, and firmware TLV layouts. Risks are TLV buffer-size assumptions, malformed or oversized beacon IEs, security mode mismatch between `sec_info` and firmware TLVs, incorrect band/secondary-channel encoding, and station-node mutation during command preparation before firmware acceptance.

## Test Signals
Test AP start for open, WPA/WPA2/SAE, static WEP, WMM on/off, HT/VHT widths, country IE 11D enable, custom IE programming, add/remove station with HT/VHT/QoS params, channel width transitions, and failure paths from sys-config/BSS-start/MAC_CONTROL.
