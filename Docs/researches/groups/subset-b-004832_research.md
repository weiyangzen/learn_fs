# Research: subset-b-004832

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/ftm-initiator.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/ftm-initiator.c

## Purpose

`ftm-initiator.c` implements the Intel iwlwifi MVM Fine Timing Measurement initiator path used by cfg80211 peer measurement requests. It translates `cfg80211_pmsr_request` FTM peers into firmware `TOF_RANGE_REQ_CMD` variants, tracks one active request, receives firmware range notifications, reports `cfg80211_pmsr_result` objects back to mac80211/cfg80211, stores optional LCI/civic location reports, and supports 802.11az/PASN secured ranging material.

## Important APIs, Types, And Functions

- `struct iwl_mvm_loc_entry` stores per-peer LCI and civic report payloads received separately from range results.
- `struct iwl_mvm_smooth_entry` stores per-peer RTT smoothing history.
- `struct iwl_mvm_ftm_pasn_entry` stores PASN/11az HLTK, TK, cipher, and RX/TX packet numbers used for secured ranging.
- `iwl_mvm_ftm_start()` is the public start entry point. It rejects concurrent requests with `-EBUSY`, selects the firmware command version, sends the request, and records `mvm->ftm_initiator.req` plus `req_wdev` on success.
- `iwl_mvm_ftm_abort()` clears local state and sends `TOF_RANGE_ABORT_CMD` for the active request.
- `iwl_mvm_ftm_restart()` fails every outstanding peer result and completes the cfg80211 request during firmware restart.
- `iwl_mvm_ftm_range_resp()` parses versioned firmware range notifications, maps firmware status to cfg80211 status/failure reasons, updates per-peer burst counters and PASN PNs, applies smoothing, attaches LCI/civic data, reports results, and completes the request on final notification.
- `iwl_mvm_ftm_lc_notif()` parses FTM action-frame measurement-report IEs and queues LCI/civic blobs for later result reporting.
- `iwl_mvm_ftm_initiator_smooth_config()` and `iwl_mvm_ftm_initiator_smooth_stop()` initialize and tear down smoothing state.

## Control Flow

The command-building path starts in `iwl_mvm_ftm_start()`. Firmware capability `IWL_UCODE_TLV_API_FTM_NEW_RANGE_REQ` chooses the old v5 layout or the newer versioned command. For new API firmware, `iwl_fw_lookup_cmd_ver()` dispatches to `iwl_mvm_ftm_start_v7()`, `_v8()`, `_v9()`, `_v11()`, `_v12()`, `_v13()`, or `_v14()`; version 15 reuses the v14 layout. Each version initializes common request fields, then iterates peers and fills the matching AP entry structure.

Per-peer helpers convert cfg80211 channel definitions to firmware channel, bandwidth, format, and control-channel position fields. Later versions add HE/160 MHz handling, trigger/non-trigger flags, BSS color, band, NDP parameters, non-trigger timing bounds, PMF/secure-LTF decisions, and station ID binding for associated AP peers. `iwl_mvm_ftm_set_secured_ranging()` looks up PASN material only for trigger-based or non-trigger-based measurements and marks the AP entry as secured when key material is available.

The notification path starts when `iwl_mvm_ftm_range_resp()` receives a firmware packet while `mvm->mutex` is held. It derives the response version, validates packet length and request ID, loops through AP result entries, locates the original peer by BSSID, fills a cfg80211 result, reports it, and increments `mvm->ftm_initiator.responses[peer_idx]`. The final-batch bit completes the cfg80211 request and calls `iwl_mvm_ftm_reset()`.

## State And Persistence

State is runtime-only and anchored in `mvm->ftm_initiator`: the active request pointer, request wdev, per-peer response counters, LCI/civic list, PASN list, and smoothing list. `iwl_mvm_ftm_reset()` clears active request state and frees LCI/civic entries, but PASN and smoothing lifetimes are managed separately. No state is persisted across driver reload; restart paths complete or fail active measurements before reset.

## Dependencies And Integration Points

The file depends on mac80211/cfg80211 PMSR and FTM data structures, iwlwifi firmware command definitions from the location API, MVM station/link state, firmware capability/version discovery, `iwl_mvm_send_cmd*()` command transport, and time synchronization via `iwl_mvm_get_sync_time()`. It integrates with key iteration for associated secured ranging, with debugfs override `ftm_unprotected`, and with cfg80211 through `cfg80211_pmsr_report()` and `cfg80211_pmsr_complete()`.

