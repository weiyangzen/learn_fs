# subset-b-004794 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bus.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bus.h

## Purpose
`bus.h` defines the common brcmfmac bus abstraction used between the bus-specific transports (SDIO, USB, PCIe) and the core/cfg80211/protocol layers. It standardizes bus state, firmware vendor identity, protocol type, firmware blob retrieval, msgbuf ring metadata, shared bus statistics, and the callback table that all bus backends expose to the common driver.

The file is a contract header rather than an implementation unit. Its inline wrappers are the normal call surface for upper layers so that most of brcmfmac does not need to know whether the underlying device is SDIO, USB, or PCIe.

## Important APIs, Types, And Functions
- Ring constants:
  - `BRCMF_H2D_MSGRING_CONTROL_SUBMIT`, `BRCMF_H2D_MSGRING_RXPOST_SUBMIT`, and `BRCMF_H2D_MSGRING_FLOWRING_IDSTART` identify host-to-device msgbuf rings.
  - `BRCMF_D2H_MSGRING_CONTROL_COMPLETE`, `BRCMF_D2H_MSGRING_TX_COMPLETE`, and `BRCMF_D2H_MSGRING_RX_COMPLETE` identify device-to-host rings.
  - `BRCMF_NROF_H2D_COMMON_MSGRINGS`, `BRCMF_NROF_D2H_COMMON_MSGRINGS`, and `BRCMF_NROF_COMMON_MSGRINGS` encode the common-ring count.
- Bus identity and mode enums:
  - `enum brcmf_fwvendor` distinguishes WCC, CYW, BCA, invalid, and count values for firmware vendor behavior.
  - `enum brcmf_bus_state` is the global transfer readiness switch: `BRCMF_BUS_DOWN` or `BRCMF_BUS_UP`.
  - `enum brcmf_bus_protocol_type` selects BCDC or MSGBUF host/dongle protocol.
  - `enum brcmf_blob_type` names firmware blob categories such as CLM and TXCAP.
- `struct brcmf_bus_ops` is the bus callback vtable. Mandatory callbacks include `stop`, `txdata`, `txctl`, and `rxctl`; optional callbacks include `preinit`, `gettxq`, `wowl_config`, memory dump, blob retrieval, debugfs setup, reset, and transport-specific remove.
- `struct brcmf_bus_msgbuf` carries ring pointers and msgbuf limits for PCIe/msgbuf operation: common rings, flowrings, RX offset, RX post count, flowring count, and submission/completion ring limits.
- `struct brcmf_bus_stats` currently tracks packet copy-on-write counts through atomics.
- `struct brcmf_bus` is the central bus instance:
  - `bus_priv` stores one of `sdio`, `usb`, or `pcie` private device pointers.
  - `proto_type`, `dev`, `drvr`, `state`, `stats`, `maxctl`, `chip`, `chiprev`, `fwvid`, queue and WoWLAN capability flags, `ops`, `msgbuf`, and `list` connect the bus to common driver state.
- Inline wrappers:
  - `brcmf_bus_preinit()`, `brcmf_bus_stop()`, `brcmf_bus_txdata()`, `brcmf_bus_txctl()`, `brcmf_bus_rxctl()`.
  - `brcmf_bus_gettxq()`, `brcmf_bus_wowl_config()`, `brcmf_bus_get_ramsize()`, `brcmf_bus_get_memdump()`, `brcmf_bus_get_blob()`, `brcmf_bus_debugfs_create()`, `brcmf_bus_reset()`, and `brcmf_bus_remove()`.
- Common-layer entry points declared for bus users include `brcmf_alloc()`, `brcmf_attach()`, `brcmf_detach()`, `brcmf_free()`, `brcmf_dev_reset()`, `brcmf_dev_coredump()`, `brcmf_fw_crashed()`, `brcmf_bus_change_state()`, and bus-specific register/exit stubs for SDIO, USB, and PCIe.

## Control Flow
Bus-specific modules create a `struct brcmf_bus`, populate `ops`, point `dev` and `bus_priv` at their transport device, and call common-layer functions such as `brcmf_attach()`. Once attached, upper layers use the inline wrappers in this header to send data and control messages without branching on transport type.

The typical data path is:
1. Core/network code decides a frame or control message must go to firmware.
2. It calls `brcmf_bus_txdata()`, `brcmf_bus_txctl()`, or `brcmf_bus_rxctl()`.
3. The wrapper dispatches through `bus->ops` to the active SDIO, USB, or PCIe implementation.
4. Completion and RX traffic flow back through common-layer callbacks such as `brcmf_rx_frame()` and `brcmf_rx_event()`.

