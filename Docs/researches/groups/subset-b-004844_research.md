# subset-b-004844 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/cfg80211.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/cfg80211.c

## Purpose
`cfg80211.c` is the mwifiex bridge between Linux cfg80211/nl80211 userspace operations and the Marvell/NXP firmware command model. It registers a `wiphy`, advertises supported bands/rates/ciphers/interface combinations, creates and destroys netdev-backed virtual interfaces, and implements the cfg80211 callbacks for station, IBSS, AP/uAP, P2P, TDLS, DFS, WoWLAN, scan, key management, antenna, CQM, coalescing, and host-MLME flows. The file is the main policy and translation layer: cfg80211 objects are validated and converted into mwifiex private state plus `HostCmd_*` firmware commands.

## Important APIs, types, and functions
The exported entry points are `mwifiex_register_cfg80211()`, `mwifiex_add_virtual_intf()`, `mwifiex_del_virtual_intf()`, `mwifiex_send_domain_info_cmd_fw()`, and `mwifiex_init_channel_scan_gap()`. The internal `mwifiex_cfg80211_ops` table binds the driver to cfg80211 callbacks such as `.scan`, `.connect`, `.disconnect`, `.start_ap`, `.stop_ap`, `.tdls_mgmt`, `.start_radar_detection`, `.channel_switch`, `.set_coalesce`, and optional power-management callbacks.

Static capability tables define interface limits (`mwifiex_iface_comb_ap_sta*`), supported legacy rates, 2.4 GHz/5 GHz channels, cipher suites, management frame stypes, WoWLAN support, and coalesce limits. Helper functions translate channel width (`mwifiex_chan_type_to_sec_chan_offset()`, `mwifiex_get_chan_type()`), parse firmware HT/VHT rate metadata into `struct rate_info`, populate HT/VHT caps, and validate regulatory alpha2 module input.

The virtual interface lifecycle is split across `mwifiex_add_virtual_intf()`, `mwifiex_del_virtual_intf()`, `mwifiex_cfg80211_change_virtual_intf()`, role-specific transition helpers, and counter helpers for `adapter->curr_iface_comb`. Role changes deauthenticate, unregister management-frame RX masks, flush processing queues, reset `priv`, reinitialize BSS role/type/mode, configure firmware BSS mode, and run STA/P2P initialization commands.

## Control flow
Registration starts in `mwifiex_register_cfg80211()`: it clones the cfg80211 ops, optionally swaps in host-MLME auth/assoc/deauth callbacks, creates the `wiphy`, copies band definitions, selects interface-combination rules, sets cipher suites, regulatory behavior, wiphy flags/features, WoWLAN/coalesce descriptors, private BSS size, and initial SNMP thresholds from firmware. The adapter pointer is stored in `wiphy_priv()` and `adapter->wiphy` is assigned after `wiphy_register()`.

Station connection through the firmware-SME path enters `mwifiex_cfg80211_connect()`, stops background scan, and delegates to `mwifiex_cfg80211_assoc()`. Association clears previous security state, applies crypto/IE/WEP inputs, tries cached cfg80211 BSS results, optionally performs an SSID scan, starts the BSS through `mwifiex_bss_start()`, and reports success/failure through cfg80211. With host MLME enabled, `.auth` and `.assoc` replace `.connect`: `mwifiex_cfg80211_authenticate()` builds a firmware management-frame skb for auth and tracks `priv->auth_flag`, while `mwifiex_cfg80211_associate()` extracts SSID from the selected BSS, pushes IEs/security state, starts the BSS, and queues host-MLME association-response delivery.

AP startup in `mwifiex_cfg80211_start_ap()` builds a `mwifiex_uap_bss_param` from beacon interval, DTIM, SSID, hidden-SSID mode, inactivity timeout, channel definition, rates, security, HT/VHT, WMM, 11h/TPC, and 11d beacon information before starting firmware uAP and installing management IEs. Stop AP aborts CAC, deletes management IEs, clears AP state, stops and resets the firmware BSS, drops carrier, and stops queues. Scanning builds `mwifiex_user_scan_cfg` or `mwifiex_bg_scan_cfg`, maps channel flags into active/passive scan type, installs temporary VSIE slots, handles random scan MACs, and calls firmware scan/bgscan commands.