## Risks And Edge Cases

- The implementation supports many firmware command/notification layouts; mismatched command version, structure size, or capability gating can silently break ranging on one firmware generation.
- Only one active request is allowed, so stale `mvm->ftm_initiator.req` state blocks future measurements.
- Secured ranging depends on PASN list contents, station lookup, cipher translation, and PN updates; missing keys can leave a trigger-based request unprotected or fail firmware validation.
- `iwl_mvm_ftm_get_host_time()` converts GP2 timestamps with wrap handling; incorrect sync timing skews reported host time.
- LCI/civic notifications are stored in a list without deduplicating old entries for the same address, so repeated location reports can increase memory until reset.
- Smoothing intentionally rewrites RTT results under threshold rules, so regressions may appear as accuracy or stability changes rather than command failures.

## Test Signals

Useful signals include successful `iw phyX measurement ftm`/PMSR requests against multiple peers, old and new firmware command-version coverage, timeout/busy/rejected peer mapping, abort and firmware-restart completion behavior, LCI/civic inclusion when requested, PASN secured-ranging tests with PN rollover/update, and debug logs for `Range response received`, RTT confidence, request ID mismatches, and unsupported bandwidth errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/ftm-initiator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/ftm-responder.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/ftm-responder.c

## Purpose

`ftm-responder.c` implements the AP-side FTM responder support for iwlwifi MVM. It programs firmware responder channel/configuration state, optionally sends LCI/civic responder data, manages responder-side PASN internal stations and keys, restarts responder state after changes, and accumulates responder statistics from firmware notifications.

## Important APIs, Types, And Functions

- `struct iwl_mvm_pasn_sta` represents an internal PASN station plus key configuration used by secured responder operation.
- `struct iwl_mvm_pasn_hltk_data` packages peer address, cipher, and HLTK data for dynamic responder configuration v3.
- `iwl_mvm_ftm_start_responder()` is the public entry point. It validates AP mode, updates the PHY context for the current channel, sends responder configuration, and optionally sends dynamic LCI/civic config.
- `iwl_mvm_ftm_responder_cmd()` fills and sends `TOF_RESPONDER_CONFIG_CMD` with BSSID, channel, bandwidth/format, broadcast station ID, optional NDP parameters, BSS color, non-trigger timing, and band.
- `iwl_mvm_ftm_responder_dyn_cfg_cmd()` dispatches dynamic LCI/civic configuration to v2 or v3 command formats.
- `iwl_mvm_ftm_responder_clear()` removes all responder PASN stations and keys.
- `iwl_mvm_ftm_restart_responder()` clears PASN state and restarts responder configuration when the bss config still enables responder mode.
- `iwl_mvm_ftm_responder_stats()` converts firmware responder stats into cfg80211 aggregate counters.

## Control Flow

Responder startup requires `mvm->mutex`, `bss_conf->ftm_responder`, non-P2P AP mode, and active AP/IBSS state. The function snapshots the RCU channel context, updates the firmware PHY context through `iwl_mvm_phy_ctxt_changed()`, then sends the responder command. Command version controls field layout: versions 6-8 share size, version 9 adds BSS color and min/max measurement timing, version 10 adds band. Bandwidth conversion is split between old TOF bandwidth enum handling and newer location frame-format/bandwidth encoding; 160 MHz is accepted only for command version 9 or later.

Dynamic config v2 builds aligned LCI and civic measurement-report IE payloads in a second host-command data segment. Dynamic config v3 embeds fixed LCI/civic buffers and can additionally carry PASN station HLTK data when supplied. Responder cleanup walks `mvm->resp_pasn_list`, deletes PASN keys, removes station IDs through MLD or legacy station APIs, deallocates internal stations, and frees memory.

## State And Persistence

Responder enablement is driven by mac80211 `bss_conf->ftm_responder` and `ftmr_params`. Runtime PASN responder stations live in `mvm->resp_pasn_list` and are explicitly removed on clear/restart. Statistics accumulate in `mvm->ftm_resp_stats`; they are not persisted to disk. Firmware holds responder configuration until reconfigured, stopped by broader interface teardown, or reset.

## Dependencies And Integration Points

