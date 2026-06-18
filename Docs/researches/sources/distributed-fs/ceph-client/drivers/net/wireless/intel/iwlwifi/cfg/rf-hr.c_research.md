# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/rf-hr.c

## Purpose
`rf-hr.c` defines HR RF configuration for Wi-Fi 6 devices such as AX101/AX200/AX201/AX203 and multiple QU/SO/MA/BZ/SC MAC combinations. It sets firmware API 100, HE RBD count, extended NVM, bandwidth variants, SISO-diversity variant, product names, and firmware aliases.

## Important APIs, Types, and Data
- Firmware API range: HR API 100 only.
- Firmware prefixes for QU, QUZ, SO, MA, BZ, and SC HR combinations.
- `IWL_DEVICE_HR` macro: RF-state LED, non-shared antenna B, VHT MU-MIMO, STBC/LDPC, 2.4/5 GHz HT40, HE RBD count, NVM 0x0a1d, extended NVM, API min/max.
- RF configs: `iwl_rf_hr1` with TX SISO diversity, `iwl_rf_hr`, and `iwl_rf_hr_80mhz` with bandwidth cap.
- Product names for AX101, AX200, AX201, and AX203.

## Control Flow and Integration
PCI IDs combine HR RF configs with MAC configs. The firmware loader uses the relevant `MODULE_FIRMWARE` alias, while capability code consumes bandwidth caps, diversity, and HE/VHT flags.

## State and Persistence Behavior
The file is immutable. Runtime state is derived from config fields and NVM content during probe and capability registration.

## Dependencies and Integration Points
It depends on `iwl-config.h` and module firmware macros. It is included as an MVM RF config and shares newer firmware prefixes with BZ/SC MAC families.

## Risks and Edge Cases
The file defines both `IWL_SC_A_HR_A_FW_PRE` and `IWL_SC_A_HR_B_FW_PRE` to the same string, which should be intentional but is easy to misread. Bandwidth and SISO-diversity variants must be matched to correct SKU IDs. Firmware API 100 must remain compatible with MAC base configs.

## Test Signals
Probe HR variants, verify firmware aliases for each prefix, confirm bandwidth caps, SISO diversity behavior, HE RBD count, VHT MU-MIMO flags, NVM parsing, and product-name strings.
