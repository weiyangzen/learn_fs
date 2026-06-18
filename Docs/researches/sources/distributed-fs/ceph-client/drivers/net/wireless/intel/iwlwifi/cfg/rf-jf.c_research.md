# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/rf-jf.c

## Purpose
`rf-jf.c` defines JF RF configuration for Wireless-AC 9260/9461/9462/9560-class devices, including firmware API 77, DCCM memory ranges for Pu/Th firmware, thermal throttling, extended NVM, non-HE RBD count, bandwidth variants, and product names.

## Important APIs, Types, and Data
- Firmware API range: JF API 77 only.
- Firmware prefixes for QU/QUZ/SO JF combinations.
- DCCM/DCCM2 offsets and lengths for 9000-era firmware.
- `iwl_jf_tt_params`: CT kill, dynamic SMPS, TX protection, and TX backoff thresholds.
- `IWL_DEVICE_JF`: DCCM/thermal fields, RF-state LED, non-shared antenna B, non-HE RBD count, VHT MU-MIMO, STBC/LDPC, HT40, NVM 0x0a1d, extended NVM, API range.
- RF configs: `iwl_rf_jf`, `iwl_rf_jf_80mhz`.
- Product and Killer adapter names.

## Control Flow and Integration
9000/22000-era MAC configs pair with JF RF configs. MVM uses DCCM fields for firmware dump support, thermal params for runtime throttling, and RF fields for capability registration and firmware loading.

## State and Persistence Behavior
The file defines immutable RF/thermal config. Runtime thermal state, firmware memory dump state, and capabilities derive from these tables.

## Dependencies and Integration Points
It depends on `iwl-config.h`. It is included under `CONFIG_IWLMVM` as an RF config and pairs especially with 9000-family MAC configs.

## Risks and Edge Cases
Comments note DCCM values are ignored when not paired with Pu/Th MAC firmware due to offload; wrong MAC/RF pairing can produce confusing unused fields. Bandwidth-capped variants must be correctly selected.

## Test Signals
Probe JF devices, confirm API 77 firmware aliases, validate 80/160 MHz capability selection, thermal throttling, DCCM dump ranges, extended NVM parsing, non-HE RBD count, and product-name mappings.