The file depends on cfg80211 channel definitions and FTM responder params, mac80211 AP bss config, MVM vif/link data for broadcast station IDs, PHY context programming, firmware location commands, PASN key helpers, MLD/legacy station-ID allocation APIs, and cfg80211 responder stats structures. It shares constants and bandwidth helpers with the FTM initiator path and uses the same firmware location API group.

## Risks And Edge Cases

- Responder mode is rejected outside active non-P2P AP mode; callers must synchronize AP state before enabling FTM responder.
- The RCU channel context is copied before firmware programming; mutex protection is expected to make subsequent changes safe.
- LCI/civic lengths are checked, but malformed semantic contents are passed through to firmware.
- Command-version gates for 160 MHz, NDP params, BSS color, and band are critical for firmware compatibility.
- `iwl_mvm_ftm_restart_responder()` ignores the return value from restart, so failures are visible only via logs and later behavior.
- PASN cleanup must stay matched with key/station allocation paths or responder restart can leak firmware station IDs or software key memory.

## Test Signals

Validation should include AP-mode FTM responder enablement, LCI/civic advertisement, 20/40/80/160 MHz bandwidth cases against matching firmware versions, responder restart during channel/context changes, PASN secured responder setup and cleanup, and cfg80211 responder stats updates for success, partial, failed, ASAP, non-ASAP, duplicate, unknown-trigger, and out-of-window cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/ftm-responder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/fw-api.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/fw-api.h

## Purpose

`fw-api.h` is the umbrella firmware API header for the iwlwifi MVM implementation. It centralizes inclusion of all MVM firmware command, notification, and data-structure headers so implementation files can include one stable header for firmware ABI definitions.

## Important APIs, Types, And Functions

The file defines no functions or data structures itself. Its important API surface is the include set: TDLS, MAC configuration, offload, context, time-event, datapath, PHY/config/system/alive/binding/command headers, coexistence, D3, filter, LED, MAC, NVM/regulatory, PHY context, power, rate scaling, RX, scan, smart FIFO, station, stats, location, TX, and RFI firmware APIs.

## Control Flow

There is no runtime control flow. Compile-time control is a conventional include guard `__fw_api_h__` wrapping the firmware API include list.

## State And Persistence

No state is declared or persisted. The header only exposes type and constant definitions from lower-level firmware API headers to source files that include it.

## Dependencies And Integration Points

This header is included by files such as `mac-ctxt.c` that need many firmware command layouts. It is tightly coupled to the `drivers/net/wireless/intel/iwlwifi/mvm/fw/api/` header tree and acts as an internal ABI aggregation point between MVM driver code and firmware command definitions.

## Risks And Edge Cases

- Include-order changes can expose missing dependencies in individual firmware API headers.
- Adding broad includes here increases rebuild scope and may hide which specific API a source file actually uses.
- Removing a header can break distant MVM sources that relied on the umbrella include instead of direct includes.

## Test Signals

The main signal is compile coverage of MVM sources that include `fw-api.h`. Header hygiene can be checked by building with warnings enabled and by ensuring firmware command users still resolve all structures, constants, and enum values after include changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/fw-api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/fw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/fw.c

## Purpose

`fw.c` owns MVM firmware bring-up, init/runtime/WoWLAN firmware loading, alive notification handling, NVM/PNVM setup, PHY calibration, regulatory/platform power configuration, debug/recovery setup, and the high-level `iwl_mvm_up()` sequence that makes the device usable after transport start. It is the central bridge between transport firmware lifecycle and higher-level mac80211 operation.

## Important APIs, Types, And Functions

- `struct iwl_mvm_alive_data` carries SKU ID values and alive validity from `UCODE_ALIVE_NTFY`.
- `iwl_mvm_load_ucode_wait_alive()` sets the current firmware image, starts firmware, waits for alive, records error table addresses and firmware versions, loads PNVM, initializes queue bookkeeping, marks firmware running, and flushes stale BSS data for legacy APIs.
- `iwl_run_init_mvm_ucode()` runs legacy INIT firmware calibration and NVM acquisition.
- `iwl_run_unified_mvm_ucode()` runs unified firmware init/NVM/PHY setup within the regular image.
- `iwl_mvm_load_rt_fw()` selects unified or split INIT+REGULAR flow and initializes paging.
- `iwl_mvm_up()` performs full runtime firmware startup and post-alive configuration.
- `iwl_mvm_load_d3_fw()` starts WoWLAN firmware and minimum D3 setup.
- Regulatory/power helpers include `iwl_mvm_sar_select_profile()`, `iwl_mvm_get_sar_geo_profile()`, `iwl_mvm_sar_geo_init()`, `iwl_mvm_ppag_send_cmd()`, `iwl_mvm_tas_init()`, `iwl_mvm_lari_cfg()`, `iwl_mvm_uats_init()`, and `iwl_mvm_sgom_init()`.
- Recovery/diagnostic entry points include `iwl_mvm_send_recovery_cmd()`, `iwl_mvm_mfu_assert_dump_notif()`, and `iwl_mvm_rx_mfuart_notif()`.

