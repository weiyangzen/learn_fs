# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/ftm-initiator.h

## Purpose

`ftm-initiator.h` declares the MLD FTM initiator state and entry points.

## Important APIs, Types, and Functions

`struct ftm_initiator_data` stores the active `cfg80211_pmsr_request`, requesting `wireless_dev`, and per-target response counters. Prototypes expose `iwl_mld_ftm_start()`, `iwl_mld_handle_ftm_resp_notif()`, and `iwl_mld_ftm_restart_cleanup()`.

## Control Flow

mac80211/cfg80211 operation code calls start for a PMSR request. Firmware notification dispatch calls the response handler. Restart/error handling calls cleanup to fail and complete any pending request.

## State and Persistence Behavior

The struct is embedded in MLD state and persists between request start and final completion or cleanup. Response counters survive across batches for periodic measurements.

## Dependencies and Integration Points

The header relies on cfg80211 PMSR and wireless device types plus firmware `IWL_TOF_MAX_APS` sizing through included MLD/location headers in users.

## Risks and Edge Cases

The active request pointer is non-owning; lifetime must be tied to cfg80211's request contract and cleared on all completion paths. `responses[]` must be sized consistently with firmware maximum AP entries.

## Test Signals

Build all FTM users, then exercise normal completion, partial batches, firmware restart cleanup, and rejection of a second request while `req` is non-NULL.
