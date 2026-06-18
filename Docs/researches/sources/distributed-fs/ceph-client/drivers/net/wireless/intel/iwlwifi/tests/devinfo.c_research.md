# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/tests/devinfo.c

## Purpose
This KUnit file validates iwlwifi device-info and PCI-ID tables. It checks lookup ordering, duplicate configs/names, subdevice matching rules, Killer branding constraints, PCI match-table behavior, and firmware API min/max consistency.

## Important APIs, Types, and Functions
- `iwl_pci_print_dev_info()` formats a device-info row for debug failures.
- `devinfo_table_order()` verifies every table row resolves to itself through `iwl_pci_find_dev_info()`.
- `devinfo_discrete_match()` checks discrete/integrated companion rows share config but have distinct names.
- `devinfo_names()`, `devinfo_no_cfg_dups()`, `devinfo_no_name_dups()`, and `devinfo_no_mac_cfg_dups()` enforce table hygiene.
- `devinfo_check_subdev_match()` validates subdevice/RF-ID/BW-limit matching rules.
- `devinfo_check_killer_subdev()` prevents Killer entries from using wildcard subdevices.
- `devinfo_pci_ids()` validates Linux PCI core matching for every `iwl_hw_card_ids` row.
- `devinfo_api_range()` checks `ucode_api_min` and `ucode_api_max` are set together.
- `devinfo_pci_ids_config()` checks old explicit PCI IDs are represented in the device-info table, with skips for wildcard and some newer Bz flows.

## Control Flow
The suite iterates static iwlwifi tables and uses KUnit assertions/expectations. Failures print enough context to identify unusable or shadowed entries. The test suite is registered as `iwlwifi-devinfo`.

## State and Persistence Behavior
Tests allocate a temporary `struct pci_dev` via KUnit memory and otherwise read static tables. They do not persist state or mutate driver configuration.

## Dependencies and Integration Points
It imports the `EXPORTED_FOR_KUNIT_TESTING` namespace and depends on `iwl-drv.h`, `iwl-config.h`, PCI ID helpers, `iwl_dev_info_table`, `iwl_hw_card_ids`, and optional `CONFIG_IWLMVM`/`CONFIG_IWLMLD` references for Bz config skipping.

## Risks and Edge Cases
The table-order test detects shadowing where a broad row hides a later specific row. Duplicate checks compare full struct bytes and may flag intentional duplicates unless pointers are shared. `devinfo_pci_ids_config()` intentionally skips newer/wildcard patterns; changes to PCI matching strategy may require adjusting that policy.

## Test Signals
Passing KUnit output indicates table lookup order, ID matching, name/config uniqueness, subdevice mask conventions, and API range metadata are internally consistent.