## Control Flow

Firmware load begins by starting transport hardware, selecting an image, registering notification waits, and calling `iwl_trans_start_fw()`. `iwl_alive_fn()` parses multiple alive-notification versions, extracts UMAC/LMAC debug pointers, SKU ID, IMR metadata, version data, and alive status. On timeout or invalid alive, the code prints security boot, power-domain, and program-counter diagnostics and may trigger firmware debug collection.

Legacy init uses INIT firmware first, reads or uploads NVM, handles RF-kill shortcuts, sends TX antenna and PHY configuration, waits for calibration/PHY DB notifications, stops the device, restarts hardware, and loads regular firmware. Unified init uses the regular image, sends `INIT_EXTENDED_CFG_CMD`, performs optional external NVM load, sends `NVM_ACCESS_COMPLETE`, sends PHY config, waits for init completion, and reads NVM once.

`iwl_mvm_up()` chains post-load configuration: shared memory, Smart FIFO, debug config, antenna and PHY DB, Bluetooth coexistence, SoC latency, LARI, RX queues/RSS, station mapping reset, DQA, auxiliary station, thermal/CTDP, LTR, power, MCC, scan config, recovery DB restore, time sync, PTP, PPAG, SAR/geographic SAR, SGOM, TAS, LED sync, UATS, RFI, and MEI state. Any fatal error jumps to `iwl_mvm_stop_device()`.

## State And Persistence

The file mutates `mvm->status`, `mvm->fwrt`, `mvm->nvm_data`, queue maps, firmware-to-mac station arrays, thermal/power state, debug state, regulatory runtime tables, error recovery buffers, and init flags. Persistent platform inputs come from ACPI/UEFI/BIOS tables, PNVM, NVM files, MEI, and firmware TLVs; the driver stores parsed results in runtime structures and sends them to firmware on each bring-up rather than writing persistent storage itself.

## Dependencies And Integration Points

It integrates with the transport layer (`iwl_trans_*`), firmware runtime/debug (`iwl_fwrt`, debug TLVs, PNVM), NVM parsing/loading, ACPI/UEFI regulatory and power tables, MEI, mac80211/cfg80211, RX queue configuration, scan, Bluetooth coexistence, thermal cooling, RFI, PTP, time sync, LED sync, and MVM station/PHY context helpers. Firmware command layout is heavily version- and capability-dependent.

## Risks And Edge Cases

- Startup sequencing is strict; moving NVM, PNVM, PHY config, calibration, paging, RX queue, or regulatory commands can break specific hardware families.
- Error paths must remove notification waits and restore the previous firmware image, otherwise later waits or state checks can see stale state.
- Many BIOS/ACPI tables are optional; unavailable data is often non-fatal, while inconsistent data such as WGDS without WRDS is logged.
- Command-version handling for SAR, geographic SAR, PPAG, TAS, LARI, and PHY config is dense and hardware dependent.
- RF-kill and CT-kill paths intentionally skip parts of setup; regressions may only occur under hardware switch, thermal, or restart conditions.
- Recovery command buffer ownership is transferred/freed in `iwl_mvm_send_recovery_cmd()`, so callers must not reuse it after sending.

## Test Signals

Key signals are clean boot on split and unified firmware families, RF-kill init/resume, WoWLAN firmware load, firmware restart recovery, valid NVM/PNVM loading, PHY calibration completion, RX queue/RSS setup, regulatory MCC/LARI/SAR/PPAG/TAS command logs, no alive timeout debug triggers, no station-map stale pointers after restart, and hardware-specific validation on AX210 and newer devices where product reset, IMR, UATS, and newer power tables apply.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/led.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/led.c

## Purpose