DFS flow starts CAC with `HostCmd_CMD_CHAN_REPORT_REQUEST` and delayed CAC work, or channel switch by parsing CSA IE, updating beacon IEs, saving the target chandef/beacon, optionally stopping carrier, and queueing channel-switch work. TDLS operations validate station/connection state, translate nl80211 operations into mwifiex TDLS commands, send TDLS management/data/action frames, and support TDLS channel switch against station-node capability/status. WoWLAN suspend cancels scans/CAC/commands, detaches netdevs, waits for transmit queues to drain, configures MEF filters and host-sleep conditions, and resume reports wake reasons and frees net-detect state.

## State and persistence behavior
This file updates persistent in-driver runtime state: `adapter->country_code`, `domain_reg`, `config_bands`, `adhoc_start_band`, `sec_chan_offset`, `curr_iface_comb`, `chan_stats`, wiphy capabilities, `priv->bss_mode`, `bss_type`, `bss_role`, `bss_started`, `cfg_bssid`, `sec_info`, WEP keys, management-frame masks, `roc_cfg`, scan flags, scheduled-scan state, CQM thresholds, DFS chandef/beacon state, host-MLME auth flags, and AP BSS config. Persistence is kernel-driver lifetime only; durable hardware state is delegated to firmware through synchronous/asynchronous `mwifiex_send_cmd()` calls.

## Dependencies and integration points
The file depends heavily on cfg80211/mac80211 data structures, netdev registration, workqueues, debugfs hooks, ethtool ops, TDLS/11n/WMM helpers, firmware command definitions, and mwifiex core helpers from `main.h`, `fw.h`, `11n.h`, and `wmm.h`. It uses `cmdevt.c`'s command queue indirectly through `mwifiex_send_cmd()`. Regulatory integration flows through `reg_notifier`, `wiphy_apply_custom_regulatory()`, and `regulatory_hint()`. Userspace integration is nl80211/cfg80211 plus hostapd/wpa_supplicant expectations such as probe-client feature probing and host-MLME management-frame registration.

## Risks and test signals
Risk is concentrated in state transitions and asynchronous cleanup: interface type changes flush workqueues while resetting `priv`; scan VSIE parsing copies IEs by advertised length and relies on bounded `MWIFIEX_MAX_VSIE_NUM`; ROC/auth state can block later auth/assoc if not cleared; AP/DFS operations must keep carrier, queues, management IEs, and firmware 11h state coherent; suspend cancels command queues and detaches all netdevs; and regulatory/domain changes directly affect firmware power tables. Regression signals should include nl80211 scan/connect/disconnect, hostapd AP start/stop/change beacon, P2P interface changes, IBSS join/leave, TDLS setup/channel switch, DFS CAC/channel switch, WoWLAN suspend/resume, antenna/rate-mask commands, regulatory changes, and command-timeout/device-removal paths. KUnit is unlikely here; meaningful validation is integration testing with cfg80211 tracepoints, firmware command logs, debugfs state, and userspace tools (`iw`, `wpa_supplicant`, `hostapd`, suspend/resume tests).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/cfg80211.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/cfg80211.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/cfg80211.h

## Purpose
`cfg80211.h` is the narrow public header for the mwifiex cfg80211 integration unit. It declares the registration hook used by the adapter initialization path and pulls in cfg80211 plus mwifiex core declarations needed for the function signature.

## Important APIs, types, and functions
The only API declared here is `int mwifiex_register_cfg80211(struct mwifiex_adapter *);`. The type `struct mwifiex_adapter` is made visible by including `main.h`, while cfg80211 structures are made visible by `<net/cfg80211.h>`. The include guard is `__MWIFIEX_CFG80211__`.

## Control flow
There is no runtime control flow in this header. At compile time it allows other driver translation units to call `mwifiex_register_cfg80211()` without depending on the full contents of `cfg80211.c`. The implementation allocates and registers the driver `wiphy`, configures wiphy capabilities, and stores the resulting `wiphy` on the adapter.

