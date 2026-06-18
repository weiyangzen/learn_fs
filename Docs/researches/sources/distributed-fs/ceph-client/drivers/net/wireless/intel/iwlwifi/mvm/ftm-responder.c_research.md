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