`led.c` registers and controls the iwlwifi MVM radio LED class device. It maps Linux LED brightness changes to either a firmware LED command on newer firmware or direct CSR register writes on older hardware, and synchronizes LED state after firmware startup.

## Important APIs, Types, And Functions

- `iwl_mvm_leds_init()` validates the module LED mode, allocates the LED name, initializes `mvm->led`, registers the class device, and sets `IWL_MVM_INIT_STATUS_LEDS_INIT_COMPLETE`.
- `iwl_led_brightness_set()` is the LED class callback and translates brightness to boolean on/off.
- `iwl_mvm_led_set()` selects firmware command control when `IWL_UCODE_TLV_CAPA_LED_CMD_SUPPORT` exists, otherwise writes `CSR_LED_REG`.
- `iwl_mvm_send_led_fw_cmd()` sends asynchronous `LEDS_CMD` only when firmware is running.
- `iwl_mvm_leds_sync()` reapplies brightness after firmware startup for firmware-controlled LEDs.
- `iwl_mvm_leds_exit()` unregisters and frees LED state.

## Control Flow

Initialization accepts default and RF-state modes, rejects unsupported modes, and treats blink mode as unsupported before falling back to RF-state behavior. Runtime brightness changes call the class callback, which calls the MVM LED setter. Firmware-controlled LEDs send an async command; register-controlled LEDs write directly. Sync is skipped if LEDs were not registered or if pre-8000 hardware uses direct register control.

## State And Persistence

State is limited to `mvm->led`, the dynamically allocated LED name, current LED brightness maintained by the LED subsystem, and `mvm->init_status`. There is no persistence; LED state is reissued after firmware startup when needed.

## Dependencies And Integration Points

The file depends on the Linux LED class subsystem, `iwlwifi_mod_params.led_mode`, mac80211 radio LED trigger names, firmware LED command definitions, CSR register access, firmware-running status, and MVM init status flags. `iwl_mvm_up()` calls `iwl_mvm_leds_sync()` near the end of firmware bring-up.

## Risks And Edge Cases

- Firmware LED commands are skipped when firmware is down, so sync after startup is necessary for command-controlled devices.
- Blink mode is explicitly unsupported, which may surprise users setting `led_mode=blink`.
- If LED registration fails, the allocated name must be freed; this file handles that path.
- Direct CSR LED writes are hardware-family sensitive and intentionally avoided for newer firmware-command devices.

## Test Signals

Validation includes LED class device registration under `/sys/class/leds`, RF-state trigger behavior, manual brightness toggles, firmware restart followed by LED sync, `led_mode=disable` producing no device, invalid LED mode returning `-EINVAL`, and absence of `LED command failed` warnings on firmware-controlled hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/link.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/link.c

## Purpose

`link.c` manages firmware link contexts for MVM's MAC configuration API, especially MLO-capable per-link state. It adds, modifies, deactivates, removes, and initializes per-vif link information, translating mac80211 `ieee80211_bss_conf` fields into `LINK_CONFIG_CMD` payloads.

## Important APIs, Types, And Functions

- `iwl_mvm_link_cmd_send()` is the local sender for `LINK_CONFIG_CMD` with add/modify/remove actions and standardized error logging.
- `iwl_mvm_set_link_fw_id()` assigns a firmware link ID; currently invalid links inherit the vif MAC ID.
- `iwl_mvm_add_link()` creates a firmware link context with MAC ID, link ID, local address, optional IBSS BSSID, invalid PHY ID, and listen LMAC for older command versions.
- `iwl_mvm_link_changed()` updates active state, PHY binding, local address, rates, protection, QoS, beacon/DTIM timing, HE/EHT parameters, BSS color, puncturing, nontransmitted-BSSID data, and link flags.
- `iwl_mvm_remove_link()` removes the firmware link context, invalidates the local firmware link ID, and updates Smart FIFO state.
- `iwl_mvm_disable_link()` deactivates then removes a link.
- `iwl_mvm_init_link()` initializes station IDs and SMPS request defaults for a link info object.

## Control Flow

Adding a link first ensures link info exists, assigns a firmware link ID, disables Smart FIFO if necessary, fills `LINK_CONFIG_CMD`, and sends `FW_CTXT_ACTION_ADD`. Modifying checks that the link exists and has a valid firmware ID, handles activation/deactivation bookkeeping, stops session protection on station deactivation, fills PHY/MAC/rate/protection/QoS/timing fields, conditionally encodes HE and EHT data, sends `FW_CTXT_ACTION_MODIFY`, and updates `link_info->active` only after a successful active-state change.