Optional capability paths have explicit defaults. `preinit()` returns success when absent; `gettxq()` returns `ERR_PTR(-ENOENT)`; WoWLAN config and debugfs creation become no-ops; RAM size returns zero; memory dump and reset return `-EOPNOTSUPP`; `brcmf_bus_remove()` falls back to `device_release_driver()` when no bus remove callback exists.

## State And Persistence Behavior
`struct brcmf_bus` persists for the lifetime of a brcmfmac device and carries global bus state consumed by cfg80211/core paths. The key persistent state is `state`, which upper layers use as a safety check before firmware commands, and metadata such as chip ID, chip revision, firmware vendor, and protocol type. `stats` persist atomic counters across normal packet handling until detach. `msgbuf` persists transport ring topology for msgbuf-capable devices.

No file-backed or firmware-backed persistence is implemented in this header. It defines in-memory structures and wrappers only; hardware and firmware state changes happen in bus-specific callback implementations and common-layer code that call into this interface.

## Dependencies And Integration Points
- Includes Linux kernel device, firmware, and kernel headers plus `debug.h`.
- Depends on forward-declared transport-private types `brcmf_sdio_dev`, `brcmf_usbdev`, and `brcmf_pciedev` through the `bus_priv` union.
- Depends on common driver types such as `struct brcmf_pub`, `struct brcmf_mp_device`, `struct brcmf_commonring`, `struct pktq`, and `struct sk_buff`.
- Integrated by cfg80211 and core code through `drvr->bus_if`; for example cfg80211 checks `drvr->bus_if->state == BRCMF_BUS_UP`, uses `fwvid` for firmware-vendor security behavior, and calls `brcmf_bus_wowl_config()` during suspend/resume.
- Conditional registration helpers (`brcmf_sdio_register()`, `brcmf_usb_register()`, `brcmf_pcie_register()`) isolate core module init/exit from disabled bus build options by returning zero or no-op stubs.

## Risks
- Several inline wrappers dereference mandatory callbacks without null checks. A bus backend that leaves `stop`, `txdata`, `txctl`, or `rxctl` unset will crash callers.
- `brcmf_bus_get_blob()` does not check `ops->get_blob`; it assumes bus implementations that support firmware blobs have wired the callback before use.
- `state` is a shared readiness signal. Incorrect transitions between `BRCMF_BUS_DOWN` and `BRCMF_BUS_UP` can allow cfg80211/core paths to send commands to a halted bus or reject valid operations.
- The msgbuf ring ID constants are part of the transport/protocol ABI. Changing them would misroute control, RX, TX-complete, or dynamic flowring traffic.
- `brcmf_bus_remove()` has two paths: transport-specific remove and generic `device_release_driver()`. Callers must account for both and avoid double-unbind behavior.

## Test Signals
- Build tests across `CONFIG_BRCMFMAC_SDIO`, `CONFIG_BRCMFMAC_USB`, and `CONFIG_BRCMFMAC_PCIE` should verify the conditional stubs and real register functions compile.
- Probe/attach smoke tests should show each bus backend populating mandatory `ops` and transitioning to `BRCMF_BUS_UP` before normal cfg80211 operations.
- Runtime signals include successful control command round trips through `brcmf_bus_txctl()`/`brcmf_bus_rxctl()`, data TX completions through the bus implementation, and RX delivery via `brcmf_rx_frame()`/`brcmf_rx_event()`.
- Suspend/resume tests should verify `brcmf_bus_wowl_config()` is called only when the bus advertises WoWLAN support and that missing optional callbacks degrade cleanly.
- Failure-path tests should cover absent optional callbacks returning `-EOPNOTSUPP` or `ERR_PTR(-ENOENT)` as documented by the wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c

## Purpose
`cfg80211.c` is the main Linux cfg80211 integration layer for brcmfmac. It translates nl80211/cfg80211 operations into Broadcom firmware commands and iovars, translates firmware events back into cfg80211 notifications, builds the wiphy capability model from firmware features, and coordinates station, AP, P2P, scheduled scan, WoWLAN, PMKSA, TDLS, RSSI CQM, and regulatory behavior.

The file sits between the kernel wireless stack and the brcmfmac core/protocol/firmware-event layers. It owns most user-visible Wi-Fi control flow: scan, connect, disconnect, AP creation, key management, virtual interface management, suspend/resume wake handling, and wiphy registration.

## Important APIs, Types, And Functions
- Static capability data:
  - `__wl_rates`, `__wl_2ghz_channels`, `__wl_5ghz_channels`, `__wl_band_2ghz`, and `__wl_band_5ghz` are base cfg80211 rate/channel/band templates.
  - `brcmf_regdom` is the custom default regulatory domain applied at attach.
  - `brcmf_cipher_suites` advertises WEP, TKIP, CCMP, and optionally AES-CMAC when MFP is supported.
  - `brcmf_txrx_stypes` advertises management frame TX/RX subtypes per station, AP, and P2P iftype.
