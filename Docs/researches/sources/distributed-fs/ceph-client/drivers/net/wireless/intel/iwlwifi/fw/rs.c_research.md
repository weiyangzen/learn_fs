# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/rs.c

## Purpose
Provides firmware rate-scaling formatting and lookup helpers. It translates firmware legacy rate indexes to PLCP values, exposes rate/MCS descriptive strings, formats `rate_n_flags` values for diagnostics, and detects HE short guard interval encodings.

## Important APIs, Types, and Functions
Tables include `fw_rate_idx_to_plcp`, `rate_mcs`, `ant_name`, and `pretty_bw`. Exported functions are `iwl_fw_rate_idx_to_plcp`, `iwl_rate_mcs`, `iwl_rs_pretty_ant`, `iwl_rs_pretty_bw`, `rs_pretty_print_rate`, and `iwl_he_is_sgi`.

## Control Flow
The lookup helpers index static arrays. `rs_pretty_print_rate()` decodes antenna, channel width, modulation type, MCS, NSS, SGI/NGI, STBC, LDPC, DCM, and beamforming. Legacy OFDM/CCK rates return early with Mbps text; HT/VHT/HE/EHT use unified formatting.

## State and Persistence Behavior
The file stores only immutable tables. Its output is diagnostic text and does not persist state or modify firmware behavior.

## Dependencies and Integration Points
Depends on mac80211 types, `fw/api/rs.h`, and rate constants from iwlwifi firmware APIs. It is used by debugfs/logging paths in MVM and firmware tracing.

## Risks
Inputs are assumed to be valid indexes in `iwl_fw_rate_idx_to_plcp()` and `iwl_rate_mcs()`, so callers must validate firmware indexes. `rs_pretty_print_rate()` must track new `RATE_MCS_*` encodings, especially EHT/320 MHz additions.

## Test Signals
Unit-style coverage for every legacy rate index, invalid antenna/bandwidth display, CCK/OFDM/HT/VHT/HE/EHT formatting, HE GI/LTF combinations, and buffer-size truncation behavior would catch most regressions.
