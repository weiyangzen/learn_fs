# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/ftm-initiator.c

## Purpose

`ftm-initiator.c` implements cfg80211 peer measurement FTM initiator support for MLD. It converts PMSR requests into firmware TOF range commands, tracks one active request, translates firmware range responses into cfg80211 PMSR results, and completes or fails outstanding requests across firmware restart.

## Important APIs, Types, and Functions

Public functions are `iwl_mld_ftm_start()`, `iwl_mld_handle_ftm_resp_notif()`, and `iwl_mld_ftm_restart_cleanup()`. Local helpers fill common request fields, map channel definitions to firmware channel/format/BW/control position, set target flags, select associated AP station ID and PMF flag, fill per-target NDP/timing parameters, validate response request ID/count, find peers by BSSID, log results, and reset active state.

## Control Flow

Start rejects concurrent requests and oversized peer lists, fills the request cookie, timeout, randomized MAC template/mask, associated BSSID/TSF MAC ID if needed, and each AP target, then sends `TOF_RANGE_REQ_CMD`. On success it stores the request and wireless device. Firmware response notifications are validated against the active request, each AP entry is matched to a peer, status/failure reason/RTT/RSSI/TSF fields are converted into `cfg80211_pmsr_result`, reported to cfg80211, and response counters update burst indexes. The last report completes the cfg80211 request and clears state. Restart cleanup reports final failures for all peers and completes the request.

## State and Persistence Behavior

Persistent state lives in `mld->ftm_initiator`: active request pointer, requesting wireless device, and per-peer response counters. Request state is cleared on final batch or restart cleanup.

## Dependencies and Integration Points

The file depends on cfg80211 PMSR/FTM APIs, mac80211 VIF association state, MLD vif/station/PHY helpers, firmware location API, MLD constants for FTM defaults, and firmware capability checks for RTT confidence logging.

## Risks and Edge Cases

Only one active FTM request is supported. Unsupported channel widths fail the entire request. The request ID is truncated to `u8` for validation, so cookie collisions in low 8 bits are theoretically possible if firmware also truncates. Secured ranging and unprotected debugfs support are TODO. Host time currently uses boottime at notification processing rather than converted firmware timestamp.

## Test Signals

Test associated and unassociated requests, AP TSF reporting, 20/40/80/160 MHz targets, trigger and non-trigger based flags, PMF flag when associated with MFP, busy/no-response/timeout/success status conversion, multi-peer batching, final completion, concurrent request rejection, unknown BSSID handling, and restart cleanup failure reporting.