- Interface management:
  - `brcmf_cfg80211_add_iface()`, `brcmf_apsta_add_vif()`, `brcmf_mon_add_vif()`, and `brcmf_p2p_add_vif()` create cfg80211 vifs.
  - `brcmf_cfg80211_del_iface()`, `brcmf_cfg80211_del_apsta_iface()`, and `brcmf_mon_del_vif()` remove them.
  - `brcmf_cfg80211_change_iface()` maps nl80211 iftypes to firmware infrastructure/AP/P2P mode and updates protocol address mode.
  - `brcmf_alloc_vif()`, `brcmf_free_vif()`, and `brcmf_cfg80211_free_vif()` manage `struct brcmf_cfg80211_vif` lifetime.
- Scanning:
  - `brcmf_cfg80211_scan()` validates state, saves `cfg->scan_request`, programs probe-request vendor IEs, runs escan, and arms the timeout timer.
  - `brcmf_escan_prep()`, `brcmf_run_escan()`, and `brcmf_do_escan()` build firmware scan structures and issue the `"escan"` iovar.
  - `brcmf_cfg80211_escan_handler()` handles partial and complete escan firmware events, merges BSS results into `escan_buf`, reports BSS entries, and completes cfg80211 scan state.
  - `brcmf_notify_escan_complete()` centralizes scan completion, scan abort, MPC restoration, scheduled-scan result notification, and `cfg80211_scan_done()`.
- Connection and security:
  - `brcmf_cfg80211_connect()` configures WPA version, auth mode, ciphers, key management, shared WEP, firmware supplicant/offload state, join preferences, and firmware join/set-SSID commands.
  - `brcmf_cfg80211_disconnect()`, `brcmf_link_down()`, `brcmf_bss_connect_done()`, `brcmf_bss_roaming_done()`, and `brcmf_notify_connect_status()` keep firmware, netdev carrier, SME bits, and cfg80211 notifications synchronized.
  - `brcmf_set_wpa_version()`, `brcmf_set_auth_type()`, `brcmf_set_wsec_mode()`, `brcmf_set_key_mgmt()`, `brcmf_set_sharedkey()`, and exported `brcmf_set_wsec()` program firmware security iovars.
  - Key ops `brcmf_cfg80211_add_key()`, `brcmf_cfg80211_del_key()`, `brcmf_cfg80211_get_key()`, `brcmf_cfg80211_config_default_key()`, and `brcmf_cfg80211_config_default_mgmt_key()` translate cfg80211 key operations to firmware `wsec_key` state.
- AP and management frames:
  - `brcmf_cfg80211_start_ap()` programs AP/GO channel, beacon interval, DTIM, 11d, security, firmware authenticator offload, SSID, hidden SSID, vendor IEs, carrier state, and AP-created bit.
  - `brcmf_cfg80211_stop_ap()` unwinds AP/GO state, clears firmware auth material, disables BSS/AP mode, restores regulatory/ARP/MPC state, and clears saved management IEs.
  - `brcmf_config_ap_mgmt_ie()`, `brcmf_vif_set_mgmt_ie()`, `brcmf_vif_clear_mgmt_ies()`, `brcmf_parse_vndr_ies()`, and `brcmf_vndr_ie()` manage firmware vendor IE add/delete commands and per-vif cached IE buffers.
  - Exported `brcmf_cfg80211_mgmt_tx()` handles probe responses and action frame TX through P2P helpers and reports TX status.
- Scheduled scan, PNO, and WoWLAN:
  - `brcmf_cfg80211_sched_scan_start()` and `brcmf_cfg80211_sched_scan_stop()` integrate PNO scheduled scanning.
  - `brcmf_notify_sched_scan_results()` converts PNO events into internal escans so cfg80211 receives full BSS data.
  - `brcmf_cfg80211_suspend()`, `brcmf_cfg80211_resume()`, `brcmf_configure_wowl()`, `brcmf_report_wowl_wakeind()`, and `brcmf_wowl_nd_results()` coordinate WoWLAN patterns, magic/disconnect/net-detect wakeups, GTK failure reporting, ARP/ND offload, bus WoWLAN state, and scheduled scan event rerouting.
- Wiphy setup and lifecycle:
  - `brcmf_cfg80211_get_ops()` returns a mutable copy of `brcmf_cfg80211_ops`, optionally removing `update_connect_params` when roaming is disabled.
  - `brcmf_cfg80211_attach()` allocates `cfg`, creates the primary station vif, initializes private memory and event handlers, builds wiphy capabilities, registers the wiphy, activates firmware events, and attaches P2P/BT coexistence/PNO.
  - `brcmf_cfg80211_detach()` detaches PNO/BT coexistence, unregisters wiphy, aborts scanning, frees buffers, cancels scan timeout work, frees wiphy allocations, and frees `cfg`.
  - `brcmf_setup_wiphy()`, `brcmf_setup_ifmodes()`, `brcmf_setup_wiphybands()`, `brcmf_construct_chaninfo()`, `brcmf_enable_bw40_2g()`, and HT/VHT helpers derive advertised capabilities from firmware features and channel lists.