## State and persistence behavior
The header itself owns no state. Its declared function initializes long-lived cfg80211 state on `struct mwifiex_adapter`, but that state is implemented in `cfg80211.c` and the broader driver.

## Dependencies and integration points
This file connects the core mwifiex adapter initialization code to cfg80211 registration. It must stay consistent with `cfg80211.c`'s exported function signature and with `main.h`'s adapter definition. Because it includes `main.h`, changes here can increase compile-time coupling across the driver.

## Risks and test signals
Risk is low but ABI-internal: changing or removing this prototype breaks compilation for any unit that registers cfg80211. Test signals are compile coverage for mwifiex and successful adapter probe/registration paths that call `mwifiex_register_cfg80211()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/cfg80211.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/cfp.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/cfp.c

## Purpose
`cfp.c` supplies mwifiex channel/frequency/power and data-rate helpers. It holds static tables for legacy, HT, and VHT rates, region-code to country-code mapping, and functions that convert firmware rate indexes and band settings into cfg80211/driver-visible rates. It also locates channel-frequency-power data from the registered wiphy bands and derives supported-rate lists for station, P2P, and ad-hoc modes.

## Important APIs, types, and functions
`mwifiex_11d_code_2_region()` maps firmware region codes such as `0x10`, `0x20`, `0x40`, and `0x50` to 802.11 country strings. `mwifiex_index_to_data_rate()` and `mwifiex_index_to_acs_data_rate()` decode firmware rate index plus HT/VHT metadata into rates in 500 kb/s-style firmware units. `mwifiex_get_active_data_rates()` returns either current BSS rates or supported rates depending on connection state. `mwifiex_get_cfp()` searches `wiphy->bands[]` for a usable channel/frequency and stores the result in `priv->cfp`. `mwifiex_is_rate_auto()` checks whether the configured rate bitmap contains more than one active slot. `mwifiex_get_rates_from_cfg80211()` converts a cfg80211 scan request rate mask to mwifiex scan rates. `mwifiex_get_supported_rates()` chooses a rate table based on station/P2P versus ad-hoc mode and band flags. `mwifiex_adjust_data_rate()` maps RX rate/HT info into histogram indexes.

Important static data includes CCK/OFDM supported and ad-hoc rate arrays, `mwifiex_data_rates`, `mcs_rate`, VHT NSS1/NSS2 MCS rate tables, `region_code_index`, and the `region_code_mapping_t` array.

## Control flow
Rate conversion first tests format bits. For VHT, it clamps MCS to 0-9, extracts bandwidth and guard interval from `ht_info`, chooses NSS based on the high nibble of the index, and indexes the AC MCS table. For HT, it handles MCS32 specially, then indexes 20/40 MHz LGI/SGI tables for MCS 0-15, with fallback to the first legacy rate. For non-HT, it bounds the index into `mwifiex_data_rates`.

Channel lookup in `mwifiex_get_cfp()` converts a mwifiex band into a cfg80211 band, rejects missing bands, skips disabled channels, and matches either exact center frequency or channel number, with `FIRST_VALID_CHANNEL` as a wildcard for the first valid channel. Supported-rate selection switches on `adapter->config_bands` for infrastructure/P2P and `adapter->adhoc_start_band` for ad-hoc, copying a zero-terminated table into the caller buffer with `mwifiex_copy_rates()`.

## State and persistence behavior
Most data is static read-only lookup state. Mutable state updates are limited and explicit: `mwifiex_get_cfp()` writes `priv->cfp.channel`, `priv->cfp.freq`, and `priv->cfp.max_tx_power`; `mwifiex_get_rates_from_cfg80211()` reads `priv->scan_request`; supported-rate selection reads `adapter->config_bands` and `adapter->adhoc_start_band`; rate-auto reads `priv->bitmap_rates`. No persistent storage is touched.

## Dependencies and integration points
This file depends on cfg80211 band/channel structures populated by `cfg80211.c`, firmware band constants from mwifiex headers, scan request state from cfg80211, and helper macros such as `mwifiex_band_to_radio_type()`, `mwifiex_copy_rates()`, and capability flags from `main.h`/`fw.h`. `cfg80211.c` uses the country-code mapper during regulatory hints and the channel/rate helpers during scan, association, station info, and histogram reporting.

## Risks and test signals
Incorrect table indexes or bit interpretation can report bad data rates, break rate masks, or corrupt histogram buckets. Channel lookup depends on wiphy band registration and regulatory-disabled flags, so regulatory changes can make expected channels unavailable. Test signals include connecting on 2.4 GHz and 5 GHz, HT20/HT40/VHT rate reporting, scan requests with custom rate masks, ad-hoc band selection, regulatory country changes, and debugfs histogram rate buckets. Boundary cases should cover MCS32, 1x1 versus 2x2, disabled channels, missing 5 GHz band, and out-of-range firmware indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/cfp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/cmdevt.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/cmdevt.c

## Purpose
`cmdevt.c` implements the mwifiex firmware command and event transport core. It owns command-node allocation, free/pending/scan queues, synchronous wait completion, command download to the bus-specific interface, command response processing, timeout recovery, event demultiplexing, sleep-confirm handling, host-sleep activation, enhanced power-save command preparation/response, and hardware-spec response parsing.

## Important APIs, types, and functions
Core command APIs include `mwifiex_send_cmd()`, `mwifiex_insert_cmd_to_pending_q()`, `mwifiex_exec_next_cmd()`, `mwifiex_process_cmdresp()`, `mwifiex_alloc_cmd_buffer()`, `mwifiex_free_cmd_buffer()`, `mwifiex_recycle_cmd_node()`, `mwifiex_cancel_pending_scan_cmd()`, `mwifiex_cancel_all_pending_cmd()`, and the internal `mwifiex_dnld_cmd_to_fw()`. Event and power APIs include `mwifiex_process_event()`, `mwifiex_check_ps_cond()`, `mwifiex_hs_activated_event()`, `mwifiex_process_hs_config()`, `mwifiex_process_sleep_confirm_resp()`, `mwifiex_cmd_enh_power_mode()`, `mwifiex_ret_enh_power_mode()`, `mwifiex_cmd_get_hw_spec()`, `mwifiex_ret_get_hw_spec()`, and `mwifiex_ret_wakeup_reason()`.

Important state holders are `struct cmd_ctrl_node`, `struct host_cmd_ds_command`, adapter queues and locks (`cmd_free_q`, `cmd_pending_q`, `scan_pending_q`, `mwifiex_cmd_lock`), `adapter->curr_cmd`, `cmd_timer`, wait queues, work flags, debug rings, bus `if_ops`, and power-save/host-sleep fields.

## Control flow
Command submission starts in `mwifiex_send_cmd()`, which rejects suspended, host-sleep-entering, surprise-removed, timed-out, reset, or manufacturing-mode-incompatible cases. It obtains a free command node, initializes sync wait fields when requested, creates a host command header, delegates preparation to uAP or STA command builders, and queues scan commands separately from normal pending commands. Normal commands are inserted into `cmd_pending_q`, main work is queued, and sync callers wait for command completion.

`mwifiex_exec_next_cmd()` refuses to run if `curr_cmd` is occupied, pops the next pending command, ensures the adapter is awake, and calls `mwifiex_dnld_cmd_to_fw()`. Download assigns sequence/BSS info, sets `adapter->curr_cmd`, adjusts skb length, logs command/action, pushes USB or generic interface headers, calls `if_ops.host_to_card()`, records debug history, and arms the command timer unless the command has no response. Responses enter `mwifiex_process_cmdresp()`, which validates the response against `curr_cmd`, deletes the timer, resolves the private BSS from sequence bits, handles raw host-command responses, dispatches STA command responses, sets wait status, recycles the node, and clears `curr_cmd`.

Events enter `mwifiex_process_event()`, which adjusts radar events to the active 11h BSS, logs event history, resolves the target `priv` from event BSS bits, annotates the event skb RX control block, and dispatches to uAP or STA event handlers before calling `if_ops.event_complete()`. Timeout flow sets `MWIFIEX_IS_CMD_TIMEDOUT`, dumps debug history/counters, fails waiting commands, requests device dump, and asks the bus layer to reset the card when supported.

## State and persistence behavior
Command buffers are preallocated for the adapter lifetime and recycled through free/pending queues. `adapter->seq_num`, `curr_cmd`, `cmd_pending`, `cmd_sent`, `event_cause`, debug rings, timeout markers, power-save state, host-sleep flags, firmware capabilities, band configuration, antenna/MCS capabilities, firmware API versions, region code, and permanent address are updated here. State is volatile driver state mirrored from firmware responses; no durable filesystem persistence is used.

## Dependencies and integration points
This file is the integration point between high-level driver code and transport-specific `if_ops` (`host_to_card`, `cmdrsp_complete`, `event_complete`, `wakeup`, `device_dump`, `card_reset`, `update_mp_end_port`). It calls STA/uAP command preparation and response handlers, scan queue/cancel helpers, power-save helpers, WMM queue checks, RX reorder adjustments, cfg80211 association-response delivery for host MLME, and bus-specific USB handling. `cfg80211.c`, debugfs, ethtool, and most driver features ultimately depend on `mwifiex_send_cmd()`.

## Risks and test signals
Primary risks are concurrency and lifecycle hazards: queue locking order, `curr_cmd` reuse after timeout, response arrival after timeout cancellation, sync wait completion, USB skb ownership on `-EBUSY`, command timer deletion, and reset-state command filtering. Hardware-spec parsing controls advertised capabilities; mistakes can disable host MLME, 11ac, scan gaps, or antenna/rate support. Test signals include command flood with concurrent scans, sync command timeout, surprise removal, suspend/resume, host sleep activation/cancel, USB and non-USB transport paths, hardware-spec parsing on multiple firmware API versions, and association response delivery under host MLME. Debugfs `debug` output and command/event trace logs are key observability points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/cmdevt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/debugfs.c

## Purpose
`debugfs.c` exposes mwifiex runtime state and low-level controls under debugfs. It creates a top-level `mwifiex` directory and per-netdev directories containing readouts for driver/BSS info, firmware statistics, internal debug rings, RX histogram data, version strings, and read/write controls for registers, memory, EEPROM, host-sleep config, debug mask, robust coexistence, histogram reset, and device reset.

## Important APIs, types, and functions
Lifecycle APIs are `mwifiex_debugfs_init()`, `mwifiex_debugfs_remove()`, `mwifiex_dev_debugfs_init()`, and `mwifiex_dev_debugfs_remove()`. Read handlers include `mwifiex_info_read()`, `mwifiex_getlog_read()`, `mwifiex_histogram_read()`, `mwifiex_debug_read()`, `mwifiex_regrdwr_read()`, `mwifiex_debug_mask_read()`, `mwifiex_verext_read()`, `mwifiex_memrw_read()`, `mwifiex_rdeeprom_read()`, `mwifiex_hscfg_read()`, and `mwifiex_timeshare_coex_read()`. Write handlers include `mwifiex_histogram_write()`, `mwifiex_regrdwr_write()`, `mwifiex_debug_mask_write()`, `mwifiex_verext_write()`, `mwifiex_memrw_write()`, `mwifiex_rdeeprom_write()`, `mwifiex_hscfg_write()`, `mwifiex_timeshare_coex_write()`, and `mwifiex_reset_write()`.

Macros generate `struct file_operations` for read-only, write-only, and read/write debugfs files, and `MWIFIEX_DFS_ADD_FILE()` creates each file in `priv->dfs_dev_dir`.

## Control flow
Module-level setup calls `mwifiex_debugfs_init()` to create `/sys/kernel/debug/mwifiex`. Per-interface setup calls `mwifiex_dev_debugfs_init()`, which creates a directory named after `priv->netdev->name` and registers files such as `info`, `debug`, `getlog`, `regrdwr`, `rdeeprom`, `memrw`, `hscfg`, `histogram`, `debug_mask`, `timeshare_coex`, `reset`, and `verext`. Removal recursively deletes the per-device directory or top-level directory.

Read handlers allocate a page or stack buffer, query live driver/firmware state, format text with `sprintf`/`snprintf`/`scnprintf`, and return it through `simple_read_from_buffer()`. Write handlers copy user input with `memdup_user_nul()` or typed `kstrto*from_user()` helpers, parse command fields, update saved command parameters or adapter state, and often invoke synchronous firmware commands. `regrdwr` and `rdeeprom` use a write-then-read model where write stores the requested operation in static file-scope variables and subsequent read executes or displays it. `memrw`, `hscfg`, and `timeshare_coex` call firmware command helpers immediately on write.

## State and persistence behavior
Debugfs state is live and kernel-resident. File-scope saved variables hold the last register and EEPROM requests globally, not per-interface, which is observable if multiple interfaces use debugfs concurrently. `debug_mask_write()` changes `adapter->debug_mask`; `verext_write()` changes `priv->versionstrsel`; `histogram_write()` resets `priv->hist_data`; `memrw_write()` updates `priv->mem_rw`; `hscfg_write()` can update firmware host-sleep configuration and host-sleep flags; `reset_write()` can trigger bus-level card reset. Debugfs entries disappear when the device/interface is removed.

## Dependencies and integration points
This file depends on Linux debugfs, netdev stats and multicast lists, mwifiex BSS/stat/debug/version helpers, firmware command paths, register/memory/EEPROM accessors, host-sleep helpers, histogram storage defined in `decl.h`, and bus reset support exposed through `adapter->if_ops.card_reset`. `cfg80211.c` calls per-device debugfs init/remove when virtual interfaces are registered/unregistered under `CONFIG_DEBUG_FS`.

## Risks and test signals
The file intentionally exposes powerful diagnostic operations. Risks include global saved register/EEPROM state across interfaces, synchronous firmware commands from debugfs context, page-sized formatted output truncation, command parsing mistakes, and reset/debug-mask controls that can disrupt normal operation. `sprintf` accumulation assumes output fits the allocated page in several handlers. Test signals include reading all debugfs files on disconnected and connected STA, AP mode, multiple virtual interfaces, invalid write payloads, register/memory/EEPROM read/write failure paths, robust-coex on non-v15 firmware, histogram reset, host-sleep configuration, and card reset behavior. Lockdep and KASAN are useful when exercising debugfs during interface removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/decl.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/decl.h

## Purpose
`decl.h` is a shared mwifiex declaration header for generic constants, small enums, packet metadata structures, WMM structures, histogram/storage structs, DFS/radar structs, firmware-dump definitions, and channel-width/offset enums. It establishes common values used across cfg80211, firmware command/event handling, data path, debugfs, power management, TDLS, 11n/11ac, and SDIO aggregation code.

## Important APIs, types, and functions
The file has no functions; its API surface is macros, enums, and structs. Major constants include BSS/interface limits, DMA/RX/TX headroom and management-frame sizes, host-MLME auth flags, management frame masks, block-ack stream limits, AMPDU window defaults, RTS/fragment thresholds, WMM version fields, retry limits, skb flag bits, TDLS operation values, TDLS RSSI/failure thresholds, rate index values, max STA/uAP/P2P counts, SDIO aggregation constants, histogram bounds, firmware-dump markers, and channel-width/offset values.

Key enums are `mwifiex_bss_type`, `mwifiex_bss_role`, `mwifiex_tdls_status`, `mwifiex_tdls_error_code`, `mwifiex_data_frame_type`, `mwifiex_wmm_ac_e`, `rdwr_status`, `mwifiex_chan_width`, and `mwifiex_chan_offset`. Key structs include `mwifiex_fw_image`, `mwifiex_802_11_ssid`, `mwifiex_wait_queue`, `mwifiex_rxinfo`, `mwifiex_txinfo`, WMM IE structs, `mwifiex_arp_eth_header`, `mwifiex_chan_stats`, `mwifiex_histogram_data`, `mwifiex_iface_comb`, `mwifiex_radar_params`, `mwifiex_11h_intf_state`, and `memory_type_mapping`.

## Control flow
There is no executable control flow. Compile-time consumers use this header to agree on structure layouts, bit meanings, and numeric bounds. Macros such as `GET_BSS_ROLE()` influence runtime branches in other files by masking `priv->bss_role`.

## State and persistence behavior
The header defines layouts for state stored elsewhere. Examples include per-skb RX/TX control blocks (`mwifiex_rxinfo`, `mwifiex_txinfo`), histogram counters (`mwifiex_histogram_data`), interface-combination counters (`mwifiex_iface_comb`), channel stats used by survey reporting, DFS CAC/channel-switch parameters, and firmware-dump memory tracking. The actual state lifetime is owned by adapters, priv structures, skbs, or debug/firmware-dump paths.

## Dependencies and integration points
`decl.h` includes kernel wait queues, timers, IEEE 802.11 definitions, ARP user ABI, and cfg80211. Its constants are used by `cfg80211.c` for management frame formatting, host-MLME auth, TDLS, AP settings, RTS/fragment validation, channel stats, scan-gap allocation, and DFS. `debugfs.c` uses histogram bounds and data structures. `cmdevt.c` uses wait queues, command buffer sizing from related headers, BSS role/type values, and power/host-sleep state conventions. Because it is included broadly, changes can have wide compile and ABI-layout impact inside the driver.

## Risks and test signals
Risks are compatibility and bounds risks: changing packet header lengths or headroom values can break firmware packet framing; altering enum numeric values can break firmware protocol assumptions; shrinking histogram or rate limits can cause out-of-bounds users; changing `__packed` structures can alter wire format; and BSS role/type constants are embedded in command sequence/event demux paths. Test signals are broad compile coverage plus runtime tests for management-frame TX/auth, skb metadata handling, histogram updates/debugfs reads, TDLS transitions, DFS CAC, firmware dump, SDIO aggregation, and command/event BSS routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/decl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/ethtool.c

## Purpose
`ethtool.c` provides the mwifiex netdev ethtool operations for Wake-on-LAN reporting and configuration. It maps ethtool WOL flags to the driver's host-sleep condition bitmap stored on the adapter.

## Important APIs, types, and functions
`mwifiex_ethtool_get_wol()` fills `struct ethtool_wolinfo` with supported wake sources and currently configured options. `mwifiex_ethtool_set_wol()` validates requested options and updates `priv->adapter->hs_cfg.conditions`. `mwifiex_ethtool_ops` exposes these as `.get_wol` and `.set_wol`; `cfg80211.c` assigns this ops table to each allocated netdev.

## Control flow
Get flow reads little-endian `adapter->hs_cfg.conditions`, always reports support for unicast, multicast, broadcast, and PHY/MAC-event wake, then returns no enabled options if conditions are at the default value. Otherwise, individual host-sleep condition bits are translated to `WAKE_UCAST`, `WAKE_MCAST`, `WAKE_BCAST`, and `WAKE_PHY`.

Set flow rejects unsupported ethtool bits, builds a host-sleep condition bitmap from requested WOL flags, uses `HS_CFG_COND_DEF` when no options are requested, and stores the result back to the adapter in little-endian form. It does not directly send a firmware command; later host-sleep/WoWLAN paths consume the stored configuration.

## State and persistence behavior
The only persistent state update is `priv->adapter->hs_cfg.conditions`, lasting for the adapter lifetime and influencing future host-sleep configuration. No hardware command is issued here, so ethtool configuration is staged driver state until power-management code applies it.

## Dependencies and integration points
This file depends on `main.h` for `mwifiex_netdev_get_priv()` and host-sleep condition constants. It integrates with Linux ethtool through `struct ethtool_ops` and with netdev setup in `mwifiex_add_virtual_intf()`. Runtime effect is coupled to `cmdevt.c` host-sleep handling and cfg80211 suspend/WoWLAN flows.

## Risks and test signals
Risk is low but semantic: ethtool may report WOL support regardless of firmware/runtime readiness, and setting options only updates cached conditions. Endianness must remain consistent because `hs_cfg.conditions` is stored little-endian. Test signals include `ethtool -s wol`/`ethtool` get cycles for all flag combinations, unsupported flag rejection, suspend/resume wake behavior after ethtool configuration, and interaction with cfg80211 WoWLAN settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/ethtool.c -->
