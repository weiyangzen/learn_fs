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