- Event handlers:
  - `brcmf_register_event_handlers()` registers firmware event callbacks for link, deauth, disassoc, assoc, roam, MIC, set-SSID, PFN, IF, P2P management, action TX/RX, PSK supplicant, RSSI, plus firmware-vendor-specific handlers.
  - `brcmf_notify_vif_event()` synchronizes firmware IF add/delete/change events with vif creation/removal waiters.
  - `brcmf_notify_rssi()`, `brcmf_notify_mic_status()`, and `brcmf_notify_tdls_peer_event()` report CQM, MIC failure, and TDLS peer changes.
- Regulatory and survey:
  - `brcmf_cfg80211_reg_notifier()` translates ISO3166 alpha2 codes through platform country-code mappings and updates firmware `"country"`.
  - `brcmf_cfg80211_dump_survey()` drives firmware OBSS measurement through `"dump_obss"` for survey data when supported.

## Control Flow
Attach flow:
1. `brcmf_cfg80211_attach()` receives the already allocated `wiphy`, primary netdev, cfg80211 ops, and P2P policy.
2. It allocates `struct brcmf_cfg80211_info`, initializes the vif list and vif-event waitqueue/spinlock, allocates the primary station vif, links it to the netdev, and calls `wl_init_priv()`.
3. `wl_init_priv()` allocates private buffers (`conf`, `extra_buf`, WoWLAN net-detect structures, escan buffer), registers firmware event handlers, initializes mutexes/timers/work, and initializes default WMM priority and config values.
4. Attach queries D11 I/O type, attaches D11 chanspec helpers, assigns `drvr->config`, builds wiphy modes/capabilities/bands/regulatory data, registers wiphy, activates firmware events, then attaches P2P, BT coexistence, and PNO modules.
5. Feature-dependent callbacks such as GTK rekey data and dump survey are added to the mutable ops copy before registration.

Operational up/down flow:
1. `brcmf_cfg80211_up()` takes `cfg->usr_sync`, sets `BRCMF_VIF_STATUS_READY`, and calls `brcmf_config_dongle()`.
2. `brcmf_config_dongle()` brings firmware up, sets scan timings, applies power save, roaming, current interface type, ARP/ND offload, frameburst/fakefrag behavior, and marks `cfg->dongle_up`.
3. `brcmf_cfg80211_down()` takes the same mutex, calls `brcmf_link_down()` when ready, waits for supplicant-visible events to settle, aborts scanning, and clears READY.

Scan flow:
1. `brcmf_cfg80211_scan()` rejects scans when the vif is not ready, scanning is busy/aborting/suppressed, or a connect is in progress.
2. It saves the cfg80211 scan request, sets `BRCMF_SCAN_STATUS_BUSY`, prepares P2P scan state, applies probe-request vendor IEs, selects the primary interface for P2P-device scans, and runs `brcmf_do_escan()`.
3. `brcmf_cfg80211_escan_handler()` receives partial results, validates event lengths and BSS counts, filters unsupported IBSS results, merges duplicate BSS entries while preserving stronger/on-channel RSSI, and appends results to the escan buffer.
4. On final status or timeout worker, BSS entries are reported to cfg80211 and `brcmf_notify_escan_complete()` clears request/timer/state and calls either `cfg80211_scan_done()` or `cfg80211_sched_scan_results()`.

Connection flow:
1. `brcmf_cfg80211_connect()` validates SSID/readiness, pushes WPA/RSN IE to firmware for normal station connections, saves association-request vendor IEs, sets CONNECTING, derives chanspec, configures WPA/auth/wsec/AKM/MFP/shared WEP, and enables firmware supplicant or SAE/PSK offload when requested.
2. It allocates an extended join command containing SSID, BSSID, optional channel, dwell/probe timings, and join preferences. If the `"join"` iovar fails it falls back to `BRCMF_C_SET_SSID`.
3. Firmware events then drive `brcmf_is_linkup()`, `brcmf_is_linkdown()`, and `brcmf_is_nonetwork()`. Success gathers assoc IEs and BSS info, sets CONNECTED, reports `cfg80211_connect_done()`, and raises carrier. Failures clear handshake bits and report auth timeout.
4. Roam events call `brcmf_bss_roaming_done()` to refresh assoc IE/BSS/channel data and report `cfg80211_roamed()`.

