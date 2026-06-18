# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/rf-pe.c

## Purpose
`rf-pe.c` currently provides product name strings for PE-related Intel/Killer Wi-Fi 8 and Wi-Fi 7 devices. It explicitly notes that `iwl_rf_wh` and `iwl_rf_wh_160mhz` are currently aliases/defines for FM RF configs elsewhere rather than local RF config objects.

## Important APIs, Types, and Data
- Product names: Killer BN1850w2, Killer BN1850i, Intel BN201, BN203, and BE223.
- No local `struct iwl_rf_cfg` definitions are present in this file.

## Control Flow and Integration
PCI ID tables can reference these product-name symbols and RF config aliases defined in headers or other translation units. The file contributes names to the build but does not alter firmware selection or capabilities directly.

## State and Persistence Behavior
Only immutable string constants are defined. No runtime state is created or mutated.

## Dependencies and Integration Points
It depends on `iwl-config.h` for shared declarations. The Makefile includes this RF file for `CONFIG_IWLMLD`.

## Risks and Edge Cases
Because RF configs are not locally defined, maintainers must check header-level aliases when changing PE/WH/FM relationships. Product-name-only files can still break builds if declarations in `iwl-config.h` diverge.

## Test Signals
Build MLD configs, run modpost for exported/declared name symbols, and verify PCI ID mappings display the expected product names while using the intended aliased RF config.