EHT puncturing is gated on command/PHY command version, module 11be disable flag, link EHT support, and available channel context. HE fields are skipped when HE is unsupported, disabled, or station mode is not associated. Removal sends `FW_CTXT_ACTION_REMOVE` and then attempts to restore Smart FIFO state.

## State And Persistence

The file mutates `struct iwl_mvm_vif_link_info`: `fw_link_id`, `active`, `phy_ctxt`, `csa_block_tx`, `listen_lmac`, queue parameters, `he_ru_2mhz_block`, station IDs, and SMPS request array. Firmware maintains the actual link context after commands are sent. Nothing is persisted beyond runtime driver state.

## Dependencies And Integration Points

It depends on MVM vif/link structures, mac80211 link/bss configuration, `MAC_CONF_GROUP` firmware commands, PHY context state, Smart FIFO updates, session protection, rate/protection/QoS helpers from `mac-ctxt.c`, module disable flags for 11ax/11be, and RCU channel-context access. It is a key integration point between mac80211 MLO link callbacks and firmware link contexts.

## Risks And Edge Cases

- Activating a link without a PHY context is treated as a no-op, which handles early removal but can hide sequencing bugs if callers expected activation.
- Link ID assignment currently aliases the vif ID for invalid links; future firmware with independent link ID allocation may need different handling.
- Smart FIFO update failure during add aborts binding because multiple bound MACs with SF enabled are forbidden.
- EHT puncturing behavior changes depending on PHY command version; wrong gates can send unsupported fields or omit required puncture masks.
- Deactivation must stop session protection and unblock CSA-blocked TX correctly to avoid stuck station traffic.

## Test Signals

Useful tests cover MLO and non-MLO link add/modify/remove, station link activation/deactivation, AP/IBSS BSSID handling, HE and EHT link changes, punctured-channel operation, Smart FIFO transitions with multiple links, CSA blocked-TX cleanup, and firmware logs for failed `LINK_CONFIG_CMD` actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mac-ctxt.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mac-ctxt.c

## Purpose

`mac-ctxt.c` manages legacy firmware MAC contexts and shared MAC-level helpers for iwlwifi MVM. It allocates MAC/TSF IDs, builds `MAC_CONTEXT_CMD` payloads for station, AP/GO, monitor, P2P device, and IBSS interfaces, prepares beacon templates, handles beacon/missed-beacon/stored-beacon/probe-response notifications, and coordinates channel-switch state with mac80211.

## Important APIs, Types, And Functions

- `iwl_mvm_ac_to_tx_fifo[]`, `iwl_mvm_ac_to_gen2_tx_fifo[]`, and `iwl_mvm_ac_to_bz_tx_fifo[]` map ACs to firmware TX FIFOs.
- `iwl_mvm_mac_ctxt_init()` allocates MAC and TSF IDs and initializes default link/time-event state.
- `iwl_mvm_mac_ctxt_add()`, `iwl_mvm_mac_ctxt_changed()`, and `iwl_mvm_mac_ctxt_remove()` are the public MAC context lifecycle entry points.
- `iwl_mvm_mac_ctxt_cmd_common()` fills shared MAC command fields: ID/color, type, TSF, addresses, basic rates, short preamble/slot, QoS, and protection flags.
- Per-type builders include `iwl_mvm_mac_ctxt_cmd_sta()`, `_listener()`, `_ibss()`, `_p2p_device()`, `_ap()`, and `_go()`.
- Shared helpers `iwl_mvm_set_fw_basic_rates()`, `iwl_mvm_set_fw_protection_flags()`, and `iwl_mvm_set_fw_qos_params()` are also used by link-context code.
- Beacon helpers include `iwl_mvm_mac_ctxt_beacon_changed()`, `iwl_mvm_mac_ctxt_send_beacon_v6()`, `_v7()`, `_v9()`, `iwl_mvm_mac_ctxt_set_tim()`, and rate/flag helpers.
- Notification handlers include `iwl_mvm_rx_beacon_notif()`, `iwl_mvm_rx_missed_beacons_notif()`, `iwl_mvm_rx_missed_beacons_notif_legacy()`, `iwl_mvm_rx_stored_beacon_notif()`, `iwl_mvm_probe_resp_data_notif()`, `iwl_mvm_channel_switch_start_notif()`, and `iwl_mvm_channel_switch_error_notif()`.

