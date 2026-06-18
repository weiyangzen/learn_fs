# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/rf-gf.c

## Purpose
`rf-gf.c` defines GF RF configuration for Wi-Fi 6E-generation AX210/AX211/AX411 and related SO/TY/MA/BZ/SC combinations, including firmware API 100, PNVM firmware declarations for several prefixes, UHB capability, HE RBD count, extended NVM, and product names.

## Important APIs, Types, and Data
- Firmware API range: GF API 100 only.
- Firmware prefixes for SO, TY, MA, BZ, and SC GF/GF4 combinations.
- `iwl_rf_gf`: UHB, RF-state LED, non-shared antenna B, VHT MU-MIMO, STBC/LDPC, 2.4/5 GHz HT40, NVM 0x0a1d, extended NVM, HE RBD count, API min/max.
- Product names for AX210/AX211/AX411 and Killer AX1675/AX1690 variants.
- Firmware declarations: `IWL_FW_AND_PNVM` for SO/TY/MA and `MODULE_FIRMWARE` for BZ/SC GF images.

## Control Flow and Integration
MAC configs such as AX210, BZ, and SC pair with this RF config. Firmware loader uses the prefix declarations and PNVM declarations where applicable. Capability registration uses the RF fields to expose 6 GHz/UHB and HT/VHT/HE behavior.

## State and Persistence Behavior
Only immutable RF config and names are defined. Runtime state includes parsed NVM/PNVM and capability flags derived from this table.

## Dependencies and Integration Points
It depends on `iwl-config.h` and firmware declaration macros. It is built for MVM RF configs and also declares firmware images used by newer MAC families.

## Risks and Edge Cases
Some prefixes use PNVM while BZ/SC entries are declared as plain module firmware. API 100 must align with matching MAC base min/max. UHB support requires correct regulatory/NVM handling.

## Test Signals
Verify firmware and PNVM alias installation, probe AX210/AX211/AX411 and BZ/SC GF IDs, check 6 GHz capability exposure, HE RBD sizing, extended NVM parsing, and product-name mapping.
