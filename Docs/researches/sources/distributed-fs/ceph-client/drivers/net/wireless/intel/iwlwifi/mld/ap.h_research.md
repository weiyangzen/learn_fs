# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/ap.h

## Purpose

`ap.h` declares the AP/IBSS helper API implemented in `ap.c`, exposing beacon-template, AP lifecycle, early-key, rate-flag, and TIM-index helpers to the rest of MLD.

## Important APIs, Types, and Functions

The prototypes cover `iwl_mld_update_beacon_template()`, `iwl_mld_start_ap_ibss()`, `iwl_mld_stop_ap_ibss()`, `iwl_mld_store_ap_early_key()`, `iwl_mld_free_ap_early_key()`, `iwl_mld_get_rate_flags()`, `iwl_mld_set_tim_idx()`, and `iwl_mld_send_beacon_template_cmd()`.

## Control Flow

mac80211 AP/IBSS callbacks call the lifecycle functions. Debugfs beacon injection reuses rate, TIM, and beacon-send helpers. Key setup code uses early-key helpers when AP group-key installation precedes firmware broadcast/multicast station setup.

## State and Persistence Behavior

The header itself has no storage, but its functions mutate firmware beacon/link/station state and per-link AP early-key arrays.

## Dependencies and Integration Points

It includes MLD core/interface definitions and firmware TX API structures. Consumers must already hold the required wiphy/driver locks described by the implementation.

## Risks and Edge Cases

Prototype drift with `ap.c` and missing includes are the main header risks. Because helpers accept raw mac80211 pointers, callers must supply valid `vif` and `bss_conf` objects for the intended link.

## Test Signals

Build all consumers with AP, IBSS, debugfs, and key-management paths enabled. Static analysis should verify callers handle error returns from start/update/store helpers.
