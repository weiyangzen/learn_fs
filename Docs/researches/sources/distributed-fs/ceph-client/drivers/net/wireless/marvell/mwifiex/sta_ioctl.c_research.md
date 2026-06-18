# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/sta_ioctl.c

## Purpose
`sta_ioctl.c` is the station-side control/configuration surface for mwifiex. It bridges cfg80211/netdev requests and internal driver callers into firmware commands for association, multicast filtering, host sleep, power save, TX power, security material, regulatory country handling, remain-on-channel, statistics, register/EEPROM access, and generic IE storage.

## Important APIs, Types, and Functions
Key exported or externally consumed entry points include `mwifiex_copy_mcast_addr`, `mwifiex_wait_queue_complete`, `mwifiex_request_set_multicast_list`, `mwifiex_fill_new_bss_desc`, `mwifiex_dnld_txpwr_table`, `mwifiex_bss_start`, `mwifiex_set_hs_params`, `mwifiex_cancel_hs`, `mwifiex_enable_hs`, `mwifiex_get_bss_info`, `mwifiex_disable_auto_ds`, `mwifiex_drv_get_data_rate`, `mwifiex_set_tx_power`, `mwifiex_drv_set_power`, `mwifiex_set_encode`, `mwifiex_get_ver_ext`, `mwifiex_remain_on_chan_cfg`, `mwifiex_get_stats_info`, `mwifiex_reg_write`, `mwifiex_reg_read`, `mwifiex_eeprom_read`, `mwifiex_set_gen_ie`, `mwifiex_get_wakeup_reason`, and `mwifiex_get_chan_info`. Internally, the file owns helpers for WPA/WAPI/WPS IE parsing, WEP/WPA/WAPI key programming, country IE processing, regulatory power table loading, and generic IE/ARP filter handling.

## Control Flow and Integration
Association starts in `mwifiex_bss_start`: optional country IE processing updates adapter regulatory state and downloads TX power limits, then a temporary `mwifiex_bssdescriptor` is filled from cfg80211 BSS IEs. STA/P2P client mode checks network compatibility, blocks netdev queues, clears old association response state, and calls `mwifiex_associate`, retrying shared-key auth for auto-WEP failures. Ad-hoc mode either joins a compatible scanned BSS or starts a new IBSS. Multicast changes first adjust `priv->curr_pkt_filter`; selected multicast lists are sent with `HostCmd_CMD_MAC_MULTICAST_ADR`, and filter changes are committed with `HostCmd_CMD_MAC_CONTROL`.

Host sleep flow is split between configuration and activation. `mwifiex_set_hs_params` stores or sends `adapter->hs_cfg`, refusing HS changes during PPS/UAPSD. `mwifiex_enable_hs` optionally disconnects all interfaces on suspend, stops scheduled scan when needed, sets `MWIFIEX_IS_HS_ENABLING`, cancels pending commands, sends synchronous HS enable, and waits on `hs_activate_wait_q`.

Security flow stores user IEs and key state in `priv`. WPA/RSN/WAPI/WPS IEs are detected from generic IE buffers; WEP keys are cached in `priv->wep_key`, update `sec_info.wep_enabled`, and toggle firmware packet filter WEP enable. WPA/WAPI keys are forwarded as `HostCmd_CMD_802_11_KEY_MATERIAL`; IBSS WPA-None duplicates the key as PTK and GTK.

## State and Persistence Behavior
Persistent mutable state includes `adapter->country_code`, `adapter->domain_reg`, `adapter->rgpower_data`, `adapter->config_bands`, `adapter->hs_cfg`, `adapter->ps_mode`, `adapter->arp_filter`, `priv->curr_pkt_filter`, `priv->sec_info`, WEP key slots, `priv->wpa_ie`, `priv->wapi_ie`, heap-allocated `priv->wps_ie`, `priv->gen_ie_buf`, `priv->assoc_rsp_size`, and `priv->attempted_bss_desc`. Firmware state is kept in sync through synchronous and asynchronous `mwifiex_send_cmd` calls. The file also exposes direct register and EEPROM commands, which are stateful firmware/hardware probes rather than local persistence.

## Dependencies and Risks
The file depends heavily on cfg80211 BSS/IE APIs, firmware command definitions in `fw.h`/`ioctl.h`, WMM/11n helpers, device-tree and firmware-loader APIs for regulatory power tables, and adapter/private locking disciplines from the broader driver. Risks concentrate around variable-length IE parsing and TLV/key copying, firmware command synchronization, lifetime of BSS IE buffers under RCU, `priv->wps_ie` allocation/replacement, and privileged register/EEPROM access. Country IE length validation and TX power range checks are explicit guardrails; generic IE parsing still depends on well-formed element lengths to advance through buffers.

## Test Signals
Useful signals are association success/failure counters, cfg80211 connect/disconnect outcomes, host-sleep suspend/resume success, multicast/promiscuous packet behavior, WEP/WPA/WAPI key programming, remain-on-channel callbacks, regulatory power table request logs, data-rate and stats queries, and error logs from `mwifiex_wait_queue_complete`, malformed IE/key sizes, and firmware command failures.