AP flow:
1. `brcmf_cfg80211_start_ap()` extracts SSID from settings or beacon head, disables MPC/ARP-ND for primary AP, applies 11d, beacon, DTIM, AP mode, channel, interface up, firmware PSK/SAE authenticator state, security derived from beacon WPA/RSN IEs, and any saved WEP key.
2. It creates the AP with `BRCMF_C_SET_SSID` or enables P2P GO BSS, sets hidden-SSID `"closednet"`, programs beacon/probe/assoc-response vendor IEs, sets AP_CREATED, and raises carrier.
3. Stop AP sleeps briefly for deauth processing, clears firmware auth material, disables BSS/AP/MBSS as appropriate, restores regulatory state and ARP/ND/MPC, clears saved IEs, clears AP_CREATED, and drops carrier.

Suspend/resume flow:
1. Suspend stops PNO, aborts scans, then either disassociates ready vifs with no WoWLAN config or calls `brcmf_configure_wowl()`.
2. WoWLAN configuration disables ARP/ND offload if needed, saves PM mode, enables PM_MAX, configures wake patterns/net-detect/GTK failure, reroutes PFN NET_FOUND to the WoWLAN handler, writes wakeind clear/wowl/wowl_activate, informs the bus, and starts keepalive.
3. Resume reports wake indications, clears firmware WoWLAN state and patterns, restores ARP/ND and PM mode, stops net-detect scheduled scan, and restores PFN NET_FOUND event handling.

## State And Persistence Behavior
Most state is runtime-only and held in `struct brcmf_cfg80211_info` and `struct brcmf_cfg80211_vif`:
- `cfg->scan_request`, `cfg->scan_status`, `cfg->escan_info`, `cfg->int_escan_map`, `cfg->escan_timeout`, and `cfg->escan_timeout_work` persist scan-in-progress state and escan results until completion, abort, timeout, or detach.
- `cfg->usr_sync` serializes up/down paths; `cfg->dongle_up`, `cfg->pwr_save`, `cfg->channel`, and `cfg->ibss_starter` remember current configuration preferences.
- `cfg->pmk_list` caches PMKID entries for older firmware paths; PMKID v3 bypasses this list and sends per-operation structures.
- `cfg->conn_info` owns dynamically allocated association request/response IE copies. They are refreshed on connect/roam and freed by `brcmf_clear_assoc_ies()`.
- `cfg->vif_list` tracks all virtual interfaces. Each vif carries `sme_state` bits, `profile`, saved management IEs, management TX completion/status fields, MBSS flag, 11d snapshot, and CQM RSSI thresholds.
- `cfg->wowl` stores suspend-time WoWLAN state: active flag, previous PM mode, net-detect match buffers, waitqueue/completion flag, and net-detect enable state.
- Firmware state is extensively mutated through `brcmf_fil_*` calls: security iovars, join/AP commands, channel/chanspecs, country code, PM/MPC, PNO/WoWLAN, AP isolation, key material, PMKSA, TDLS, and BSS enablement.

There is no file persistence. State that must survive reset or suspend is either restored from in-memory cfg/vif fields or queried again from firmware. Detach unregisters wiphy, aborts scan work, frees buffers, and releases heap allocations but does not free the `wiphy` object itself beyond brcmfmac-owned dynamic subfields.

## Dependencies And Integration Points
- Kernel wireless APIs: `<net/cfg80211.h>`, cfg80211 ops, wiphy registration, cfg80211 scan/connect/roam/disconnect/AP/station/WoWLAN notifications, regulatory notifier, survey info, and CQM RSSI events.
- brcmfmac core/protocol layers: `core.h`, `proto.h`, `fwil.h`, `fwil_types.h`, `feature.h`, `fwsignal.h`, `vendor.h`, `common.h`, `fwvid.h`, and `bus.h`.
- P2P, PNO, and BT coexistence modules: `p2p.h`, `pno.h`, and `btcoex.h` provide add/delete vif, scan prep, action frame, remain-on-channel, scheduled scan, attach/detach, and Bluetooth coexistence controls.
- Firmware event handling: `brcmf_fweh_register()`, `brcmf_fweh_unregister()`, `brcmf_fweh_activate_events()`, and event codes such as `BRCMF_E_ESCAN_RESULT`, `BRCMF_E_LINK`, `BRCMF_E_IF`, `BRCMF_E_PFN_NET_FOUND`, `BRCMF_E_RSSI`, and P2P action/probe events.
- Bus integration: cfg80211 checks `drvr->bus_if->state` and `fwvid`, calls `brcmf_bus_wowl_config()` on suspend/resume, and relies on bus/core readiness before firmware iovars are safe.
- D11/chanspec helpers: `brcmu_d11_attach()`, `encchspec`, and `decchspec` translate between cfg80211 channel definitions and firmware chanspec encodings.