## Control Flow

MAC context initialization iterates active interfaces to reserve unused MAC IDs and compatible TSF IDs. TSF sharing is preferred between station and AP/GO interfaces when beacon intervals are divisor/multiple compatible, avoiding drift between related TBTT schedules. During resume/recovery, existing IDs are preserved if the iterator finds the vif already active.

Lifecycle commands route through `iwl_mvm_mac_ctx_send()` based on vif type. Station contexts set multicast acceptance, association timing, DTIM/TBTT values, listen interval, AID, P2P CT window, probe-request filters, HE filter, and TWT policy. AP/GO contexts set multicast FIFO, probe/beacon filters, beacon interval, DTIM interval, multicast queue, and stable beacon time; GO additionally sends CT window and opportunistic power-save state. Monitor mode enables promiscuous/control/beacon/probe/FCS filters and allocates a sniffer internal station. P2P device mode restricts receive filtering to probe requests and can enable extended discovery when another GO is active.

Beacon template updates get a beacon skb from mac80211 and choose firmware template version by capability/API. Older formats include TX command data and TIM/CSA offsets. Newer formats send rate flags, byte count, template/link ID, TIM, CSA/ECSA, optional broadcast TWT offset, and FILS discovery hints for APs on PSC or wide 6 GHz channels. Notifications update CSA countdowns, AP beacon GP2 time, IBSS manager state, missed-beacon loss decisions, stored beacon forwarding to mac80211 RX, P2P NoA/probe-response state, and channel-switch completion or disconnect.

## State And Persistence

The file mutates per-vif `struct iwl_mvm_vif` state: MAC ID, TSF ID, color, uploaded flag, AP/IBSS active fields, time-event data, AP beacon time, CSA countdown state, default link queues/stations, probe response RCU pointer, and counters. Global MVM state touched includes `csa_vif`, `csa_tx_blocked_vif`, `ap_last_beacon_gp2`, `ibss_manager`, sniffer station, hardware flags, and debug triggers. Firmware holds MAC contexts and beacon templates after commands; software state is runtime-only.

## Dependencies And Integration Points

This file sits between mac80211 vif/bss callbacks and firmware MAC commands. It depends on cfg80211/mac80211 interface types, rates, beacon generation, CSA helpers, RCU vif lookup, iwlwifi firmware context/filter/beacon/offload APIs, station allocation, Bluetooth coexistence TX priority, time-event CSA scheduling, debug triggers, and link-context helper reuse. `link.c` calls its rate/protection/QoS helpers for MLD link commands.

## Risks And Edge Cases

- MAC/TSF ID allocation is global across active interfaces; recovery/resume must preserve IDs to avoid firmware/mac80211 mismatches.
- Beacon template version gating is complex and tied to `IWL_UCODE_TLV_CAPA_CSA_AND_TBTT_OFFLOAD`, `IWL_UCODE_TLV_API_NEW_BEACON_TEMPLATE`, and command versions.
- `iwl_mvm_mac_ctxt_set_tim()` manually parses beacon IEs and warns if TIM is absent; malformed beacon templates can break power-save delivery.
- AP beacon scheduling intentionally offsets from an associated station TBTT using randomness; changes can affect multi-interface coexistence.
- Missed-beacon handling distinguishes consecutive misses with and without RX; wrong thresholds or notification version IDs can cause false disconnects or missed loss events.
- Probe-response NoA data uses RCU replacement; old data must be freed with `kfree_rcu()` to avoid use-after-free.
- CSA handling spans beacon TX notifications, delayed work, station TX blocking, and firmware error notifications, so partial failures can leave TX blocked or channel switch incomplete.

## Test Signals

Good coverage includes station association and reassociation, AP/GO/IBSS bring-up, monitor mode with FCS flag changes, P2P device discovery, multi-interface TSF sharing, beacon template updates across firmware versions, TIM and CSA/ECSA offset correctness, FILS beacon flags on 6 GHz/PSC channels, missed-beacon disconnect thresholds, stored beacon delivery into mac80211 RX, P2P NoA probe-response updates, and CSA start/error notifications for AP and station modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mac-ctxt.c -->
