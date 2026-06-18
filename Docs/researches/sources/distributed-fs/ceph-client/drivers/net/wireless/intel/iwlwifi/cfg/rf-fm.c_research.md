# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/rf-fm.c

## Purpose
`rf-fm.c` defines FM RF configuration for BZ/GL/SC-era Wi-Fi 7 devices, including EHT/UHB capability, NVM version/type, RBD count, bandwidth-limited variant, product names, and core firmware declarations for several MAC/RF revision prefixes.

## Important APIs, Types, and Data
- Firmware prefixes: BZ FM B/C/FM4 and GL FM B/C variants.
- `IWL_DEVICE_FM` macro: STBC, LDPC, HT40 on 2.4/5 GHz, RF-state LED, non-shared antenna B, VHT MU-MIMO, UHB, EHT, EHT RBD count, NVM version 0x0a1d, extended NVM.
- RF configs: `iwl_rf_fm` and `iwl_rf_fm_160mhz` with `bw_limit = 160`.
- Product name strings for Killer BE1750/BE1790 and Intel BE200/BE201/BE202/BE401.
- `IWL_CORE_FW` declarations tied to `IWL_BZ_UCODE_CORE_MAX`.

## Control Flow and Integration
PCI ID tables pair these RF configs with BZ/GL/SC MAC configs. The selected RF config controls advertised PHY features, RBD sizing, NVM parsing, LED behavior, bandwidth limit, and firmware image prefix.

## State and Persistence Behavior
Immutable RF configuration only. Runtime capability state is derived by MVM/MLD from these fields and NVM contents.

## Dependencies and Integration Points
It depends on `iwl-config.h` and core firmware macros from the broader cfg build. It is included under `CONFIG_IWLMLD`.

## Risks and Edge Cases
The 160 MHz variant intentionally caps bandwidth despite EHT-capable defaults. Firmware prefixes share BZ core max, so core-version macro availability and include ordering matter. UHB/EHT flags must match regulatory/NVM support.

## Test Signals
Probe FM devices, confirm firmware alias availability, validate EHT/UHB capability exposure, RBD count, extended NVM parsing, bandwidth cap behavior for 160 MHz variants, and product-name mappings.