## Risks
- Scan state is split across a timer, work item, event handler, `cfg->scan_request`, and bit flags. Race handling relies on clearing `cfg->scan_request` before firmware aborts and on checking BUSY/ABORT/SUPPRESS bits consistently.
- Several firmware event handlers trust the event payload after length checks specific to each event. Any missed datalen validation around firmware-controlled structures could cause malformed-event handling bugs.
- Firmware offload state is complex: PSK, SAE, 1X, FT, MFP, AP authenticator offload, and supplicant offload all manipulate profile bits and firmware iovars. Incorrect ordering can leave keys or PMKs resident in firmware after disconnect/stop AP.
- Management IE handling caches only parsed vendor IEs and has fixed buffer limits (`IE_MAX_LEN`, `WL_EXTRA_BUF_MAX`, `VNDR_IE_PARSE_LIMIT`). Oversized or numerous IEs can be rejected or partially processed.
- AP startup has many firmware-version and feature-dependent branches (`MBSS`, `RSDB`, `MCHAN`, APSTA, 11d, P2P GO). Regressions can affect only certain chip/firmware combinations.
- Regulatory handling depends on platform country-code tables or fallback for selected chips. Missing tables on devices without fallback rejects country updates.
- Detach order matters: event handlers, timeout work, P2P/PNO/BT modules, wiphy registration, vif memory, and buffers all reference `cfg`; missed cancellation or late firmware events can become use-after-free risks.
- `brcmf_cfg80211_get_key()` reports AES firmware state as `WLAN_CIPHER_SUITE_AES_CMAC` even when CCMP may be the data cipher, reflecting a coarse firmware `wsec` bitmap and potentially surprising callers.

## Test Signals
- Build coverage should include PM and non-PM kernels, MFP/no-MFP, PNO/WoWLAN, P2P, TDLS, MBSS, RSDB/MCHAN, and SDIO/USB/PCIe bus combinations.
- Wiphy registration tests should inspect advertised interface modes, interface combinations, bands, HT/VHT caps, cipher suites, WoWLAN flags, ext features, and vendor commands against firmware feature bits.
- Scan tests should cover normal scan completion, duplicate BSS merge, P2P-device scan routing, abort during connect/suspend, timeout worker, scheduled-scan PNO conversion, and scan suppression during critical protocol.
- Station tests should cover open/WEP/WPA/WPA2/WPA3-SAE, PSK offload, SAE password offload, 1X PMK set/delete, FT roam, MFP required/capable, no-network failure, disconnect, firmware roam, and bus-down link handling.
- AP tests should cover AP and P2P GO startup/stop, hidden SSID, MBSS secondary AP, beacon/probe/assoc-response IEs, WEP reconfiguration after firmware down/up, AP isolation, station authorize/deauthorize, and station add/delete notifications.
- Power-management tests should cover suspend without WoWLAN, suspend with magic/disconnect/pattern/net-detect/GTK failure, wake indication reporting, PFN event handler rerouting/restoration, and bus WoWLAN callback behavior.
- Regulatory/survey tests should cover ISO3166 validation, platform country-code table lookup, fallback chips, firmware rejection, band/channel recomputation, OBSS survey busy/rx/tx accounting, and survey rejection while connected.
- Failure injection should target allocation failures in attach, escan buffer allocation, internal scan request allocation, `wiphy_register()` failure, firmware iovar failures, and interface event timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.h

## Purpose
`cfg80211.h` declares brcmfmac's cfg80211-facing state model, constants, inline conversion helpers, and public functions implemented by `cfg80211.c`. It is the local interface between the brcmfmac core, P2P/PNO/BT coexistence helpers, bus-aware code, and the cfg80211 operations layer.

The header captures the in-memory objects that persist wireless configuration state: global cfg80211 state, per-vif SME/profile state, saved management IEs, escan state, virtual-interface event synchronization, and WoWLAN net-detect state.

## Important APIs, Types, And Functions
- Size and timing constants:
  - `BRCMF_SCAN_IE_LEN_MAX`, `WL_NUM_SCAN_MAX`, `WL_TLV_INFO_MAX`, `WL_BSS_INFO_MAX`, `WL_ASSOC_INFO_MAX`, `WL_EXTRA_BUF_MAX`, `BRCMF_ESCAN_BUF_SIZE`, and `BRCMF_ESCAN_TIMER_INTERVAL_MS` constrain scan, BSS, assoc, and command buffers.
  - `WL_ROAM_TRIGGER_LEVEL`, `WL_ROAM_DELTA`, `BRCMF_DEFAULT_BCN_TIMEOUT_ROAM_ON`, and `BRCMF_DEFAULT_BCN_TIMEOUT_ROAM_OFF` set roaming defaults.
  - `BRCMF_VIF_EVENT_TIMEOUT` defines vif firmware-event wait time.
