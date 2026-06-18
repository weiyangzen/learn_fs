# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-config.h

## Purpose
Declares device-family, MAC, RF, firmware API, antenna, NVM, thermal, EEPROM, and device-ID configuration contracts used to bind PCI hardware to firmware and opmode behavior.

## Important APIs, Types, and Functions
Important enums include `iwl_device_family`, `iwl_led_mode`, `iwl_nvm_type`, and `iwl_mac_cfg_ltr_delay`. Core structs are `iwl_family_base_params`, `iwl_ht_params`, `iwl_tt_params`, `iwl_eeprom_params`, `iwl_pwr_tx_backoff`, `iwl_mac_cfg`, `iwl_rf_cfg`, and `iwl_dev_info`. Helpers/macros include antenna masks, `num_of_ant()`, firmware filename macros, core/API version conversions, MAC/RF type constants, subdevice extractors, and `iwl_pci_find_dev_info()`.

## Control Flow
The header itself is declarative. Probe code selects a `iwl_dev_info` and config pointers, firmware loading combines MAC/RF API ranges, and opmodes use the flags to size queues, choose NVM parsing, enable capabilities, and apply workarounds.

## State and Persistence Behavior
Config structures are static immutable driver data. They determine runtime allocations, feature flags, firmware filename selection, thermal behavior, and hardware workarounds for each device lifetime.

## Dependencies and Integration Points
Depends on Linux networking, PCI modalias types, `iwl-csr.h`, and `iwl-drv.h`. It is central to PCI ID matching, firmware loading, MVM/DVM/MLD selection, NVM parsing, transport setup, and feature gating.

## Risks
Incorrect API ranges or firmware prefixes cause firmware load failures. Wrong antenna, NVM, queue, or memory limits can break radio capability reporting or DMA sizing. Device match masks must be precise enough to avoid binding a device to an incompatible RF config.

## Test Signals
PCI ID matching, generated firmware filenames, core/API fallback, old and new device families, CDB/bandwidth/subdevice matching, NVM parsing modes, antenna counts, Wi-Fi 7 MLD selection, and KUnit coverage of device info tables are useful.
