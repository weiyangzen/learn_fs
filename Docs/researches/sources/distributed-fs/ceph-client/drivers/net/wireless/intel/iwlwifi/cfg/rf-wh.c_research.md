# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/rf-wh.c

## Purpose
`rf-wh.c` defines a WH RF configuration variant for Wi-Fi 7 devices where EHT support is disabled, plus product names for BE211/BE213/AX221 and Killer BE1775 variants. Comments note that regular `iwl_rf_wh` and `iwl_rf_wh_160mhz` are currently aliases for FM configs.

## Important APIs, Types, and Data
- `IWL_DEVICE_WH` macro: STBC, LDPC, 2.4/5 GHz HT40, RF-state LED, non-shared antenna B, VHT MU-MIMO, UHB, EHT RBD count, NVM 0x0a1d, extended NVM.
- `iwl_rf_wh_non_eht`: applies `IWL_DEVICE_WH` and explicitly sets `.eht_supported = false`.
- Product names: Killer BE1775s/i, Intel BE211, BE213, and AX221.

## Control Flow and Integration
PCI IDs can select `iwl_rf_wh_non_eht` for WH devices requiring UHB-capable but non-EHT behavior, while other WH variants may alias FM configs. Capability registration consumes the EHT-disabled flag and bandwidth/capability fields.

## State and Persistence Behavior
The file defines immutable config and strings only. Runtime capabilities derive from these fields and NVM contents.

## Dependencies and Integration Points
It depends on `iwl-config.h`. The Makefile includes it for `CONFIG_IWLMLD`.

## Risks and Edge Cases
The macro includes EHT-sized RBD count while `iwl_rf_wh_non_eht` disables EHT; this should be validated against transport expectations. Alias comments mean WH behavior is split across this file and FM definitions.

## Test Signals
Build MLD, probe WH non-EHT IDs, verify UHB without EHT capability exposure, RBD allocation behavior, extended NVM parsing, and product-name mapping. Also check alias-based WH variants still resolve correctly.