- WME/EDCF constants:
  - Access categories `AC_BE`, `AC_BK`, `AC_VI`, `AC_VO`, `EDCF_AC_COUNT`, and `MAX_8021D_PRIO`.
  - Bit masks/shifts for ACI, ACM, ECW, and AIFSN fields are used to derive firmware/WMM priority mapping.
- Vendor IE flags:
  - `BRCMF_VNDR_IE_BEACON_FLAG`, `PRBRSP`, `ASSOCRSP`, `AUTHRSP`, `PRBREQ`, `ASSOCREQ`, custom, and P2P action-frame flags identify the firmware packet classes for vendor IE add/delete commands.
- Scan and SME enums:
  - `enum brcmf_scan_status` defines bit indices for busy, abort, and suppress.
  - `enum brcmf_profile_fwsup` tracks station supplicant offload mode: none, PSK, 1X, or SAE.
  - `enum brcmf_profile_fwauth` tracks AP authenticator offload mode: none, PSK, or SAE.
  - `enum brcmf_mgmt_tx_status` tracks management TX completion/ack/off-channel state.
  - `enum brcmf_vif_status` defines vif SME bits: ready, connecting, connected, disconnecting, AP created, EAP success, assoc success.
  - `enum wl_escan_state` tracks idle/scanning for escan.
- Core structs:
  - `struct brcmf_cfg80211_conf` stores frag/RTS/retry thresholds.
  - `struct brcmf_cfg80211_security` stores current WPA versions, auth type, pairwise cipher, and group cipher.
  - `struct brcmf_cfg80211_profile` stores BSSID, security, default keys, firmware supplicant/authenticator choices, and FT state.
  - `struct vif_saved_ie` stores per-vif probe request, probe response, beacon, association request, and association response IEs with lengths.
  - `struct brcmf_cfg80211_vif` combines a lower `brcmf_if`, `wireless_dev`, profile, SME bits, saved IEs, list node, management TX completion/status/id/rx registration, MBSS/11d state, and CQM RSSI thresholds.
  - `struct brcmf_cfg80211_connect_info` stores heap-owned association request and response IEs for cfg80211 notifications.
  - `struct escan_info` stores escan state, buffer, owning wiphy/interface, and scan runner callback.
  - `struct brcmf_cfg80211_vif_event` stores the waitqueue, spinlock, firmware action, and target vif used to synchronize firmware IF events.
  - `struct brcmf_cfg80211_wowl` stores suspend/resume WoWLAN state, previous PM mode, net-detect match data, waitqueue, completion flag, and enable flag.
  - `struct brcmf_cfg80211_info` is the global cfg80211 state object containing wiphy, config, P2P/BT/PNO modules, current scan and connection state, PMK list, scan flags, public driver pointer, buffers, escan timer/work, vif list/event, WoWLAN state, D11 helpers, assoc list, and WMM priority mapping.
  - `struct brcmf_tlv` is the generic 802.11 TLV header used by IE parsing.
- Inline conversion helpers:
  - `cfg_to_wiphy()`, `wiphy_to_cfg()`, `wdev_to_cfg()`, `wdev_to_vif()`, `cfg_to_ndev()`, `ndev_to_cfg()`, `ndev_to_prof()`, `ndev_to_vif()`, and `cfg_to_conn()` centralize container and private-data conversions.
- Public functions:
  - Lifecycle: `brcmf_cfg80211_attach()`, `brcmf_cfg80211_detach()`, `brcmf_cfg80211_get_ops()`, `brcmf_cfg80211_up()`, and `brcmf_cfg80211_down()`.
  - Vif management: `brcmf_alloc_vif()`, `brcmf_free_vif()`, `brcmf_cfg80211_free_vif()`, vif event arm/wait helpers, and `brcmf_get_vif_state_any()`.
  - Scan/AP/security helpers: `brcmf_notify_escan_complete()`, `brcmf_abort_scanning()`, `brcmf_vif_set_mgmt_ie()`, `brcmf_vif_clear_mgmt_ies()`, `channel_to_chanspec()`, `brcmf_set_mpc()`, `brcmf_is_apmode_operating()`, `brcmf_set_wsec()`, and `brcmf_cfg80211_mgmt_tx()`.

## Control Flow
The header supports these primary flows:
- Attach/setup flow: core code obtains ops with `brcmf_cfg80211_get_ops()`, calls `brcmf_cfg80211_attach()`, and stores the returned `struct brcmf_cfg80211_info` in `drvr->config`. The structures declared here then become the shared state for cfg80211 operations and firmware event callbacks.
- Netdev up/down flow: core netdev paths call `brcmf_cfg80211_up()` and `brcmf_cfg80211_down()`, which use the `brcmf_cfg80211_info` mutex and vif SME bits declared here.
- Vif flow: interface creation allocates `struct brcmf_cfg80211_vif`, links it into `cfg->vif_list`, arms `cfg->vif_event`, and waits for a firmware IF event to fill `vif->ifp`/`wdev.netdev`.
- Scan flow: cfg80211 scan state is tracked with `cfg->scan_request`, `cfg->scan_status`, `cfg->escan_info`, timer/work, and `BRCMF_SCAN_STATUS_*` bits.
- Connect/AP flow: per-vif `profile`, `saved_ie`, and `sme_state` carry security, connection, AP-created, and management IE state across cfg80211 calls and firmware events.
- Suspend/resume flow: `cfg->wowl` retains WoWLAN active state, saved PM mode, and net-detect results until resume reports wakeup data and restores normal handlers.

## State And Persistence Behavior
The header defines in-memory state only. Nothing in `cfg80211.h` writes persistent storage, but it establishes what `cfg80211.c` preserves across operations:
- Global cfg state persists from attach to detach and owns buffers for command scratch space, escan aggregation, assoc IE copies, PMK lists, WoWLAN net-detect data, and module state.
- Per-vif state persists until virtual interface removal. It stores SME bit state, saved vendor IEs, current keys, security profile, management TX state, MBSS role, 11d setting snapshot, and RSSI thresholds.
- Saved management IEs and association IEs are duplicated into driver-owned memory so that later update/delete commands and cfg80211 notifications can use stable data after caller-owned buffers are gone.
- WoWLAN state persists across suspend/resume only in RAM; the previous PM mode and net-detect match data are restored or reported on resume.

All firmware persistence is indirect. Fields here are mirrored to firmware by `cfg80211.c` through `brcmf_fil_*` calls, and they must be kept coherent with firmware events.

## Dependencies And Integration Points
- Includes `brcmu_d11.h` for chanspec encode/decode helpers, `core.h` for `brcmf_pub`/`brcmf_if`, `fwil_types.h` for firmware command structures, and `p2p.h` for P2P state embedded in `brcmf_cfg80211_info`.
- Exposes cfg80211-facing types such as `struct wiphy`, `struct wireless_dev`, `struct net_device`, `struct cfg80211_scan_request`, `struct cfg80211_ops`, and `enum nl80211_iftype`.
- Integrates with PNO and BT coexistence through embedded pointers `struct brcmf_pno_info *pno` and `struct brcmf_btcoex_info *btcoex`.
- Integrates with firmware events through `brcmf_cfg80211_vif_event`, scan status bits, and public helpers that event callbacks call.
- Integrates with the common bus/core layer through `brcmf_cfg80211_attach()`, up/down helpers, MPC control, and `brcmf_is_apmode_operating()`.

## Risks
- Buffer constants are security-sensitive. Increasing accepted IE or scan sizes without matching firmware and allocation limits can overflow firmware command buffers; decreasing them can break valid user configurations.
- `struct brcmf_cfg80211_info` is shared across cfg80211 calls, firmware event callbacks, timers, and workqueues. Callers must honor locking and lifecycle ordering from the implementation.
- `sme_state` and `scan_status` are bitfields using enum values as bit indices. Reordering enum entries or treating them as values rather than bit positions would corrupt state checks.
- Inline conversion helpers assume netdev/wdev/private-data pointers are initialized according to brcmfmac conventions. Calling them during partial attach/detach can dereference incomplete state.
- `vif_saved_ie` has fixed `IE_MAX_LEN` arrays for several management frame classes. Firmware/user inputs larger than those arrays must be rejected before copying.
- `brcmf_cfg80211_wowl` uses waitqueue/completion-style state for net-detect data; resume paths must avoid stale `nd_data_completed` or stale handler routing.

## Test Signals
- Compile coverage should catch structure/API drift between this header and `cfg80211.c`, `p2p.c`, `pno.c`, `btcoex.c`, and core netdev code.
- Attach/detach tests should verify all allocated members represented in `struct brcmf_cfg80211_info` are initialized, used, and freed exactly once.
- Vif lifecycle tests should validate `brcmf_cfg80211_vif_event` wait/arm behavior, list membership, netdev private data, and cleanup for station/AP/P2P/monitor interfaces.
- Scan/connect/AP tests should inspect `sme_state`, `scan_status`, saved IE lengths, profile security fields, and WoWLAN fields before and after success, failure, abort, suspend, and detach.
- Static analysis should watch fixed-size arrays (`saved_ie`, `dcmd_buf`, `extra_buf`, escan buffer, PMK list, assoc list) and inline helper dereferences for bounds and lifetime assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.h -->
